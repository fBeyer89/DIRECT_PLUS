#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 13:57:37 2019

@author: fbeyer
"""

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
    return fn_bvec, fn_bval  


change_bval_bvec("/data/pt_02161/wd/hcp_prep/_subject_ADI082_fu2/dicom_convert/DTI_64dir_23iso_86ms_TR7500_s14.bval", 
                 "/data/pt_02161/wd/hcp_prep/_subject_ADI082_fu2/dicom_convert/DTI_64dir_23iso_86ms_TR7500_s14.bvec")



