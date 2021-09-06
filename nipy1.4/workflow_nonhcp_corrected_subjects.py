# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 12:26:20 2015

@author: fbeyer
"""

from nipype.pipeline.engine import Node, Workflow
import nipype.interfaces.utility as util
import nipype.interfaces.io as nio
import nipype.interfaces.fsl as fsl
from nipype.interfaces.dcm2nii import Dcm2nii

#import workflows to use
from structural.structural import create_structural
from diffusion.diffusion import create_dti

'''
Main workflow for DIRECT-PLUS study
====================================================
Uses file structure set up by conversion script.
'''


def create_workflow(subjectlist, working_dir, trt, data_dir, freesurfer_dir, out_dir, tp):
    # set fsl output type to nii.gz
    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')
    # main workflow
    direct_preproc = Workflow(name='direct_preproc')
    direct_preproc.base_dir = working_dir
    direct_preproc.config['execution']['crashdump_dir'] = direct_preproc.base_dir + "/crash_files"
    
    
    
    subjects_node = Node(name="subs_node",
                    interface=util.IdentityInterface(
                            fields=["subject"]))
    subjects_node.iterables = ("subject", subjectlist)
    
    def rename_subject(input_id, tp):
        output_id=input_id+"_"+tp
        return output_id
       
    #modify subject name so it can be saved in the same FREESURFER directory
    rename=Node(util.Function(input_names=['input_id', 'tp'], 
                            output_names=['output_id'],
                            function = rename_subject), name="rename")  
    rename.inputs.tp=tp
    
    #get anatomical image from NIFTI
    templates = {'anat_head': '{subject}/brain/*T1_3D_TFE_SENSE*.nii',
		 'dwi': '{subject}/brain/*DTI_high_iso*.nii',
		 'bval': '{subject}/brain/*DTI_high_iso*.bval',
		 'bvec': '{subject}/brain/*DTI_high_iso*.bvec'
                 }
    selectfiles = Node(nio.SelectFiles(templates,
                                       base_directory=data_dir),
                       name="selectfiles")
     
    
    #structural workflow   
    structural_wf = create_structural()
    structural_wf.inputs.inputnode.freesurfer_dir=freesurfer_dir
    
    #diffusion workflow 
    dwi_wf = create_dti()
    dwi_wf.inputs.inputnode.freesurfer_dir=freesurfer_dir
    dwi_wf.inputs.inputnode.dwi_dwelltime=trt
    
    #sink to store files
    sink = Node(nio.DataSink(parameterization=True,
                             base_directory=out_dir,
                             substitutions = 
                             [('_subject_', '')]), name='sink')


    # connections
    direct_preproc.connect([
        # remove the first volumes
        (subjects_node, selectfiles, [("subject", "subject")]),
        (selectfiles, structural_wf, [("anat_head", "inputnode.anat")]),           
        (subjects_node, rename, [("subject", "input_id")]),
        (rename, structural_wf, [("output_id", "inputnode.subject")]),
        (structural_wf, sink, [('outputnode.brain', 'structural.@brain')]),
        (structural_wf, sink, [('outputnode.anat_head', 'structural.@anat_head')]),
        (structural_wf, sink, [('outputnode.brainmask', 'structural.@brainmask')]),
              
        #diffusion workflow
        #(subjects_node,dwi_wf, [("subject", "inputnode.subject_id")]),
	(structural_wf, dwi_wf, [("outputnode.subject_id", "inputnode.subject_id")]),
        (selectfiles, dwi_wf, [("dwi", "inputnode.dwi")]),
        (selectfiles, dwi_wf, [("bvec", "inputnode.bvecs")]),
        (selectfiles, dwi_wf, [("bval", "inputnode.bvals")]),
        (dwi_wf, sink, [('outputnode.dwi_denoised', 'diffusion.@dwi_denoised')]),
        (dwi_wf, sink, [('outputnode.dwi_unringed', 'diffusion.@dwi_unringed')]),
        (dwi_wf, sink, [('outputnode.bo_brainmask', 'diffusion.@bo_brainmask')]),
        (dwi_wf, sink, [('outputnode.bo_brain', 'diffusion.@bo_brain')]),
        (dwi_wf, sink, [('outputnode.rotated_bvecs', 'diffusion.eddy.@rotated_bvecs')]),
        (dwi_wf, sink, [('outputnode.eddy_corr', 'diffusion.eddy.@eddy_corr')]),
        (dwi_wf, sink, [('outputnode.total_movement_rms', 'diffusion.eddy.@total_movement_rms')]),
        (dwi_wf, sink, [('outputnode.cnr_maps', 'diffusion.eddy.@cnr_maps')]),
        (dwi_wf, sink, [('outputnode.residuals', 'diffusion.eddy.@residuals')]),
        (dwi_wf, sink, [('outputnode.shell_params', 'diffusion.eddy.@shell_params')]),
        (dwi_wf, sink, [('outputnode.outlier_report', 'diffusion.eddy.@outlier_report')]),
        (dwi_wf, sink, [('outputnode.eddy_params', 'diffusion.eddy.@eddy_params')]),
        (dwi_wf, sink, [('outputnode.dti_fa', 'diffusion.dti.@dti_fa')]),
        (dwi_wf, sink, [('outputnode.dti_md', 'diffusion.dti.@dti_md')]),
        (dwi_wf, sink, [('outputnode.dti_l1', 'diffusion.dti.@dti_l1')]),
        (dwi_wf, sink, [('outputnode.dti_l2', 'diffusion.dti.@dti_l2')]),
        (dwi_wf, sink, [('outputnode.dti_l3', 'diffusion.dti.@dti_l3')]),
        (dwi_wf, sink, [('outputnode.dti_v1', 'diffusion.dti.@dti_v1')]),
        (dwi_wf, sink, [('outputnode.dti_v2', 'diffusion.dti.@dti_v2')]),
        (dwi_wf, sink, [('outputnode.dti_v3', 'diffusion.dti.@dti_v3')]),
        (dwi_wf, sink, [('outputnode.fa2anat', 'diffusion.dti.@fa2anat')]),
        (dwi_wf, sink, [('outputnode.fa2anat_dat', 'diffusion.dti.@fa2anat_dat')]),
        (dwi_wf, sink, [('outputnode.fa2anat_mat', 'diffusion.dti.@fa2anat_mat')])])
    

    direct_preproc.write_graph(dotfilename='direct_preproc.dot', graph2use='colored', format='pdf', simple_form=True)
    direct_preproc.run(plugin='MultiProc', plugin_args={'initial_specs': 'request_memory = 1500'})
    #direct_preproc.run(plugin='CondorDAGMan', plugin_args={'initial_specs': 'request_memory = 1500'})
    
    #
