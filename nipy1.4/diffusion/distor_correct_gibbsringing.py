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
        'dwi_b0',
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
        "dwi_unringed",
        'dwi_denoised',
        "mag2b0mat",
        "mag2b0",
        "fmap",
        "bvals",
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

   

    #create list:
    def merge_dwi(dwi_b0, dwi):
        return [dwi_b0,dwi]
    merge_list=Node(util.Function(input_names=["dwi_b0", "dwi"],
                  output_names=["all_dwi"],
                  function = merge_dwi), name="merge_list")  

    #merge the b0s with the bweighted file.    
    merge = Node(fsl.Merge(), name="merge")
    merge.inputs.dimension = 't'

    #change bval and bvec files.
    def change_bval_bvec(bval, bvec):
        import numpy as np
        import os
        bvec_vals=np.loadtxt(bvec)
        addzeros=np.zeros((3,9))
        bvec_vals_long=np.hstack((addzeros,bvec_vals))
        fn_bvec=os.getcwd()+'/bvecs_long.txt'
        np.savetxt(fn_bvec, bvec_vals_long,  delimiter=' ', newline='\n', fmt='%.5f')
        bval_vals=np.loadtxt(bval)
        addzeros=np.zeros(9)
        bval_vals_long=np.hstack((addzeros,bval_vals))
        fn_bval=os.getcwd()+'/bvals_long.txt'
        np.savetxt(fn_bval, bval_vals_long,  delimiter=' ', newline=' ', fmt='%.5f')                 
        return fn_bval,fn_bvec

    change_bvalbvec=Node(util.Function(input_names=["bval", "bvec"],
                  output_names=["fn_bval", "fn_bvec"],
                  function = change_bval_bvec), name="change_bvalbvec")
     
    distor_correct.connect([
    (inputnode, merge_list,[('dwi', 'dwi')]),
    (inputnode, merge_list,[('dwi_b0', 'dwi_b0')]),
    (merge_list, merge,[('all_dwi', 'in_files')]),
    (inputnode, change_bvalbvec, [("bvecs", "bvec")]),
    (inputnode, change_bvalbvec, [("bvals", "bval")])])
    
    # noise reduction on all images
    denoise = Node(DWIdenoise(noise='noise.nii.gz'), name="denoise")
    unring = Node(MRdegibbs(), name="unring")
    
    #use 10 B0 images for registration with fieldmap
    extract_b0=Node(fsl.ExtractROI(x_min=0, x_size=-1,
                                   y_min=0, y_size=-1,
                                   z_min=0, z_size=-1,
                                   t_min=0,  t_size=10),    name='extract_b0')
    
    #average over 10 timepoints.
    average_b0 = Node(fsl.ImageMaths(op_string= '-Tmean'), "average_b0")
    
    
    #create brain mask from average of 10 b0
    bet = Node(interface=fsl.BET(), name='bet')
    bet.inputs.mask = True
    bet.inputs.frac = 0.2
    bet.inputs.robust = True
    
    distor_correct.connect([
    (merge, denoise,[('merged_file', 'in_file')]),
    (denoise, unring, [('out_file', 'in_file')]),
    (unring, extract_b0, [('out_file', 'in_file')]),
    (extract_b0, average_b0, [('roi_file', 'in_file')]),
    (average_b0, bet, [('out_file', 'in_file')]),
    (denoise, outputnode, [('out_file', 'dwi_denoised')]),
    (unring, outputnode, [('out_file', 'dwi_unringed')]),
    (bet, outputnode, [("mask_file", "bo_brainmask")]),
    (bet, outputnode, [("out_file", "bo_brain")]),
    ])  
    
    #register mag and B0 image with flirt    
    mag2b0 = Node(fsl.FLIRT(dof=6,
    out_file='mag2b0.nii.gz',
    interp='spline'), name="mag2b0")
  
    
    distor_correct.connect([(inputnode,mag2b0,[('dwi_mag', 'in_file')]),
    (average_b0, mag2b0, [('out_file', 'reference')]),
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
    
    #smooth the fieldmap so eddy converges
    smooth_fieldmap=Node(fsl.preprocess.FUGUE() , name="smooth_fieldmap")
    smooth_fieldmap.inputs.smooth3d=4
    smooth_fieldmap.inputs.save_fmap=True
    #smooth_fieldmap.inputs.fmap_out_file="fieldmap_smoothed.nii.gz"  
    
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
        (remove_vol, smooth_fieldmap, [('roi_file', 'fmap_in_file')]),
        (smooth_fieldmap, adjust_fmap, [('fmap_out_file', 'fn')]),
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
    eddy.inputs.num_threads = 32 ## total number of CPUs to use
    eddy.inputs.repol = True
    eddy.inputs.cnr_maps=True
    eddy.inputs.residuals=True

    ''
    # connect the nodes
    ''
    distor_correct.connect([

        (merge, mk_index, [('merged_file', 'dwi_file')]),
        (inputnode, mk_acq, [('dwi_dwelltime', 'epi_acq_time')]),
        (bet, eddy, [("mask_file", "in_mask")]),
        (change_bvalbvec, eddy, [("fn_bval", "in_bval")]),
        (change_bvalbvec, eddy, [("fn_bvec", "in_bvec")]),    
        (change_bvalbvec, outputnode, [("fn_bval", "bvals")]),
        (mk_acq, eddy, [('fn', 'in_acqp')]),
        (mk_index, eddy, [('fn', 'in_index')]),
        (adjust_mat, eddy, [('fn', 'field_mat')]),
        (adjust_fmap, eddy, [('fn', 'field')]),
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
