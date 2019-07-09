#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 16:33:26 2019

@author: fbeyer
"""

def correct_fn(fn):
    import os
    import re
    if fn[-7:]=='.nii.gz':
         fn_for_eddy=fn[:-7]
         new=re.sub("2.3", "2_3", fn_for_eddy)
         os.rename(fn,new+'.nii.gz')
    else:
        fn_for_eddy=fn[:-4]
        new=re.sub("2.3", "2_3", fn_for_eddy)
        os.rename(fn,new+'.mat')    
    return new


#x=correct_fn('/data/pt_02161/wd/hcp_prep_workflow/dwi_preproc/distor_correct/fmap_coreg/_subject_ADI002_fu2/rm_vol/gre_field_mapping_2.3iso_s18_ph_fslprepared_maths_roi.nii.gz')

y=correct_fn('/data/pt_02161/wd/hcp_prep_workflow/dwi_preproc/distor_correct/_subject_ADI002_fu2/fmap2dwi/gre_field_mapping_2.3iso_s17_e2_flirt.mat')