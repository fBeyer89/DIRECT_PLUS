# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 12:27:06 2015

@author: fbeyer
run:
python run_workflow.py f subjectlist.txt
"""

from workflow_nonhcp import create_workflow
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

subjects=["s21","s22","s23","s24","s27","s28","s29"]
#["s14","s15","s16","s17","s19","s20"]
#["s2","s3","s4","s5","s6","s7","s9","s10","s11","s12","s13"]

root_dir = '/data/p_02205/TIME18/'
working_dir = '/data/pt_02205/wd/fu'
data_dir = root_dir
out_dir = '/data/pt_02205/preprocessed/T18/'

freesurfer_dir = '/data/pt_02205/freesurfer/'

dwi_dwelltime=0.053
tp="fu"

create_workflow(subjectlist=subjects,
                     working_dir=working_dir,
                     data_dir=data_dir,
                     freesurfer_dir=freesurfer_dir,
                     out_dir=out_dir,
                     dwi_dwelltime=dwi_dwelltime,
                     tp=tp)
