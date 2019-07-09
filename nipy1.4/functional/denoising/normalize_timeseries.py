# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 12:31:26 2015

@author: fbeyer
"""


def time_normalizer(in_file, tr):
    '''
    Mean centering and variance normalizing a time series
    '''
    import os
    import nitime.fmri.io as io
    import nibabel as nib
    from nipype.utils.filemanip import fname_presuffix
    T = io.time_series_from_file(in_file, normalize=None,
                                 TR=tr)  
    #could change the normalization to percent or something but here keep it raw
    normalized_data = T.data
    img = nib.load(in_file)
    out_img = nib.Nifti1Image(normalized_data, img.affine(), header=img.header)
    out_file = fname_presuffix(in_file, suffix='_norm', newpath=os.getcwd())
    out_img.to_filename(out_file)
    return out_file
