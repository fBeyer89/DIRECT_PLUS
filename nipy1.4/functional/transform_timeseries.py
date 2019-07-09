# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 12:30:06 2015

@author: fbeyer
"""


from nipype.pipeline.engine import MapNode, Node, Workflow
import nipype.interfaces.utility as util
import nipype.interfaces.fsl as fsl
import nipype.interfaces.ants as ants
import nipype.interfaces.afni as afni
import nipype.interfaces.utility as util
import nipype.algorithms.confounds as confounds
'''
Workflow to apply all spatial transformations to each volume
of a time series in a single interpolation
'''
def create_transform_pipeline(name='transfrom_timeseries'):
    # set fsl output type
    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')
    # initiate workflow
    transform_ts = Workflow(name='transform_timeseries')
    # inputnode
    inputnode=Node(util.IdentityInterface(fields=['orig_ts',
    'anat_head',
    'mat_moco',
    'fullwarp',
    'resolution',
    'brain_mask',
    ]),
    name='inputnode')
    # outputnode
    outputnode=Node(util.IdentityInterface(fields=['trans_ts',
    'trans_ts_mean',
    'trans_ts_masked',
    'resamp_t1',
    'anat_mask_resamp',
    'comb_mask_resamp',
    'out_dvars'
    ]),
    name='outputnode')
    #resample anatomy
    resample = Node(fsl.FLIRT(datatype='float',
    out_file='T1_resampled.nii.gz'),
    name = 'resample_anat')
    transform_ts.connect([(inputnode, resample, [('anat_head', 'in_file'),
    ('anat_head', 'reference'),
    ('resolution', 'apply_isoxfm')
    ]),
    (resample, outputnode, [('out_file', 'resamp_t1')])
    ])
    # split timeseries in single volumes
    split=Node(fsl.Split(dimension='t',
    out_base_name='timeseries'),
    name='split')
    transform_ts.connect([(inputnode, split, [('orig_ts','in_file')])])
    
    # applymoco premat and fullwarpfield
    applywarp = MapNode(fsl.ApplyWarp(interp='spline',
    relwarp=True,
    out_file='rest2anat.nii.gz',
    datatype='float'),
    iterfield=['in_file', 'premat'],
    name='applywarp')
    transform_ts.connect([(split, applywarp, [('out_files', 'in_file')]),
    (inputnode, applywarp, 
    [('mat_moco', 'premat'),
    ('fullwarp','field_file')]),
    (resample, applywarp, [('out_file', 'ref_file')])
    ])
    # re-concatenate volumes
    merge=Node(fsl.Merge(dimension='t',
    merged_file='rest2anat.nii.gz'),
    name='merge')
    transform_ts.connect([(applywarp,merge,[('out_file','in_files')]),
    (merge, outputnode, [('merged_file', 'trans_ts')])])
    # calculate new mean
    tmean = Node(fsl.maths.MeanImage(dimension='T',
    out_file='rest_mean2anat_lowres.nii.gz'),
    name='tmean')
    transform_ts.connect([(merge, tmean, [('merged_file', 'in_file')]),
    (tmean, outputnode, [('out_file', 'trans_ts_mean')])
    ])
    
    #create brain mask from anatomical and brain extracted tmean 
    extract_epi_mask= Node(fsl.preprocess.BET(mask=True), name="extract_epi_mask")
    transform_ts.connect([(tmean, extract_epi_mask, [('out_file', 'in_file')]),
                          ])   
    
    resample_brain = Node(afni.Resample(resample_mode='NN',
    outputtype='NIFTI_GZ',
    out_file='T1_brain_mask_lowres.nii.gz'),
    name = 'resample_brain')
    
    combine_masks=Node(fsl.utils.ImageMaths(), name="combine_masks")
    #only use voxels that are present in both masks
    combine_masks.inputs.op_string='-add'
    
    final_mask=Node(fsl.utils.ImageMaths(), name="final_mask")
    final_mask.inputs.op_string='-thr 2 -bin'
    
    transform_ts.connect([(inputnode, resample_brain, [('brain_mask', 'in_file')]),
                          (tmean, resample_brain,     [('out_file', 'master')]),
                          (resample_brain, outputnode, [('out_file', 'anat_mask_resamp')]),
                          (extract_epi_mask, combine_masks, [('mask_file', 'in_file')]),
                          (resample_brain, combine_masks, [('out_file', 'in_file2')]),
                          (combine_masks, final_mask, [('out_file', 'in_file')]),
                          (final_mask, outputnode, [('out_file', 'comb_mask_resamp')])
                          ])
    

    
    #mask the transformed file
    mask = Node(fsl.ApplyMask(), name="mask")
    transform_ts.connect([(combine_masks,mask, [('out_file', 'mask_file')]),
                          (merge, mask, [('merged_file', 'in_file')]),
                          (mask, outputnode, [('out_file', 'trans_ts_masked')])
		         ])


    #calculate DVARS
    dvars = Node(confounds.ComputeDVARS(save_all=True, save_plot=True), name="dvars")
    transform_ts.connect([(resample_brain, dvars, [('out_file', 'in_mask')]),
                          (merge, dvars, [('merged_file', 'in_file')]),
                          (dvars, outputnode, [('out_all', 'out_dvars')])
                         ])



    
    return transform_ts
