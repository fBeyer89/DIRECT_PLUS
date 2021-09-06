# -*- coding: utf-8 -*-
"""
Created on Thu June 13 2019

@author: Frauke Beyer
"""
'''
Diffusion-weighted imaging preprocessing for ADI study
=========================================================================
denoising with dwidenoise + mrdegibbs from MRTrix3.0; 
prepare fieldmap based on magnitude and phase image
eddy-openmp from FSL with replace outliers option but no slice-to-volume
correction -> first processing version!!
-------------------------------------------------------------------------
'''
from nipype import Node, Workflow
from dwi_corr_util import (DWIdenoise, MRdegibbs)
from nipype.interfaces import fsl
from nipype.interfaces import utility as util


def create_distortion_correct():
    # fsl output type
    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')
    # initiate workflow
    distor_correct = Workflow(name='distor_correct')
    # input node
    inputnode = Node(util.IdentityInterface(fields=[
        'dwi',
        'bvals',
        'bvecs',
        'dwi_dwelltime'
    ]),
        name='inputnode')
    # output node
    outputnode = Node(util.IdentityInterface(fields=[
        'bo_brain',
        "bo_brainmask",
        "dwi_unringed",
        'dwi_denoised',
        "eddy_corr",
        "rotated_bvecs",
        "total_movement_rms",
	    "outlier_report",
        "cnr_maps",
        "residuals",
        "shell_params",
        "eddy_params"
    ]),
        name='outputnode')

       
    # noise reduction on all images
    denoise = Node(DWIdenoise(noise='noise.nii.gz'), name="denoise")
    unring = Node(MRdegibbs(), name="unring")
    
    #use first B0 images for registration with fieldmap
    extract_b0=Node(fsl.ExtractROI(x_min=0, x_size=-1,
                                   y_min=0, y_size=-1,
                                   z_min=0, z_size=-1,
                                   t_min=0,  t_size=1),    name='extract_b0')
      
    
    #create brain mask from average of 10 b0
    bet = Node(interface=fsl.BET(), name='bet')
    bet.inputs.mask = True
    bet.inputs.frac = 0.2
    bet.inputs.robust = True
    
    distor_correct.connect([
    (inputnode, denoise,[('dwi', 'in_file')]),
    (denoise, unring, [('out_file', 'in_file')]),
    (unring, extract_b0, [('out_file', 'in_file')]),
    (extract_b0, bet, [('roi_file', 'in_file')]),
    (denoise, outputnode, [('out_file', 'dwi_denoised')]),
    (unring, outputnode, [('out_file', 'dwi_unringed')]),
    (bet, outputnode, [("mask_file", "bo_brainmask")]),
    (bet, outputnode, [("out_file", "bo_brain")]),
    ])  
    
    
    #create acq parameters file/index file.
    def write_acq(epi_acq_time):
        import numpy as np
        import os
        fn=os.getcwd()+'/acqparams_dwi.txt'
        np.savetxt(fn, [0,-1, 0, epi_acq_time],  delimiter=' ', newline=' ', fmt='%.5f')
        return fn
        
    def write_index(dwi_file):
        import nibabel as nb
        import numpy as np
        import os
        if type(dwi_file)==list:
            dwi = nb.load(dwi_file[0])
            dwi_data = dwi.get_data()
        else:
            dwi = nb.load(dwi_file)
            dwi_data = dwi.get_data()   
    
        fn=os.getcwd()+'/index.txt'
        np.savetxt(fn, np.ones(np.shape(dwi_data)[3]),  delimiter=' ', newline='\n', fmt='%.0i')
        return fn

    mk_acq=Node(util.Function(input_names=["epi_acq_time"],
                  output_names=["fn"],
                  function = write_acq), name="mk_acq")  

    mk_index=Node(util.Function(input_names=["dwi_file"],
                  output_names=["fn"],
                  function = write_index), name="mk_index")  

    # eddy motion correction
    eddy = Node(fsl.epi.Eddy(), name="eddy")
    eddy.inputs.num_threads = 4#32 ## total number of CPUs to use
    eddy.inputs.repol = True
    eddy.inputs.cnr_maps=True
    eddy.inputs.residuals=True

    ''
    # connect the nodes
    ''
    distor_correct.connect([

        (inputnode, mk_index, [('dwi', 'dwi_file')]),
        (inputnode, mk_acq, [('dwi_dwelltime', 'epi_acq_time')]),
        (bet, eddy, [("mask_file", "in_mask")]),
        (inputnode, eddy, [("bvals", "in_bval")]),
        (inputnode, eddy, [("bvecs", "in_bvec")]),    
        (mk_acq, eddy, [('fn', 'in_acqp')]),
        (mk_index, eddy, [('fn', 'in_index')]),
        (unring, eddy, [("out_file", "in_file")]),
        (eddy, outputnode, [("out_corrected", "eddy_corr")]),
        (eddy, outputnode, [("out_parameter", "eddy_params")]),
        (eddy, outputnode, [("out_rotated_bvecs", "rotated_bvecs")]),
        (eddy, outputnode, [("out_movement_rms", "total_movement_rms")]),
        (eddy, outputnode, [("out_shell_alignment_parameters", "shell_params")]),
        (eddy, outputnode, [("out_outlier_report", "outlier_report")]),
        (eddy, outputnode, [("out_cnr_maps", "cnr_maps")]),
        (eddy, outputnode, [("out_residuals", "residuals")])

        
        ]) 
                             
                             
    return distor_correct
