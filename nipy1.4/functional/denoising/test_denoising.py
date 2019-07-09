#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 12:09:46 2019

@author: fbeyer
"""

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
    
    
cc_reg="/data/pt_02161/wd/adi_prep/resting/denoise/_subject_ADI009_bl/compcor/components_file.txt"
mask="/data/pt_02161/wd/adi_prep/resting/transform_timeseries/_subject_ADI009_bl/final_mask/rest_mean2anat_lowres_brain_mask_maths_maths.nii.gz"
epi_coreg="/data/pt_02161/wd/adi_prep/resting/_subject_ADI009_bl/meanintensnorm/rest2anat_maths.nii.gz"

[x,y]=create_designs(cc_reg,epi_coreg,mask)

print x
print y