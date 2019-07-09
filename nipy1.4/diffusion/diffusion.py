# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 13:41:03 2018

@author: Rui Zhang
"""

'''
Main workflow for preprocessing of diffusion-weighted data
==========================================================
Uses file structure set up by conversion
'''
from nipype import Node, Workflow
from distor_correct_gibbsringing import create_distortion_correct
from nipype.interfaces import fsl
from nipype.interfaces.utility import IdentityInterface
import nipype.interfaces.freesurfer as fs
import nipype.interfaces.utility as util
from inspect import getsourcefile
import os.path as path, sys
current_dir = path.dirname(path.abspath(getsourcefile(lambda:0)))
sys.path.insert(0, current_dir[:current_dir.rfind(path.sep)])
from util import return_list_element
sys.path.pop(0) 

def create_dti():
    # main workflow for preprocessing diffusion data
    # fsl output type
    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')
    # Initiation of a workflow
    dwi_preproc = Workflow(name="dwi_preproc")
    # inputnode
    inputnode = Node(IdentityInterface(fields=[
        'subject_id',
        'freesurfer_dir',
        'aseg',
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
    outputnode = Node(IdentityInterface(fields=[
        'bo_brain',
        "bo_brainmask",
        'dwi_denoised',
        'dwi_unringed',
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
        "eddy_params",
        'dti_fa',
        'dti_md',
        'dti_l1',
        'dti_l2',
        'dti_l3',
        'dti_v1',
        'dti_v2',
        'dti_v3',
        'fa2anat',
        'fa2anat_mat',
        'fa2anat_dat'
    ]),
        name='outputnode')

    '''
    workflow to run distortion correction
    -------------------------------------
    '''
    distor_corr = create_distortion_correct()

    '''
    tensor fitting
    --------------
    '''
    dti = Node(fsl.DTIFit(), name='dti')

    #connecting the nodes
    dwi_preproc.connect([

        (inputnode, distor_corr, [('dwi', 'inputnode.dwi')]),
        (inputnode, distor_corr, [('dwi_b0', 'inputnode.dwi_b0')]),
        (inputnode, distor_corr, [('dwi_mag', 'inputnode.dwi_mag')]),      
        (inputnode, distor_corr, [('dwi_ph', 'inputnode.dwi_ph')]),
        (inputnode, distor_corr, [("bvals", "inputnode.bvals")]),
        (inputnode, distor_corr, [("bvecs", "inputnode.bvecs")]),
        (inputnode, distor_corr, [("dwi_dwelltime", "inputnode.dwi_dwelltime")]),
        (inputnode, distor_corr, [("te_diff", "inputnode.te_diff")]),
        (distor_corr, outputnode, [('outputnode.bo_brain', 'bo_brain')]),
        (distor_corr, outputnode, [('outputnode.bo_brainmask', 'bo_brainmask')]),
        (distor_corr, outputnode, [('outputnode.dwi_denoised', 'dwi_denoised')]),
        (distor_corr, outputnode, [('outputnode.dwi_unringed', 'dwi_unringed')]),
        (distor_corr, outputnode, [('outputnode.fmap','fmap')]),
        (distor_corr, outputnode, [('outputnode.mag2b0mat','mag2b0mat')]),
        (distor_corr, outputnode, [('outputnode.mag2b0','mag2b0')]),
        (distor_corr, outputnode, [('outputnode.eddy_corr', 'eddy_corr')]),
        (distor_corr, outputnode, [('outputnode.rotated_bvecs', 'rotated_bvecs')]),
        (distor_corr, outputnode, [('outputnode.total_movement_rms', 'total_movement_rms')]),
        (distor_corr, outputnode, [('outputnode.cnr_maps', 'cnr_maps')]),
        (distor_corr, outputnode, [('outputnode.residuals', 'residuals')]),
        (distor_corr, outputnode, [('outputnode.shell_params', 'shell_params')]),
        (distor_corr, outputnode, [('outputnode.eddy_params', 'eddy_params')]),
        (distor_corr, outputnode, [('outputnode.outlier_report', 'outlier_report')]),
        (distor_corr, dti, [("outputnode.rotated_bvecs", "bvecs")]),
        (distor_corr, dti, [('outputnode.bo_brainmask', 'mask')]),
        (distor_corr, dti, [('outputnode.eddy_corr', 'dwi')]),
        (distor_corr, dti, [("outputnode.bvals", "bvals")]),
        (dti, outputnode, [('FA', 'dti_fa')]),
        (dti, outputnode, [('MD', 'dti_md')]),
        (dti, outputnode, [('L1', 'dti_l1')]),
        (dti, outputnode, [('L2', 'dti_l2')]),
        (dti, outputnode, [('L3', 'dti_l3')]),
        (dti, outputnode, [('V1', 'dti_v1')]),
        (dti, outputnode, [('V2', 'dti_v2')]),
        (dti, outputnode, [('V3', 'dti_v3')])

    ])

    '''
    coregistration of FA and T1
    ------------------------------------
    '''

    # linear registration with bbregister
    bbreg = Node(fs.BBRegister(contrast_type='t1',
    out_fsl_file='fa2anat.mat',
    out_reg_file='fa2anat.dat',
    registered_file='fa2anat_bbreg.nii.gz',
    init='fsl'
    ),
    name='bbregister')

    # connecting the nodes
    dwi_preproc.connect([

        (inputnode, bbreg, [('subject_id', 'subject_id')]),
        (inputnode, bbreg, [('freesurfer_dir', 'subjects_dir')]),
        (dti, bbreg, [("FA", "source_file")]),
        (bbreg, outputnode, [('out_fsl_file', 'fa2anat_mat'),
                             ('out_reg_file', 'fa2anat_dat'),
                             ('registered_file', 'fa2anat')])

    ])

    return dwi_preproc
