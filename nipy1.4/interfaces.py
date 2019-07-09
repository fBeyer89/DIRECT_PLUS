import os
import sys
import math

from nipype.interfaces.base import isdefined
from nipype.interfaces.base import BaseInterface, InputMultiPath,\
    OutputMultiPath, BaseInterfaceInputSpec, traits, File, TraitedSpec,\
    CommandLineInputSpec, CommandLine, Directory
from traits.trait_errors import TraitError
import nipype.interfaces.dcm2nii as d2n
from nipype.utils.filemanip import split_filename
from util import *



class DicomInfoInputSpec(BaseInterfaceInputSpec):
    files = InputMultiPath(
            traits.Either(traits.List(File(exists=True)),File(exists=True)),
            mandatory=True,
            desc="a list of dicom files from which to extract data",
            copyfile=False)

class DicomInfoOutputSpec(TraitedSpec):
    info = traits.List(traits.Dict(),
            desc="an ordered list of dicts, all in the same directory.")

class DicomInfo(BaseInterface):
    input_spec = DicomInfoInputSpec
    output_spec = DicomInfoOutputSpec

    def __init__(self, *args, **kwargs):
        super(DicomInfo, self).__init__(*args, **kwargs)
        self.info = []

    def _run_interface(self, runtime):
        import pydicom
        files = self.inputs.files
        by_series = {}
        self.info = []
        for f in files:
            d = pydicom.dcmread(f)
            try: 
                s_num = d.SeriesNumber
                s_num = int(s_num)
            except Exception, e:
                raise e
            
            if not s_num in by_series:
                by_series[s_num] = {
                    "series_num": s_num,
                    "series_desc": getattr(d,"SeriesDescription",None),
                    "protocol_name": getattr(d,"ProtocolName",None),
                }
                if [0x19,0x1018] in d and \
                        "description" in dir(d[0x19,0x1018]) and \
                        "RealDwellTime" in d[0x19,0x1018].description():
                    try:
                        by_series[s_num]["RealDwellTime"] = float(d[0x19,0x1018].value)
                    except Exception, e:
                        pass # don't die
                it = getattr(d,"ImageType",None)
                if it:
                    if not isinstance(it,str):
                        it = list(it)
                    by_series[s_num]["image_type"] = it
                ipped = getattr(d,"InPlanePhaseEncodingDirection", None)
                if ipped:
                    by_series[s_num]["ipp_encoding_direction"] = ipped
                
                # ep repetition time
                rep = d.get((0x0018,0x0080), None)
                if rep:
                    try:
                        rep = float(rep.value)/1000 #to get it in seconds
                    except Exception, e:
                        pass
                    else:
                        by_series[s_num]["TR"] = rep 
                        
                # ep echo spacing ingredients
                bpppe = d.get((0x0019,0x1028), None)
                if bpppe:
                    try:
                        bpppe = float(bpppe.value)
                    except Exception, e:
                        pass
                    else:
                        by_series[s_num]["bw_per_pix_phase_encode"] = bpppe 
                        
                acq_mat = getattr(d, "AcquisitionMatrix", None)
                if acq_mat and len(acq_mat) == 4:
                    # acq mat text gets turned into this struct.
                    # n will be in 0/1 (other index will == 0), m will be in 2/3
                    by_series[s_num]["acq_matrix_n"] = acq_mat[0] or acq_mat[1]
                    by_series[s_num]["acq_matrix_m"] = acq_mat[2] or acq_mat[3]
                # try to get orientation from header
                if getattr(d,"SeriesDescription")=='cmrr_mbep2d_DTI_32Ch_ColFA':
                    print "no header orientation given"
                else:
                    orient = orientation_from_dcm_header(d)
                    if orient:
                        by_series[s_num]["orientation"] = orient
                # try to get siemens shadow header
                #try:
                #    ss = read_siemens_shadow(f)[0]
                #except Exception, e:
                #    pass
                #else:
                #    siemens_keys = ["in_plane_rotation", "polarity_swap"]
                #    by_series[s_num].update(dict([(k,v) for k,v in ss.iteritems() if k in siemens_keys]))
            bs = by_series[s_num]
            # collect all of the unique EchoTimes per series
            try:
                et = getattr(d,"EchoTime",None)
                if et:
                    et = float(et)
                    if not "echo_times" in bs:
                        bs["echo_times"] = []
                    if not et in bs["echo_times"]:
                        bs["echo_times"].append(et)
            except Exception, e:
                pass # don't die.
        for s_num, s_info in by_series.iteritems():
            # find delta_te, collapse to echo time if needed
            if "echo_times" in s_info:
                etc = len(s_info["echo_times"])
                if etc == 0:
                    del s_info["echo_times"]
                elif etc == 1:
                    s_info["echo_time"] = s_info["echo_times"][0]
                    del s_info["echo_times"]
                elif etc == 2:
                    s_info["delta_te"] = abs(s_info["echo_times"][0] - s_info["echo_times"][1])
        for k in sorted(by_series.keys()):
            self.info.append(by_series[k])
        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs["info"] = self.info
        return outputs

class NiiWranglerInputSpec(BaseInterfaceInputSpec):
    nii_files = InputMultiPath(
            traits.Either(traits.List(File(exists=True)),File(exists=True)),
            mandatory=True,
            desc="a list of nifti files to be categorized, matched up, etc.",
            copyfile=False)
    series_map = traits.Dict(
            key_trait=traits.Str(),
            value_trait=traits.List(),
            value = {},
            mandatory=False,
            usedefault=True,
            desc="keys are any member of SCAN_TYPES, values are lists of series\
                  descriptions as recorded in DICOM headers.")
    dicom_info = traits.List(
            mandatory=True,
            desc="one dict for each series in the session, in the order they were\
                  run. each dict should contain at least the series_num (int) and\
                  the series_desc (str).")
    ep_TR=  traits.Either(traits.Enum("NONE"), traits.Float(),
            desc="rsfmri TR or 'NONE' if not used.")   
    ep_rsfmri_echo_spacings = traits.Either(traits.Enum("NONE"), traits.Float(),
            desc="""
            The effective echo spacing of your BOLD images. Already accounts
            for whether or not iPAT (acceleration in the phase direction) was
            used. If you're using acceleration, then the EES is not going to
            match the 'Echo Spacing' that Siemen's reports in the console.
            Setting this value will prevent any attempt to derive it.""")   
    ep_dwi_echo_spacings = traits.Either(traits.Enum("NONE"), traits.Float(),
            desc="""
            The effective echo spacing of your BOLD images. Already accounts
            for whether or not iPAT (acceleration in the phase direction) was
            used. If you're using acceleration, then the EES is not going to
            match the 'Echo Spacing' that Siemen's reports in the console.
            Setting this value will prevent any attempt to derive it.""")
    ep_unwarp_dir = traits.Enum("x", "x-", "-x", "y", "y-", "-y", "z", "z-", "-z",
            desc="Setting this value will prevent any attempt to derive it.")
            

class NiiWranglerOutputSpec(TraitedSpec):
    dicom_info = traits.List(
            mandatory=True,
            desc="one dict for each series in the session, in the order they were\
                  run. each dict should contain at least the series_num (int) and\
                  the series_desc (str). NiiWrangler writes nifti location here.")
    t1 = OutputMultiPath(
            traits.Either(traits.List(File(exists=True)),File(exists=True)),
            mandatory=True,
            desc="anatomical uni nifti (list in chronological order  if repeated)")
    rsfmri = OutputMultiPath(
            traits.Either(traits.List(File(exists=True)),File(exists=True)),
            mandatory=True,
            desc="rsfmri nifti (list in chronological order  if repeated)")
    rs_mag = OutputMultiPath(
            traits.Either(traits.List(File(exists=True)),File(exists=True)),
            mandatory=True,
            desc="rs ap nifti (list in chronological order  if repeated)")
    rs_ph = OutputMultiPath(
            traits.Either(traits.List(File(exists=True)),File(exists=True)),
            mandatory=True,
            desc="rs pa (list in chronological order  if repeated)")
    dwi   = OutputMultiPath(
            traits.Either(traits.List(File(exists=True)),File(exists=True)),
            mandatory=True,
            desc="dwi nifti (list in chronological order  if repeated).")
    dwi_b0   = OutputMultiPath(
            traits.Either(traits.List(File(exists=True)),File(exists=True)),
            mandatory=True,
            desc="dwi nifti (list in chronological order  if repeated).")
    dwi_mag=OutputMultiPath(
            traits.Either(traits.List(File(exists=True)),File(exists=True)),
            mandatory=True,
            desc="dwi ap nifti for topup (list in chronological order  if repeated).")
    dwi_ph= OutputMultiPath(
            traits.Either(traits.List(File(exists=True)),File(exists=True)),
            mandatory=True,
            desc="dwi pa nifti for topup (list in chronological order  if repeated).")
    flair=  OutputMultiPath(
            traits.Either(traits.List(File(exists=True)),File(exists=True)),
            mandatory=True,
            desc="flair nifti (list in chronological order  if repeated).")
    ep_TR=  traits.Either(traits.Enum("NONE"), traits.Float(),
            value=["NONE"], mandatory=False, usedefault=True,
            desc="rsfmri TR or 'NONE' if not used.")
    ep_rsfmri_echo_spacings = traits.Either(traits.Enum("NONE"), traits.Float(),
            value=["NONE"], mandatory=False, usedefault=True,
            desc="""
            The effective echo spacing of your rsfmri images. Already accounts
            for whether or not iPAT (acceleration in the phase direction) was
            used. If you're using acceleration, then the EES is not going to
            match the 'Echo Spacing' that Siemen's reports in the console.
            This value will be derived, if not overridden by the input of the
            same name. Please inspect the value after your initial run of the
            pipeline to ensure that it's sane.
            """)
    ep_rsfmri_dwelltime = traits.Either(traits.Enum("NONE"), traits.Float(),
            value=["NONE"], mandatory=False, usedefault=True,
            desc="""
            The dwelltime of your rsfmri images. Calculated as 1/bandwidth in
            phase encode direction. Already accounts
            for whether or not iPAT (acceleration in the phase direction) was
            used. 
            """)
    ep_rsfmri_fieldmap_te= traits.Either(traits.Enum("NONE"), traits.Float(),
        value=["NONE"], mandatory=False, usedefault=True,
        desc="""
        TE difference used for fieldmap acquisition. 
        """)
    ep_dwi_echo_spacings = traits.Either(traits.Enum("NONE"), traits.Float(),
            value=["NONE"], mandatory=False, usedefault=True,
            desc="""
            The effective echo spacing of your BOLD images. Already accounts
            for whether or not iPAT (acceleration in the phase direction) was
            used. If you're using acceleration, then the EES is not going to
            match the 'Echo Spacing' that Siemen's reports in the console.
            This value will be derived, if not overridden by the input of the
            same name. Please inspect the value after your initial run of the
            pipeline to ensure that it's sane.
            Length must match number of bold images.""")
    ep_dwi_dwelltime = traits.Either(traits.Enum("NONE"), traits.Float(),
        value=["NONE"], mandatory=False, usedefault=True,
        desc="""
        The dwelltime of your dwi images. Calculated as 1/bandwidth in
        phase encode direction. Already accounts
        for whether or not iPAT (acceleration in the phase direction) was
        used. 
        """)
    ep_dwi_fieldmap_te= traits.Either(traits.Enum("NONE"), traits.Float(),
        value=["NONE"], mandatory=False, usedefault=True,
        desc="""
        TE difference used for fieldmap acquisition. 
        """)
    ep_unwarp_dirs = traits.List(traits.Enum("x", "x-", "-x", "y", "y-", "-y", "z", "z-", "-z",),
            mandatory=True,
            desc="Length must match number of bold images.")

class NiiWrangler(BaseInterface):
    input_spec = NiiWranglerInputSpec
    output_spec = NiiWranglerOutputSpec

    def __init__(self, *args, **kwargs):
        super(NiiWrangler, self).__init__(*args, **kwargs)
        self.t1_files = []
        self.rsfmri_files = []
        self.rs_mag_files = []
        self.rs_ph_files = []
        self.dwi_files = []
        self.dwi_b0_files=[]
        self.dwi_mag_files = []
        self.dwi_ph_files = []
        self.bval = []
        self.bvec = []
        self.ep_TR= None
        self.ep_dwi_echo_spacings = None
        self.ep_dwi_dwelltime=None
        self.ep_dwi_fieldmap_te=None
        self.ep_rsfmri_echo_spacings = None
        self.ep_rsfmri_dwelltime=None
        self.ep_rsfmri_fieldmap_te=None
        self.ep_unwarp_dirs = None        
        self.flair_files = []
        self.nii_info=[]

    def _run_interface(self, runtime):
        import re
        import operator
        
        print "starting NII wrangler"
        nii_files = self.inputs.nii_files
        smap = self.inputs.series_map
        dinfo = self.inputs.dicom_info
        #block_averaging = self.inputs.block_struct_averaging
        s_num_reg = re.compile(".*s(\d+)")
        nii_by_series = {}
        fails = []
        extras = []
       
        for fn in nii_files:
            try:
                # we only want the first nii for each series
                # TODO: find out what those others (A/B) are all about. fix this as needed.
                sn = int(s_num_reg.match(fn).groups()[0])
                if sn in nii_by_series:
                    extras.append(fn)
                    continue
                nii_by_series[sn] = fn
            except Exception, e:
                fails.append(fn)
        if fails:
            raise ValueError("Could not derive series number from file names: %s." % str(fails))
        if extras:
            print >> sys.stderr, "\nWARNING: Ignoring extra niftis: %s\n" % str(extras)
        # add nifti names to the dicts
        m_count = 0
        for sn, fn in nii_by_series.iteritems():
            m = filter(lambda x: x.get("series_num",-1) == sn, dinfo)
            if not m:
                continue
            m_count += 1
            m[0]["nifti_file"] = fn
        
        if not m_count == len(dinfo):
            print "number of niftis and dicom series doesn't correspond due to AAHScout"
            #raise ValueError("incorrect number of nifti->series matches (%d/%d)" % (m_count, len(dinfo)))
            
        self.nii_info=dinfo    
        # time for some data wrangling
        nf = "nifti_file"
        sd = "series_desc"
        it = "image_type"
        t1 = [d for d in filter(lambda x: sd in x and x[sd] in smap.get("t1",[]), dinfo) if nf in d]
        if len(t1)==0:
            print "no T1 acquired"
        elif len(t1)==1:
            self.t1_files = t1[0][nf]
        else:
            self.t1_files = [d[nf] for d in t1]


        #get rsfmri, if no "resting state return default file" and ap/pa scans
        bs = [d for d in filter(lambda x: sd in x and x[sd] in smap.get("rsfmri",[]), dinfo) if nf in d]
        if len(bs)==0:
            print "no rs acquired"
        elif len(bs)==1:
            self.rsfmri_files = bs[0][nf]
        else:
            self.rsfmri_files = [d[nf] for d in bs]       

        #get 64dir dwi (and don't raise an error if there is none)
        dwi = [d for d in filter(lambda x: sd in x and x[sd] in smap.get("dwi",[]), dinfo) if nf in d]        
        if len(dwi)==0:
            print "no DTI acquired"
            self.dwi_files=['nothing to proceed']  
        elif len(dwi)==1:
            self.dwi_files = dwi[0][nf]
        else:
            self.dwi_files = [d[nf] for d in dwi]
       

        #get 9b0 dwi (and don't raise an error if there is none)
        dwi_b0 = [d for d in filter(lambda x: sd in x and x[sd] in smap.get("dwi_b0",[]), dinfo) if nf in d]        
        if len(dwi_b0)==0:
            print "no b0 DTI acquired"
            self.dwi_b0_files=['nothing to proceed']  
        elif len(dwi_b0)==1:
            self.dwi_b0_files = dwi_b0[0][nf]
        else:
            self.dwi_b0_files = [d[nf] for d in dwi_b0]
        
 
        flair = [d for d in filter(lambda x: sd in x and x[sd] in smap.get("flair",[]), dinfo) if nf in d]
        if len(flair)==0:
            print "no FLAIR acquired"
            self.flair_files=['nothing to proceed']
        elif len(flair)==1:
            self.flair_files = flair[0][nf]
        else:
            self.flair_files = [d[nf] for d in flair]
         
            
        #get fieldmaps -> needs some more twirking.
        dwi_mag = filter(lambda x: sd in x and
                x[sd] in smap.get("fieldmap_dwi",[]) and
                it in x and
                isinstance(x[it], list) and
                len(x[it]) > 2 and
                x[it][2].strip().lower() == "m", dinfo) # we want the 3rd field of image type to be 'm'
        dwi_ph = filter(lambda x: sd in x and
                x[sd] in smap.get("fieldmap_dwi",[]) and
                it in x and
                isinstance(x[it], list) and
                len(x[it]) > 2 and
                x[it][2].strip().lower() == "p", dinfo) # we want the 3rd field of image type to be 'p'
        self.dwi_mag_files = dwi_mag[0][nf] #[d[nf] for d in dwi_mag if nf in d]
        self.ep_dwi_fieldmap_te = dwi_mag[0]["delta_te"]
        self.dwi_ph_files= dwi_ph[0][nf] #[d[nf] for d in dwi_ph if nf in d]
           
        rs_mag = filter(lambda x: sd in x and
                x[sd] in smap.get("fieldmap_rs",[]) and
                it in x and
                isinstance(x[it], list) and
                len(x[it]) > 2 and
                x[it][2].strip().lower() == "m", dinfo) # we want the 3rd field of image type to be 'm'
        rs_ph = filter(lambda x: sd in x and
                x[sd] in smap.get("fieldmap_rs",[]) and
                it in x and
                isinstance(x[it], list) and
                len(x[it]) > 2 and
                x[it][2].strip().lower() == "p", dinfo) # we want the 3rd field of image type to be 'p'
        self.rs_mag_files = rs_mag[0][nf]#[d[nf] for d in rs_mag if nf in d]
        self.ep_rsfmri_fieldmap_te = rs_mag[0]["delta_te"]
        self.rs_ph_files= rs_ph[0][nf]#[d[nf] for d in rs_ph if nf in d]
        
        #get info about phase difference:
        
        
        #calculate echo spacing for rsfmri/dwi   
        #if more than one resting state scan was acquired:
        ep_rsfmri_echo_fail = False
        if isdefined(self.inputs.ep_rsfmri_echo_spacings):
            self.ep_rsfmri_echo_spacings = self.inputs.ep_rsfmri_echo_spacings
        elif bs and "bw_per_pix_phase_encode" in bs[0] and "acq_matrix_n" in bs[0]:
            if not "bw_per_pix_phase_encode" in bs[0] and "acq_matrix_n" in bs[0]:
                ep_rsfmri_echo_fail = True
            else:
                self.ep_rsfmri_echo_spacings = 1/(bs[0]["bw_per_pix_phase_encode"] * bs[0]["acq_matrix_n"])
                self.ep_rsfmri_dwelltime = 1/(bs[0]["bw_per_pix_phase_encode"])
        else:
            self.ep_rsfmri_echo_spacings = "NONE" 
            self.ep_rsfmri_dwelltime = "NONE"
        
        ep_dwi_echo_fail = False
        if isdefined(self.inputs.ep_dwi_echo_spacings):
            self.ep_dwi_echo_spacings = self.inputs.ep_dwi_echo_spacings
        elif dwi and "bw_per_pix_phase_encode" in dwi[0] and "acq_matrix_n" in dwi[0]:
            if not "bw_per_pix_phase_encode" in dwi[0] and "acq_matrix_n" in dwi[0]:
                ep_rsfmri_echo_fail = True
            else:
                self.ep_dwi_echo_spacings = 1/(dwi[0]["bw_per_pix_phase_encode"] * dwi[0]["acq_matrix_n"])
                self.ep_dwi_dwelltime = 1/(dwi[0]["bw_per_pix_phase_encode"])
        else:
            self.ep_rsfmri_echo_spacings = "NONE" 
            self.ep_rsfmri_dwelltime = "NONE"
            
        #get TR for resting state scan    
        ep_TR_fail=False
        if isdefined(self.inputs.ep_TR):
            self.ep_TR=self.inputs.ep_TR
        elif bs and "TR" in bs[0]:
            if not "TR" in bs[0]:
                ep_TR_fail = True
            else: 
                print "setting TR value"
                self.ep_TR=bs[0]["TR"]
        else:
             self.ep_TR= "NONE"
        
        if isdefined(self.inputs.ep_unwarp_dir):
            self.ep_unwarp_dirs = [self.inputs.ep_unwarp_dir for n in self.rsfmri_files]
            # if you have any polarity swapped series, apply that now
            pswaps = smap.get("polarity_swapped", [])
            if pswaps:
                for b_idx, uw_dir in enumerate(self.ep_unwarp_dirs):
                    if bs[b_idx].get("series_desc",None) in pswaps:
                        raw_dir = uw_dir.replace("-","")
                        self.ep_unwarp_dirs[b_idx] = "-"+raw_dir if not "-" in uw_dir else raw_dir
        else:
            # fail. we can do better!
            raise ValueError("We can't derive ep_unwarp_dir yet. Please set it in the nii wrangler config section.")

            
        # don't continue if there was screwiness around calculating ep echo spacing
        if ep_rsfmri_echo_fail:
            raise ValueError("Unabel to calculate fmri ep echo spacing. Try specifying manually in nii wrangler config section.")
        if ep_dwi_echo_fail:
            raise ValueError("Unabel to calculate dwi ep echo spacing. Try specifying manually in nii wrangler config section.")
        if ep_TR_fail:
            raise ValueError("Unabel to derive TR. Try specifying manually in nii wrangler config section.")
        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs["t1"] = self.t1_files
        outputs["rsfmri"] = self.rsfmri_files
        outputs["rs_mag"] = self.rs_mag_files
        outputs["rs_ph"] = self.rs_ph_files
        outputs["dwi"] = self.dwi_files
        outputs["dwi_b0"] = self.dwi_b0_files
        outputs["dwi_mag"] = self.dwi_mag_files
        outputs["dwi_ph"] = self.dwi_ph_files
        outputs["flair"] = self.flair_files
        outputs["ep_TR"] = self.ep_TR
        outputs["ep_dwi_echo_spacings"] = self.ep_dwi_echo_spacings
        outputs["ep_dwi_dwelltime"] = self.ep_dwi_dwelltime
        outputs["ep_rsfmri_echo_spacings"] = self.ep_rsfmri_echo_spacings
        outputs["ep_rsfmri_dwelltime"] = self.ep_rsfmri_dwelltime
        outputs["ep_unwarp_dirs"] = self.ep_unwarp_dirs
        outputs["dicom_info"] = self.nii_info
        outputs["ep_dwi_fieldmap_te"]=self.ep_dwi_fieldmap_te
        outputs["ep_rsfmri_fieldmap_te"]=self.ep_rsfmri_fieldmap_te
        return outputs
        
