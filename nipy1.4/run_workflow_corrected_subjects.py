# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 12:27:06 2015

@author: fbeyer
run:
python run_workflow.py f subjectlist.txt
"""

from workflow_nonhcp_corrected_subjects import create_workflow
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

subjects=['s220']#

#for T0
#['s48','s67']
#["s231", "s333"]
#["s89","s278"]

#for T18
#s59
#s70
#s98
#s104
#s220
#s244
#['s22', 's142', 's284', 's299', 's342', 's348']

root_dir = '/data/p_02205/TIME18/'
working_dir = '/data/pt_02205/wd/T18/'
data_dir = root_dir
out_dir = '/data/pt_02205/preprocessed/T18/'

freesurfer_dir = '/data/pt_02205/freesurfer/'

tp="fu"
#"bl"
trt=0.041

#see Sample_characteristics.csv for which TRT value 
#change in scan parameters occured ~ march 2017.
#for s48 and s67 s89 -> trt=0.053
#for s278(T0), s231 and s333 (and all T18 subjects) -> trt=0.041
create_workflow(subjectlist=subjects,
                     working_dir=working_dir,
		            trt=trt,
                     data_dir=data_dir,
                     freesurfer_dir=freesurfer_dir,
                     out_dir=out_dir,
                     tp=tp)
