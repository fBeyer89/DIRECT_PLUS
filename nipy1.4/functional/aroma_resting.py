# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 12:26:20 2015

@author: fbeyer
"""

from nipype.pipeline.engine import Node, Workflow
import nipype.interfaces.utility as util
import nipype.interfaces.io as nio
import nipype.interfaces.fsl as fsl
import nipype.interfaces.afni as afni
from strip_rois import strip_rois_func
from moco import create_moco_pipeline
from transform_timeseries import create_transform_pipeline
from smoothing import create_smoothing_pipeline
from fieldmap_coreg import create_fmap_coreg_pipeline
from nipype.interfaces.fsl import ICA_AROMA
from denoising.denoise_for_aroma import create_denoise_pipeline
#from ants_registration import create_ants_registration_pipeline
'''
Main workflow for resting state preprocessing.
====================================================
Performs basic preprocessing and AROMA-based denoising 
1) removal of 4 initial volumes
2) distortion correction based on fieldmaps
3) realignment of volumes to first MCFLIRT
5) co-registration to structural
6) combine transform from functional to anatomical space
7) normalize intensity and spatial smoothing
8) calculate transform to MNI space for AROMA
9) ICA AROMA
10) removal of CompCor components from WM + CSF, highpass filtering
11) registration to MNI space with ANTS transforms
'''
def create_resting():

    # main workflow
    func_preproc = Workflow(name='resting')
    
    inputnode=Node(util.IdentityInterface(fields=
    ['subject_id',
    'out_dir',
    'freesurfer_dir',
    'func',
    'rs_mag',
    'rs_ph',
    'anat_head',
    'anat_brain',
    'anat_brain_mask',
    'wmseg',
    'csfseg',
    'vol_to_remove', 
    'TR',
    'highpass_freq',
    'epi_resolution',
    'echo_space', 
    'te_diff',
    'fwhm',
    'pe_dir',
    'composite_transform',
    'standard_brain',
    'standard_downsampled'
    ]),
    name='inputnode')   
         
    ##PREPROCESSING FOR AROMA (Steps 1 - 7)
    # node to remove first volumes
    remove_vol = Node(util.Function(input_names=['in_file','t_min'],
    output_names=["out_file"],
    function=strip_rois_func),
    name='remove_vol')
       
    # workflow for motion correction
    moco=create_moco_pipeline()
    
    # workflow for fieldmap correction and coregistration
    fmap_coreg=create_fmap_coreg_pipeline()
    
    # workflow for applying transformations to timeseries
    transform_ts = create_transform_pipeline()
     
    #reorient to std
    reorient2std=Node(fsl.Reorient2Std(), name="reorient2std")
    #mean intensity normalization
    meanintensnorm = Node(fsl.ImageMaths(op_string= '-ing 10000'), name='meanintensnorm')
    
    smoothing = create_smoothing_pipeline() 
 
    # connections
    func_preproc.connect([  
    (inputnode, remove_vol, [('func', 'in_file')]),
    (inputnode, remove_vol, [('vol_to_remove', 't_min')]),
    (inputnode, moco, [('anat_brain_mask', 'inputnode.brainmask')]),
    (remove_vol, moco, [('out_file', 'inputnode.epi')]),
    (inputnode, fmap_coreg,[('subject_id','inputnode.fs_subject_id'),
                            ('rs_mag', 'inputnode.mag'),
                            ('rs_ph', 'inputnode.phase'),
                            ('freesurfer_dir','inputnode.fs_subjects_dir'),                             
                            ('echo_space','inputnode.echo_space'),
                            ('te_diff','inputnode.te_diff'),
                            ('pe_dir','inputnode.pe_dir'),
                            ('anat_head', 'inputnode.anat_head'),
                            ('anat_brain', 'inputnode.anat_brain')
                            ]),
    (moco, fmap_coreg, [('outputnode.epi_mean', 'inputnode.epi_mean')]),
    (remove_vol, transform_ts, [('out_file', 'inputnode.orig_ts')]),
    (inputnode, transform_ts, [('anat_head', 'inputnode.anat_head')]),
    (inputnode, transform_ts, [('anat_brain_mask', 'inputnode.brain_mask')]),
    (inputnode, transform_ts, [('epi_resolution','inputnode.resolution')]),
    (moco, transform_ts, [('outputnode.mat_moco', 'inputnode.mat_moco')]),
    (fmap_coreg, transform_ts, [('outputnode.fmap_fullwarp', 'inputnode.fullwarp')]),
    (transform_ts, meanintensnorm, [('outputnode.trans_ts', 'in_file')]),
    (meanintensnorm, smoothing,  [('out_file', 'inputnode.ts_transformed')]),
    (inputnode, smoothing, [('fwhm', 'inputnode.fwhm')])
    ])
    
    ##CALCULATE TRANSFORM from anatomical to standard space with FSL tools
    # Anat > Standard
    # register high-resolution to standard template with non-linear transform
    # flirt serves as preparation for fnirt)
    
    #reorient brain to standard (because Freesurfer space can cause problems)
    #reorient2std = Node(fsl.Reorient2Std(), name="reorient2std")
    
    
    flirt_prep = Node(fsl.FLIRT(cost_func='mutualinfo', interp='trilinear'), name='flirt_prep')
    flirt_prep.inputs.interp='trilinear'
    flirt_prep.inputs.dof=12   
   
    fnirt=Node(fsl.FNIRT(), name='fnirt')
    fnirt.inputs.field_file=True
    fnirt.inputs.fieldcoeff_file=True
    
    
    func_preproc.connect([ 
    #(inputnode, reorient2std, [('anat_brain', 'in_file')])
    #(reorient2std, flirt_prep,  [('out_file', 'in_file')]),   
    (inputnode, flirt_prep,  [('anat_brain', 'in_file')]),  
    (inputnode, flirt_prep, [('standard_brain', 'reference')]),
    (flirt_prep, fnirt,    [('out_matrix_file', 'affine_file')]),          
    (inputnode,fnirt, [('anat_brain', 'in_file')]),
    (inputnode, fnirt, [('standard_brain', 'ref_file')]),
     ])

    
    def getcwd(subject_id):
        import os
        tmp=os.getcwd()
        tmp=tmp[:-6]
        tmp=tmp+'ica_aroma/out' #%(subject_id)
        return tmp
        
    get_wd = Node(util.Function(input_names=['subject_id'],
    output_names=["d"],
    function=getcwd),
    name='get_wd')
    
    ica_aroma= Node(ICA_AROMA(), name="ica_aroma")
    ica_aroma.inputs.denoise_type = 'both'
    #ica_aroma.inputs.out_dir = os.getcwd()

    func_preproc.connect([
    (moco, ica_aroma, [('outputnode.par_moco','motion_parameters')]),
    (smoothing, ica_aroma, [('outputnode.ts_smoothed', 'in_file')]),
    (fnirt, ica_aroma, [('field_file', 'fnirt_warp_file')]),
    (transform_ts, ica_aroma, [('outputnode.comb_mask_resamp', 'mask')]),
    (inputnode, get_wd, [('subject_id', 'subject_id')]),
    (get_wd, ica_aroma, [('d', 'out_dir')])
    ])

    ##POSTPROCESSING
    postprocess=create_denoise_pipeline()
    
    func_preproc.connect([
    (transform_ts, postprocess, [('outputnode.comb_mask_resamp', 'inputnode.brain_mask')]),                              
    (meanintensnorm, postprocess,   [('out_file', 'inputnode.epi_coreg')]),
    (inputnode, postprocess,    [('TR', 'inputnode.tr')]),
    (inputnode, postprocess,    [('highpass_freq', 'inputnode.highpass_freq')]),
    (inputnode, postprocess,    [('wmseg', 'inputnode.wmseg')]),
    (inputnode, postprocess,    [('csfseg', 'inputnode.csfseg')]),
    ])   
    
    #outputnode
    outputnode=Node(util.IdentityInterface(fields=['par','rms','mean_epi','tsnr','stddev_file', 'realigned_ts',
                                                   'fmap','unwarped_mean_epi2fmap', 'coregistered_epi2fmap', 'fmap_fullwarp', 
                                                   'epi2anat', 'epi2anat_mat','epi2anat_dat','epi2anat_mincost',
                                                   'full_transform_ts', 'full_transform_mean', 'resamp_t1', 'comb_mask_resamp','dvars_file',
                                                   'out_flirt_prep', 'out_matrix_flirt_prep', 'out_warped', 'out_warp_field',
                                                   'aggr_denoised_file', 'nonaggr_denoised_file', 'out_dir',
                                                   'wmcsf_mask','combined_motion','comp_regressor','comp_F','comp_pF',
                                                   'out_betas','ts_fullspectrum','ts_filtered']),
    name='outputnode')  
        
    # connections
    func_preproc.connect([
    (moco, outputnode, [#('outputnode.epi_moco', 'realign.@realigned_ts'),
    ('outputnode.par_moco', 'par'),
    ('outputnode.rms_moco', 'rms'),
    ('outputnode.epi_moco', 'realigned_ts'),
    ('outputnode.epi_mean', 'mean_epi'),
    ('outputnode.tsnr_file', 'tsnr'),
    ('outputnode.stddev_file', 'stddev'),
    ]),
    (fmap_coreg, outputnode, [('outputnode.fmap','fmap'),
    ('outputnode.unwarped_mean_epi2fmap', 'unwarped_mean_epi2fmap'),
    ('outputnode.epi2fmap', 'coregistered_epi2fmap'),
    ('outputnode.fmap_fullwarp', 'fmap_fullwarp'),
    ('outputnode.epi2anat', 'epi2anat'),
    ('outputnode.epi2anat_mat', 'epi2anat_mat'),
    ('outputnode.epi2anat_dat', 'epi2anat_dat'),
    ('outputnode.epi2anat_mincost', 'epi2anat_mincost')
    ]),
    (transform_ts, outputnode, [('outputnode.trans_ts', 'full_transform_ts'),
    ('outputnode.trans_ts_mean', 'full_transform_mean'),
    ('outputnode.resamp_t1', 'resamp_t1'),
    ('outputnode.comb_mask_resamp', 'comb_mask_resamp'),
    ('outputnode.out_dvars', 'dvars_file')]),
    (flirt_prep, outputnode, [('out_file', 'out_flirt_prep'),
    ('out_matrix_file', 'out_matrix_flirt_prep')]),
    (fnirt, outputnode, [('warped_file', 'out_warped'),
    ('field_file', 'out_warp_field')]),
    (ica_aroma, outputnode, [('aggr_denoised_file', 'aggr_denoised_file'),
                             ('nonaggr_denoised_file', 'nonaggr_denoised_file'),
                             ('out_dir','out_dir')]),
    (postprocess, outputnode, [('outputnode.wmcsf_mask', 'wmcsf_mask'),
                           ('outputnode.combined_motion','combined_motion'),
                           ('outputnode.comp_regressor', 'comp_regressor'),
                           ('outputnode.comp_F', 'comp_F'),
                           ('outputnode.comp_pF','comp_pF'),
                           ('outputnode.out_betas', 'out_betas'),
                           ('outputnode.ts_fullspectrum', 'ts_fullspectrum'),
                           ('outputnode.ts_filtered', 'ts_filtered')
                           ])
    
    ])
    
    
    return func_preproc
