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

subjects=['s109','s110','s111','s112','s113','s114','s115','s116','s117','s118',
             's119','s121','s122','s124','s125','s126','s127','s128','s130','s131','s132','s133','s134','s135','s136','s139','s142','s143','s144','s145','s146',
             's148','s149','s150']
#urnning
#['s74','s75','s76','s81','s82','s83','s87','s88','s89','s90','s91','s92','s94','s96','s98','s99','s100','s101','s102','s104','s105','s106','s107','s108']
#done
#["s2","s3","s5","s6","s7","s9","s10","s11","s12","s13",'s31','s34','s34','s35','s36','s37','s38','s39','s41','s44','s46','s49','s50','s54','s55','s56','s58','s59','s60','s61','s62','s63','s66','s70','s72','s73']


root_dir = '/data/p_02205/TIME0/'
working_dir = '/data/pt_02205/wd'
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
