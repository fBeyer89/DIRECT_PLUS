# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 14:33:51 2015

@author: fbeyer
"""

'''
Main workflow for preprocessing of mprage data
===============================================
Uses file structure set up by conversion
'''
from nipype.pipeline.engine import Node, Workflow
import nipype.interfaces.io as nio
from reconall import create_reconall_pipeline
from mgzconvert import create_mgzconvert_pipeline
import nipype.interfaces.utility as util


def create_structural():
 
    # main workflow
    struct_preproc = Workflow(name='anat_preproc')   
    #struct_preproc.config['execution']['crashdump_dir'] = struct_preproc.base_dir + "/crash_files"
    #inputnode
    inputnode=Node(util.IdentityInterface(fields=['subject','anat',
    'out_dir',
    'freesurfer_dir'
    ]),
    name='inputnode')    
    
    outputnode=Node(util.IdentityInterface(fields=['brain','brainmask', 'anat_head','wmseg','csfseg','wmedge', 'subject_id']),
    name='outputnode')      
    
    # workflow to run freesurfer reconall
    reconall=create_reconall_pipeline()
    
    # workflow to get brain, head and wmseg from freesurfer and convert to nifti
    mgzconvert = create_mgzconvert_pipeline()
   
    
    # connections
    struct_preproc.connect(
        [(inputnode, reconall, [('anat', 'inputnode.anat')]),   
         (inputnode, reconall, [('subject', 'inputnode.fs_subject_id')]),
         (inputnode, reconall, [('freesurfer_dir', 'inputnode.fs_subjects_dir')]),
         (reconall, mgzconvert,  [('outputnode.fs_subject_id', 'inputnode.fs_subject_id'),
                                  ('outputnode.fs_subjects_dir', 'inputnode.fs_subjects_dir')]),  
         (mgzconvert, outputnode, [('outputnode.anat_brain', 'brain')]),
         (mgzconvert, outputnode, [('outputnode.anat_brain_mask', 'brainmask')]),
         (mgzconvert, outputnode, [('outputnode.anat_head', 'anat_head')]),
         (mgzconvert, outputnode, [('outputnode.wmseg', 'wmseg')]),
         (mgzconvert, outputnode, [('outputnode.csfseg', 'csfseg')]),
         (mgzconvert, outputnode, [('outputnode.wmedge', 'wmedge')]),
         (reconall, outputnode, [('outputnode.fs_subject_id', 'subject_id')])
         ])

    return struct_preproc