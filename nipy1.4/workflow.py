import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.utility as util     # utility
import nipype.pipeline.engine as pe   
from nipype import Function
from nipype.interfaces.dcm2nii import Dcm2niix
from interfaces import *
from config import *
from util import *
from bids_conversion import *

class HCPrepWorkflow(pe.Workflow):
    def __init__(self, config=None, base_dir=None, *args, **kwargs):
        super(HCPrepWorkflow, self).__init__(*args, **kwargs)
        self.hc_config = config
        self.base_dir = base_dir

    @property
    def hc_config(self):
        return self._hc_config
    @hc_config.setter
    def hc_config(self, value):
        self._hc_config = value
        if self._hc_config:
            self.update_nodes_from_config()

    def get_conf(self, section, option):
        if not self.hc_config:
            return None
        return self.hc_config.get(section,{}).get(option, None)

    def update_nodes_from_config(self):
        # subjects node
        subs = self.get_conf("general","subjects")
        if subs:
            self.subjects_node.iterables = ("subject", subs)
        # dcm grabber
        sub_dir = self.get_conf("general","subject_dir")
        dcm_temp = self.get_conf("general","dicom_template")    
        fs_dir = self.get_conf("general","fs_dir") 
        out_dir = self.get_conf("general","out_dir")
        standard = self.get_conf("templates","t1_template_2mm")  
        standard_downsampled = self.get_conf("templates","t1_template_3mm")  
        outputdir=self.get_conf("general", "outputdir")
        bids_outputdir=self.get_conf("general", "bids_outputdir")
        vol_to_remove=self.get_conf("rspreproc","vol_to_remove")
        epi_resolution=self.get_conf("rspreproc","epi_resolution")
        highpass_freq=self.get_conf("rspreproc","highpass_freq")
        ep_unwarp_dir=self.get_conf("rspreproc","ep_unwarp_dir")
        fwhm=self.get_conf("rspreproc","fwhm")
        #working_dir = self.get_conf("general","working_dir")     
        if sub_dir:
            self.dicom_grabber.inputs.base_directory = sub_dir
        if dcm_temp:
            self.dicom_grabber.inputs.field_template = {"dicom": dcm_temp}  
        if bids_outputdir:
            self.bids.inputs.bids_output=bids_outputdir
        if fs_dir:
            self.structural_wf.inputs.inputnode.freesurfer_dir=fs_dir
            self.resting.inputs.inputnode.freesurfer_dir=fs_dir
            self.dwi_wf.inputs.inputnode.freesurfer_dir=fs_dir
        if out_dir:
            self.structural_wf.inputs.inputnode.out_dir=out_dir
            self.resting.inputs.inputnode.out_dir=out_dir
        if standard:
            self.structural_wf.inputs.inputnode.standard_brain=standard  
        if vol_to_remove:
            self.resting.inputs.inputnode.vol_to_remove=vol_to_remove
        if epi_resolution:
            self.resting.inputs.inputnode.epi_resolution=epi_resolution 
            self.resting.inputs.inputnode.fwhm=fwhm 
            self.resting.inputs.inputnode.highpass_freq=highpass_freq
            self.resting.inputs.inputnode.standard_downsampled=standard_downsampled
            self.resting.inputs.inputnode.standard_brain=standard
            self.resting.inputs.inputnode.pe_dir=ep_unwarp_dir
        if outputdir:
            self.data_sink.inputs.base_directory=outputdir
            self.data_sink.inputs.substitutions=[('_subject_', ''),
                                                 ('_filternoise0', 'filter_compcor_gsr'),
                                                 ('_filternoise1', 'filter_compcor'),
                                                 ('_highpass_filter0', 'highpass_compcor_gsr'),
                                                 ('_highpass_filter1', 'highpass_compcor'),
                                                 ('dtifit__', 'dtifit_'),
                                                 ('rest_mean2anat_lowres_brain_mask_maths_maths', 'combined_brain_mask'),
                                                 ('_denoised_roi_brain', '_firstb0'),
                                                 ('_denoised_roi_brain_mask', '_b0mask')
                                                 ]


    
                            
        # nifti wrangler
        series_map = self.hc_config.get("series", {})
        if series_map:
            self.nii_wrangler.inputs.series_map = series_map
        # set template and config values (names are also input names on some nodes)
        temps = self.hc_config.get("templates", {})
        c_files = self.hc_config.get("config_files", {})
        # any other per-step hcp config - a good place to overide un-derived values
        apply_dict_to_obj(self.hc_config.get("nifti_wrangler", {}), self.nii_wrangler.inputs)

    def run(self, *args, **kwargs):
        self.connect_nodes()
        super(HCPrepWorkflow, self).run(*args, **kwargs)

    def write_graph(self, *args, **kwargs):
        self.connect_nodes()
        super(HCPrepWorkflow, self).write_graph(*args, **kwargs)
        
    def clear_nodes(self):
        all_nodes = self._get_all_nodes()
        if all_nodes is not None:
            self.remove_nodes(all_nodes)

    def connect_nodes(self):
        # Some connections that don't change
        self.clear_nodes()
        self.connect([
            # prep steps
            (self.subjects_node, self.dicom_grabber, [("subject", "subject")]),
            (self.dicom_grabber, self.dicom_convert, [("dicom", "source_names")]),
            (self.dicom_grabber, self.dicom_info, [("dicom", "files")]),
            (self.dicom_convert, self.nii_wrangler, [("converted_files", "nii_files")]),                  
            (self.dicom_info, self.nii_wrangler, [("info", "dicom_info")]),
            (self.nii_wrangler, self.bids, [('dicom_info', 'dicom_info')]),
            (self.dicom_convert, self.bids, [('bids', 'bids_info')]),  
            (self.subjects_node,self.bids, [('subject', 'subj')]),     
            (self.nii_wrangler, self.data_sink, [("t1", "nifti.@t1")]), 
            (self.nii_wrangler, self.data_sink, [("rsfmri", "nifti.@rsfmri")]), 
            (self.nii_wrangler, self.data_sink, [("rs_mag", "nifti.@rs_mag")]),       
            (self.nii_wrangler, self.data_sink, [("rs_ph", "nifti.@rs_ph")]),    
            (self.nii_wrangler, self.data_sink, [("dwi", "nifti.@dwi")]), 
            (self.nii_wrangler, self.data_sink, [("dwi_b0", "nifti.@dwi_b0")]), 
            (self.nii_wrangler, self.data_sink, [("dwi_mag", "nifti.@dwi_mag")]),  
            (self.nii_wrangler, self.data_sink, [("dwi_ph", "nifti.@dwi_ph")]), 
            (self.dicom_convert, self.data_sink, [("bvals", "nifti.@bval")]),
            (self.dicom_convert, self.data_sink, [("bvecs", "nifti.@bvecs")]),
            (self.dicom_convert, self.data_sink, [("bids", "nifti.@bids")]),    
            (self.nii_wrangler, self.data_sink, [("flair", "nifti.@flair")]),
            
            #structural workflow
            (self.nii_wrangler, self.structural_wf, [("t1", "inputnode.anat")]),           
            (self.subjects_node, self.structural_wf, [("subject", "inputnode.subject")]),
            (self.structural_wf, self.data_sink, [('outputnode.brain', 'structural.@brain')]),
            (self.structural_wf, self.data_sink, [('outputnode.anat_head', 'structural.@anat_head')]),
            (self.structural_wf, self.data_sink, [('outputnode.brainmask', 'structural.@brainmask')]),
            (self.structural_wf, self.data_sink, [('outputnode.anat2std', 'structural.@anat2std')]),
            (self.structural_wf, self.data_sink, [('outputnode.anat2std_transforms', 'structural.@anat2std_transforms')]),
            (self.structural_wf, self.data_sink, [('outputnode.std2anat_transforms', 'structural.@std2anat_transforms')]),
            
            #diffusion workflow
#            (self.subjects_node,self.dwi_wf, [("subject", "inputnode.subject_id")]),
            (self.structural_wf, self.dwi_wf, [("outputnode.subject_id", "inputnode.subject_id")]),
            (self.nii_wrangler, self.dwi_wf, [("dwi", "inputnode.dwi")]),
            (self.nii_wrangler, self.dwi_wf, [("dwi_b0", "inputnode.dwi_b0")]),
            (self.nii_wrangler, self.dwi_wf, [("dwi_mag", "inputnode.dwi_mag")]),
            (self.nii_wrangler, self.dwi_wf, [("dwi_ph", "inputnode.dwi_ph")]),
            (self.nii_wrangler, self.dwi_wf, [("ep_dwi_dwelltime", "inputnode.dwi_dwelltime")]),
            (self.nii_wrangler, self.dwi_wf, [("ep_dwi_fieldmap_te", "inputnode.te_diff")]),
            (self.bids, self.dwi_wf, [("bval_file", "inputnode.bvals")]),
            (self.bids, self.dwi_wf, [("bvec_file", "inputnode.bvecs")]),  
            (self.dwi_wf, self.data_sink, [('outputnode.dwi_denoised', 'diffusion.@dwi_denoised')]),
            (self.dwi_wf, self.data_sink, [('outputnode.fmap', 'diffusion.@fmap')]),
            (self.dwi_wf, self.data_sink, [('outputnode.bo_brainmask', 'diffusion.@bo_brainmask')]),
            (self.dwi_wf, self.data_sink, [('outputnode.bo_brain', 'diffusion.@bo_brain')]),
            (self.dwi_wf, self.data_sink, [('outputnode.rotated_bvecs', 'diffusion.eddy.@rotated_bvecs')]),
    	        (self.dwi_wf, self.data_sink, [('outputnode.eddy_corr', 'diffusion.eddy.@eddy_corr')]),
	        (self.dwi_wf, self.data_sink, [('outputnode.total_movement_rms', 'diffusion.eddy.@total_movement_rms')]),
            (self.dwi_wf, self.data_sink, [('outputnode.cnr_maps', 'diffusion.eddy.@cnr_maps')]),
            (self.dwi_wf, self.data_sink, [('outputnode.residuals', 'diffusion.eddy.@residuals')]),
            (self.dwi_wf, self.data_sink, [('outputnode.shell_params', 'diffusion.eddy.@shell_params')]),
	        (self.dwi_wf, self.data_sink, [('outputnode.outlier_report', 'diffusion.eddy.@outlier_report')]),
            (self.dwi_wf, self.data_sink, [('outputnode.eddy_params', 'diffusion.eddy.@eddy_params')]),
            (self.dwi_wf, self.data_sink, [('outputnode.dti_fa', 'diffusion.dti.@dti_fa')]),
            (self.dwi_wf, self.data_sink, [('outputnode.dti_md', 'diffusion.dti.@dti_md')]),
            (self.dwi_wf, self.data_sink, [('outputnode.dti_l1', 'diffusion.dti.@dti_l1')]),
            (self.dwi_wf, self.data_sink, [('outputnode.dti_l2', 'diffusion.dti.@dti_l2')]),
            (self.dwi_wf, self.data_sink, [('outputnode.dti_l3', 'diffusion.dti.@dti_l3')]),
            (self.dwi_wf, self.data_sink, [('outputnode.dti_v1', 'diffusion.dti.@dti_v1')]),
            (self.dwi_wf, self.data_sink, [('outputnode.dti_v2', 'diffusion.dti.@dti_v2')]),
            (self.dwi_wf, self.data_sink, [('outputnode.dti_v3', 'diffusion.dti.@dti_v3')]),
            (self.dwi_wf, self.data_sink, [('outputnode.fa2anat', 'diffusion.dti.@fa2anat')]),
	        (self.dwi_wf, self.data_sink, [('outputnode.fa2anat_dat', 'diffusion.dti.@fa2anat_dat')]),
	        (self.dwi_wf, self.data_sink, [('outputnode.fa2anat_mat', 'diffusion.dti.@fa2anat_mat')]),
                        
            #functional
            #(self.subjects_node,self.resting, [("subject", "inputnode.subject_id")]),
            (self.structural_wf, self.resting, [("outputnode.subject_id", "inputnode.subject_id")]),
            (self.nii_wrangler, self.resting, [("rsfmri", "inputnode.func")]),    
            (self.nii_wrangler, self.resting, [("rs_mag", "inputnode.rs_mag")]), 
            (self.nii_wrangler, self.resting, [("rs_ph", "inputnode.rs_ph")]),
            (self.nii_wrangler, self.resting, [("ep_rsfmri_fieldmap_te", "inputnode.te_diff")]),
            (self.structural_wf, self.resting, [('outputnode.brain', 'inputnode.anat_brain')]),
            (self.structural_wf, self.resting, [('outputnode.anat_head', 'inputnode.anat_head')]),
            (self.structural_wf, self.resting, [('outputnode.brainmask', 'inputnode.anat_brain_mask')]),
            (self.structural_wf, self.resting, [('outputnode.wmseg', 'inputnode.wmseg')]),
            (self.structural_wf, self.resting, [('outputnode.csfseg', 'inputnode.csfseg')]),
            (self.nii_wrangler, self.resting, [("ep_rsfmri_echo_spacings", "inputnode.echo_space")]),
            (self.nii_wrangler, self.resting, [("ep_TR", "inputnode.TR")]),
            (self.resting,self.data_sink, [('outputnode.tsnr','resting.moco.@tsnr_file')]),
            (self.resting,self.data_sink, [('outputnode.par','resting.moco.@realignment_parameters_file')]),
            (self.resting,self.data_sink, [('outputnode.rms','resting.moco.@rms')]),
            (self.resting,self.data_sink, [('outputnode.mean_epi','resting.moco.@mean_epi')]),
            (self.resting,self.data_sink, [('outputnode.realigned_ts','resting.moco.@realigned_ts')]),
            (self.resting,self.data_sink, [('outputnode.unwarped_mean_epi2fmap','resting.unwarp.@mean_epi_file_unwarped')]),
            (self.resting,self.data_sink, [('outputnode.coregistered_epi2fmap','resting.unwarp.@mean_epi_file')]),
            (self.resting,self.data_sink, [('outputnode.fmap','resting.unwarp.@fmap')]),
            (self.resting,self.data_sink, [('outputnode.fmap_fullwarp','resting.unwarp.@fmap_fullwarp')]),
            (self.resting,self.data_sink, [('outputnode.epi2anat_dat','resting.anat_coreg.@reg_file')]),
            (self.resting,self.data_sink, [('outputnode.epi2anat','resting.anat_coreg.@epi2anat')]),
            (self.resting,self.data_sink, [('outputnode.epi2anat_mat','resting.anat_coreg.@epi2anat_mat')]),
            (self.resting,self.data_sink, [('outputnode.full_transform_ts','resting.transform_ts.@full_transform_ts')]),
            (self.resting,self.data_sink, [('outputnode.full_transform_mean','resting.transform_ts.@full_transform_mean')]),
            (self.resting,self.data_sink, [('outputnode.resamp_t1','resting.transform_ts.@resamp_t1')]),
            (self.resting,self.data_sink, [('outputnode.comb_mask_resamp','resting.transform_ts.@comb_mask_resamp')]),
            (self.resting,self.data_sink, [('outputnode.dvars_file','resting.transform_ts.@dvars_file')]),
            (self.resting,self.data_sink, [('outputnode.out_warped', 'resting.aroma.@out_warped')]),
            (self.resting,self.data_sink, [('outputnode.out_warp_field', 'resting.aroma.@out_warp_field')]),
            (self.resting,self.data_sink, [('outputnode.aggr_denoised_file', 'resting.aroma.@aggr_denoised_file')]),
            (self.resting,self.data_sink, [('outputnode.nonaggr_denoised_file', 'resting.aroma.@nonaggr_denoised_file')]),
            (self.resting,self.data_sink, [('outputnode.ts_fullspectrum','resting.aroma.@denoised_fullspectrum')]),
            (self.resting,self.data_sink, [('outputnode.ts_filtered','resting.aroma.@denoised_filtered')])          
     
            ])

    """ self-inflating nodes """
    
    @property
    def subjects_node(self):
        if not getattr(self,"_subjects_node",None):
            self._subjects_node = pe.Node(
                    name="subs_node",
                    interface=util.IdentityInterface(
                            fields=["subject"]))
        return self._subjects_node
    @subjects_node.setter
    def subjects_node(self, val):
        self._subjects_node = val

    @property
    def dicom_grabber(self):
        if not getattr(self,"_dicom_grabber",None):
            self._dicom_grabber = pe.Node(
                    name = "dicom_source_1",
                    interface = nio.DataGrabber(
                            infields = ["subject"],
                            outfields = ["dicom"],))
            self._dicom_grabber.inputs.template = "subject"
            self._dicom_grabber.inputs.template_args = {"dicom": [["subject"]]}
            self._dicom_grabber.inputs.sort_filelist = True
        return self._dicom_grabber
    @dicom_grabber.setter
    def dicom_grabber(self, val):
        self._dicom_grabber = val

    @property
    def dicom_convert(self):
        if not getattr(self,"_dicom_convert",None):
            self._dicom_convert = pe.Node(name="dicom_convert", interface=Dcm2niix())
            self._dicom_convert.inputs.out_filename="%p_s%s"
        return self._dicom_convert
    @dicom_convert.setter
    def dicom_convert(self, val):
        self._dicom_convert = val

    @property
    def dicom_select(self):
        if not getattr(self,'_dicom_select',None):
            self._dicom_select = pe.Node(name="select_dicom", interface=util.Select(index = 0))
        return self._dicom_select
    @dicom_select.setter
    def dicom_select(self, val):
        self._dicom_select = val

    @property
    def dicom_info(self):
        if not getattr(self,'_dicom_info',None):
            self._dicom_info = pe.Node(name="dicom_info", interface=DicomInfo())
        return self._dicom_info
    @dicom_info.setter
    def dicom_info(self, val):
        self._dicom_info = val
        
    @property
    def bids(self):
        from bids_conversion import create_bids
        if not getattr(self,'_bids',None):
               self._bids = pe.Node(name="bids", interface=Function(
                           input_names=["dicom_info","bids_info","bids_output","subj"],
                           output_names=["bval_file", "bvec_file"],
                           function=create_bids))
        return self._bids
    @bids.setter
    def bids(self, val):
        self._bids = val

    @property
    def nii_wrangler(self):
        if not getattr(self,'_nii_wrangler',None):
            self._nii_wrangler = pe.Node(name="nii_wrangler", interface=NiiWrangler())
        return self._nii_wrangler
    @nii_wrangler.setter
    def nii_wrangler(self, val):
        self._nii_wrangler = val
        
    @property
    def structural_wf(self):
        from structural.structural import create_structural
        if not getattr(self,'_structural_wf',None):
            self._structural_wf = create_structural()
        return self._structural_wf
    @structural_wf.setter
    def structural_wf(self, val):
        self._structural_wf = val

    @property
    def resting(self):
        from functional.aroma_resting import create_resting
        if not getattr(self,'_resting',None):
            self._resting = create_resting()
        return self._resting
    @resting.setter
    def resting(self, val):
        self._resting = val
       
    @property
    def dwi_wf(self):
        from diffusion.diffusion import create_dti
        if not getattr(self,'_dwi_wf',None):
            self._dwi_wf = create_dti()
        return self._dwi_wf
    @dwi_wf.setter
    def dwi_wf(self, val):
        self._dwi_wf = val
   
        
    @property
    def data_sink(self):
        if not getattr(self,'_data_sink',None):
            self._data_sink = pe.Node(name="data_sink", interface=nio.DataSink())
        return self._data_sink
    @data_sink.setter
    def data_sink(self, val):
        self._data_sink = val

