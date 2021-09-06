# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 12:27:06 2015

@author: fbeyer
run:
python run_workflow.py f subjectlist.txt
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

subjects=['s376']




#T18:'s234', 's74'

#DBIEX: ''
#no anat files/DICOM: #'s244''s342',

#subjects with par/rec -> done
#['s41','s108','s116','s185','s197','s216','s241','s252','s260','s273','s275','s313','s372','s378']


#T0:
#run but some errors (see table='s201','s204','s205','s206','s210','s211','s212','s213','s214','s215','s216','s217','s218','s219','s220','s221','s222','s224','s225','s226','s227','s228','s229','s230','s231','s232','s234','s235','s236','s237','s238','s239','s240','s241','s242','s243','s244','s246','s247','s248','s249','s250','s251','s252','s253','s254','s255','s256','s257','s258','s259','s260','s261','s262','s263','s264','s265','s266','s267','s268','s269','s271','s272','s273','s274','s275','s277']
#subjects with another anat name: 's1','s118','s164','s242'] (DBIEX_4_1) + 's346' DBIEX_3_1

root_dir = '/data/p_02205/TIME18/'
working_dir = '/data/pt_02205/Data/wd/T18/'
data_dir = root_dir
out_dir = '/data/pt_02205/Data/preprocessed/T18/'

freesurfer_dir = '/data/pt_02205/Data/freesurfer/'

tp="fu"

create_workflow(subjectlist=subjects,
                     working_dir=working_dir,
                     data_dir=data_dir,
                     freesurfer_dir=freesurfer_dir,
                     out_dir=out_dir,
                     tp=tp)
