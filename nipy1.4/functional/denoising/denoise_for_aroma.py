# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 12:34:01 2015

@author: fbeyer
"""

from nipype.pipeline.engine import Node, Workflow, MapNode
import nipype.interfaces.fsl as fsl
import nipype.interfaces.afni as afni
import nipype.interfaces.freesurfer as fs
import nipype.interfaces.utility as util
import nipype.algorithms.confounds as conf
#from compcor import extract_noise_components
#from fix_header_tr import fix_TR_fs

'''
Main workflow for denoising
Largely based on https://github.com/nipy/nipype/blob/master/examples/
rsfmri_vol_surface_preprocessing_nipy.py#L261
use denoising in functional space (project csf/wm mask to functional)
only regress wm+csf compcor-components (not motion components)
using highpass instead of bandpassfiltering and no normalization of timeseries
'''


def create_denoise_pipeline(name='denoise'):
    # workflow
    denoise = Workflow(name='denoise')
    # Define nodes
    inputnode = Node(interface=util.IdentityInterface(fields=['brain_mask',
                                                              'epi_coreg',
                                                              'wmseg',
                                                              'csfseg',
                                                              'highpass_freq',
                                                              'tr']),
                     name='inputnode')
    outputnode = Node(interface=util.IdentityInterface(fields=['wmcsf_mask',
                                                               'combined_motion',
                                                               'comp_regressor',
                                                               'comp_F',
                                                               'comp_pF',
                                                               'out_betas',
                                                               'ts_fullspectrum',
                                                               'ts_filtered']),
                      name='outputnode')

    # combine tissue classes to noise mask
    wmcsf_mask = Node(fsl.BinaryMaths(operation='add',
                                      out_file='wmcsf_mask.nii'),
                      name='wmcsf_mask')
    denoise.connect([(inputnode, wmcsf_mask, [('wmseg', 'in_file'),
                                              ('csfseg', 'operand_file')])])
        
    #resample + binarize wm_csf mask to epi resolution.
   
    resample_wmcsf= Node(afni.Resample(resample_mode='NN',
    outputtype='NIFTI_GZ',
    out_file='wmcsf_mask_lowres.nii.gz'),
    name = 'resample_wmcsf')
    
    bin_wmcsf_mask=Node(fsl.utils.ImageMaths(), name="bin_wmcsf_mask")
    bin_wmcsf_mask.inputs.op_string='-nan -thr 0.99 -ero -bin'
    
    denoise.connect([(wmcsf_mask, resample_wmcsf, [('out_file', 'in_file')]),
                     (inputnode, resample_wmcsf, [('brain_mask', 'master')]),
                     (resample_wmcsf, bin_wmcsf_mask,[('out_file', 'in_file')]),
                     (bin_wmcsf_mask, outputnode, [('out_file', 'wmcsf_mask')])
                    ])
         
    #no other denoising filters created here because AROMA performs already well.
       
    compcor=Node(conf.ACompCor(), name="compcor")
    compcor.inputs.num_components=5 #https://www.sciencedirect.com/science/article/pii/S105381191400175X?via%3Dihub
    denoise.connect([
                     (inputnode, compcor, [('epi_coreg', 'realigned_file')]),
                     (bin_wmcsf_mask, compcor, [('out_file', 'mask_files')]),
                     
                     ])    
    
    def create_designs(compcor_regressors,epi_coreg,mask):
            import numpy as np
            import pandas as pd
            import os
            from nilearn.input_data import NiftiMasker
           
            brain_masker = NiftiMasker(mask_img = mask, 
                               smoothing_fwhm=None, standardize=False,
                               memory='nilearn_cache', 
                               memory_level=5, verbose=2)
    
            whole_brain = brain_masker.fit_transform(epi_coreg)
            avg_signal = np.mean(whole_brain,axis=1)
            
            all_regressors=pd.read_csv(compcor_regressors,sep='\t')
            
            #add global signal.
            all_regressors['global_signal']=avg_signal
            
            fn=os.getcwd()+'/all_regressors.txt'
            all_regressors.to_csv(fn, sep='\t', index=False)
            
            return [fn, compcor_regressors]
            
    #create a list of design to loop over.
    create_design = Node(util.Function(input_names=['compcor_regressors','epi_coreg','mask'], output_names=['reg_list'], function=create_designs),
              name='create_design')
    
    denoise.connect([
    (compcor, create_design, [('components_file', 'compcor_regressors')]),
    (inputnode, create_design, [('epi_coreg', 'epi_coreg')]),
    (inputnode, create_design, [('brain_mask', 'mask')])
    ])
    
    # regress compcor and other noise components
    filter2 = MapNode(fsl.GLM(out_f_name='F_noise.nii.gz',
                           out_pf_name='pF_noise.nii.gz',
                           out_res_name='rest2anat_denoised.nii.gz',
                           output_type='NIFTI_GZ',
                           demean=True), 
                    iterfield=['design'],
                    name='filternoise')
    filter2.plugin_args = {'submit_specs': 'request_memory = 17000'}
    
    denoise.connect([(inputnode, filter2, [('epi_coreg', 'in_file')]),
                     #(createfilter2, filter2, [('out_files', 'design')]),
                     #(compcor, filter2, [('components_file', 'design')]),
                     (create_design, filter2, [('reg_list', 'design')]),
                     (inputnode, filter2, [('brain_mask', 'mask')]),
                     (filter2, outputnode, [('out_f', 'comp_F'),
                                            ('out_pf', 'comp_pF'),
                                            ('out_file', 'out_betas')
                                            ])
                     ])



    def calc_sigma(TR,highpass):
        # https://www.jiscmail.ac.uk/cgi-bin/webadmin?A2=ind1205&L=FSL&P=R57592&1=FSL&9=A&I=-3&J=on&d=No+Match%3BMatch%3BMatches&z=4
        sigma=1. / (2 * TR * highpass)
        return sigma

    calc_s=Node(util.Function(input_names=['TR', 'highpass'], output_names=['sigma'], function=calc_sigma),
                  name='calc_s')
    
    
    denoise.connect(inputnode, 'tr', calc_s, 'TR')
    denoise.connect(inputnode, 'highpass_freq', calc_s, 'highpass')
    
    #use only highpass filter (because high-frequency content is already somewhat filtered in AROMA)) 
    highpass_filter = MapNode(fsl.TemporalFilter(out_file='rest_denoised_highpassed.nii'),
                           name='highpass_filter', iterfield=['in_file'])
    highpass_filter.plugin_args = {'submit_specs': 'request_memory = 17000'}
    denoise.connect([(calc_s, highpass_filter, [('sigma', 'highpass_sigma')]),
                     (filter2, highpass_filter, [('out_file', 'in_file')]),
                     (filter2, outputnode, [('out_file', 'ts_fullspectrum')]),
                     (highpass_filter, outputnode, [('out_file', 'ts_filtered')])
                     ])
    
    return denoise
