# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 11:59:34 2018

@author: fbeyer
"""

def return_list_element(bvals,bvecs,dwi):
    import os
    import re
    import numpy as np

    #for the case that there is one DWI file identified by the nifti wrangler
    if (len(dwi)==1 and os.path.isfile(dwi[0])):
        
        #if there is more than one element for the bval/bvecs
        if type(bvals)==list:
                
            series_num_dwi=re.compile(".*cmrr_mbep2d_DTI_32Ch_s(.*).nii.gz*").match(dwi[0]).groups()
            
            for i in np.arange(0,len(bvals)):
                series_num_bval=re.compile(".*cmrr_mbep2d_DTI_32Ch_s(.*).bval*").match(bvals[i]).groups()
                
                if (series_num_dwi==series_num_bval):
                    index=i
                    
            bval_file=bvals[index]
            bvec_file=bvecs[index]
        else:
            bval_file=bvals   
            bvec_file=bvecs
    return bval_file,bvec_file

def orientation_from_dcm_header(header):
    # borrowed from hcp xnat dicom juggling java
    # get and check the base values
    if not header:
        raise ValueError("didn't get a header")
    o = getattr(header, "ImageOrientationPatient", None)
    o = [float(a) for a in o]
    if not o:
        raise ValueError("couldn't find ImageOrientationPatient in header")
    if len(o) != 6:
        raise ValueError("cannot be translated to cosine vectors")
    # consistency checks
    epsilon = 0.001
    if abs(o[0] * o[3] + o[1] * o[4] + o[2] * o[5]) > 0.001:
        raise ValueError("cosine vectors not orthogonal")
    if abs(1.0 - o[0] * o[0] - o[1] * o[1] - o[2] * o[2]) > epsilon:
        raise ValueError("cosine vectors not normal")
    # looks like we're good to go. derive the value
    absNormalX = abs(o[1] * o[5] - o[2] * o[4])
    absNormalY = abs(o[2] * o[3] - o[0] * o[5])
    absNormalZ = abs(o[0] * o[4] - o[1] * o[3])
    if absNormalX > absNormalY:
        return "sagittal" if absNormalX > absNormalZ else "transverse"
    else:
        return "coronal" if absNormalY > absNormalZ else "transverse"

def numberfy(s):
    n = s
    try:
        n = float(n)
        return n
    except Exception:
        return s

def float_or_none(s):
    n = s
    try:
        n = float(n)
        return n
    except Exception:
        return None

def int_or_none(s):
    n = s
    try:
        n = int(n)
        return n
    except ValueError:
        return None