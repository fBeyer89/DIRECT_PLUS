# -*- coding: utf-8 -*-
"""
Created on Thu June 13 2019

@author: Frauke Beyer
"""
'''
Diffusion-weighted imaging preprocessing for ADI study
=========================================================================
denoising with dwidenoise from MRTrix3.0; 
prepare fieldmap based on magnitude and phase image
eddy-openmp from FSL with replace outliers option but no slice-to-volume
correction
-------------------------------------------------------------------------
'''
from nipype import Node, Workflow
from dwi_corr_util import DWIdenoise
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
        'dwi_mag',
        'dwi_ph',
        'bvals',
        'bvecs',
        'dwi_dwelltime',
        'te_diff'
    ]),
        name='inputnode')
    # output node
    outputnode = Node(util.IdentityInterface(fields=[
        'bo_brain',
        "bo_brainmask",
        'dwi_denoised',
        "mag2b0mat",
        "mag2b0",
        "fmap",
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

    
    #use the first B0 image for registration with fieldmap
    extract_b0=Node(fsl.ExtractROI(x_min=0, x_size=-1,
                                   y_min=0, y_size=-1,
                                   z_min=0, z_size=-1,
                                   t_min=0,  t_size=1),    name='extract_b0')
    
    #create brain mask from first b0
    bet = Node(interface=fsl.BET(), name='bet')
    bet.inputs.mask = True
    bet.inputs.frac = 0.2
    bet.inputs.robust = True
    
    distor_correct.connect([
    (inputnode, denoise,[('dwi', 'in_file')]),
    (denoise, extract_b0, [('out_file', 'in_file')]),
    (extract_b0, bet, [('roi_file', 'in_file')]),
    (denoise, outputnode, [('out_file', 'dwi_denoised')]),
    (bet, outputnode, [("mask_file", "bo_brainmask")]),
    (bet, outputnode, [("out_file", "bo_brain")]),
    ])  
    
    #register mag and B0 image with flirt    
    mag2b0 = Node(fsl.FLIRT(dof=6,
    out_file='mag2b0.nii.gz',
    interp='spline'), name="mag2b0")
  
    
    distor_correct.connect([(inputnode,mag2b0,[('dwi_mag', 'in_file')]),
    (extract_b0, mag2b0, [('roi_file', 'reference')]),
    (mag2b0, outputnode, [('out_matrix_file', 'mag2b0mat')]),
    (mag2b0, outputnode, [('out_file', 'mag2b0')])
    ]) 
      
    #### prepare fieldmap ####   
    #skullstrip magnitude image and erode even further
    bet_mag = Node(fsl.BET(frac=0.5,    mask=True),    name='bet_mag')
    distor_correct.connect(inputnode,'dwi_mag', bet_mag,'in_file')   
    erode = Node(fsl.maths.ErodeImage(kernel_shape='sphere',    kernel_size=3,    args=''),    name='erode')
    distor_correct.connect(bet_mag,'out_file', erode, 'in_file')
    
    # prepare fieldmap
    prep_fmap = Node(fsl.epi.PrepareFieldmap(),    name='prep_fmap')
    distor_correct.connect([(erode, prep_fmap, [('out_file', 'in_magnitude')]),   
                        (inputnode, prep_fmap, [('dwi_ph', 'in_phase'),('te_diff', 'delta_TE')]),
                        (prep_fmap, outputnode, [('out_fieldmap','fmap')])
                        ])
    #divide by 2pi
    calc_hz= Node(fsl.ImageMaths(),    name='calc_hz')
    calc_hz.inputs.op_string='-div 6.2832'
    
    
    #remove second volume of fieldmap as it is not useful
    remove_vol=Node(fsl.ExtractROI(x_min=0, x_size=-1,
                                   y_min=0, y_size=-1,
                                   z_min=0, z_size=-1,
                                   t_min=0,  t_size=1),    name='remove_vol')   
    
    #convert . into _ in filenames (otherwise eddy will throw an error)       
    def correct_fn(fn):
        import shutil
        import re
        if fn[-7:]=='.nii.gz':
             fn_for_eddy=fn[:-7]
             new=re.sub("2.3", "2_3", fn_for_eddy)
             shutil.copyfile(fn, new+'.nii.gz')
             return new
        else:
            fn_for_eddy=fn[:-4]
            new=re.sub("2.3", "2_3", fn_for_eddy)
            shutil.copyfile(fn, new+'.mat')  
            return new+'.mat'     
        
    adjust_fmap = Node(util.Function(input_names=["fn"],
                  output_names=["fn"],
                  function = correct_fn), name="adjust_fmap")  

    adjust_mat = Node(util.Function(input_names=["fn"],
                  output_names=["fn"],
                  function = correct_fn), name="adjust_mat")      
    
    distor_correct.connect([
        (prep_fmap, calc_hz, [('out_fieldmap', 'in_file')]),
        (calc_hz, remove_vol, [('out_file', 'in_file')]),
        (remove_vol, adjust_fmap, [('roi_file', 'fn')]),
        (mag2b0, adjust_mat, [('out_matrix_file', 'fn')])
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
        dwi = nb.load(dwi_file)
        dwi_data = dwi.get_data()
    
        fn=os.getcwd()+'/index.txt'
        np.savetxt(fn, np.ones(np.shape(dwi_data)[3]),  delimiter=' ', newline=' ', fmt='%.0i')
        return fn

    mk_acq=Node(util.Function(input_names=["epi_acq_time"],
                  output_names=["fn"],
                  function = write_acq), name="mk_acq")  

    mk_index=Node(util.Function(input_names=["dwi_file"],
                  output_names=["fn"],
                  function = write_index), name="mk_index")  

    # eddy motion correction
    eddy = Node(fsl.epi.Eddy(), name="eddy")
    eddy.inputs.num_threads = 16 ## total number of CPUs to use
    eddy.inputs.repol = True
    eddy.inputs.cnr_maps=True
    eddy.inputs.residuals=True
    eddy.inputs.dont_peas=True
    #from the eddy user guide
    #we have single shell data and dispersed acquisition of B0 images.
    #But, if one has a data set with a single shell (i.e. a single non-zero shell) 
    #and the assumption of no movement between the first b=0 and the first 
    #diffusion weighted image is true it can be better to avoid that uncertainty. 
    #And in that case it may be better to turn off peas by setting the 
    #--dont_peas flag. 


    ''
    # connect the nodes
    ''
    distor_correct.connect([

        (inputnode, mk_index, [('dwi', 'dwi_file')]),
        (inputnode, mk_acq, [('dwi_dwelltime', 'epi_acq_time')]),
        (bet, eddy, [("mask_file", "in_mask")]),
        (inputnode, eddy, [("bvecs", "in_bvec")]),
        (inputnode, eddy, [("bvals", "in_bval")]),
        (mk_acq, eddy, [('fn', 'in_acqp')]),
        (mk_index, eddy, [('fn', 'in_index')]),
        (adjust_mat, eddy, [('fn', 'field_mat')]),
        (adjust_fmap, eddy, [('fn', 'field')]),
        (denoise, eddy, [("out_file", "in_file")]),
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
