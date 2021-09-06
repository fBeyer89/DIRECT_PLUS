# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 12:27:06 2015

@author: fbeyer
"""

#from workflow_nonhcp import create_workflow

##Or for other cases
from workflow_nonhcp_DBIEX import create_workflow

import sys
import os

'''
Meta script to run preprocessing for DIRECT-PLUS trial
---------------------------------------------------
Can run with file list
python run_workflow f {text file containing list of subjects}
'''

#with open(sys.argv[2], 'r') as f:
#    subjects = [line.strip() for line in f]

subjects=['s346']


root_dir = '/data/p_02205/TIME0/'
working_dir = '/data/pt_02205/wd/'
data_dir = root_dir
out_dir = '/data/pt_02205/preprocessed/T0/'

freesurfer_dir = '/data/pt_02205/freesurfer/'

tp="bl"

create_workflow(subjectlist=subjects,
                     working_dir=working_dir,
                     data_dir=data_dir,
                     freesurfer_dir=freesurfer_dir,
                     out_dir=out_dir,
                     tp=tp)
