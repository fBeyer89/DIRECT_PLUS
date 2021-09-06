#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 10:49:21 2019

@author: fbeyer
#Use environment agewell_nip1.2 (py2 + pydicom + pandas)
"""

import pydicom
import os
import pandas as pd
import numpy as np

    
print "running program"
subj=pd.read_csv("/data/p_02205/sample_description/participants_overview.csv")
subjects=subj.iloc[:,0]
watfater=[None]*len(subjects)*2
pesteps=[None]*len(subjects)*2
date=[None]*len(subjects)*2
group=[None]*len(subjects)*2
name=[None]*len(subjects)*2
age=[None]*len(subjects)*2
sex=[None]*len(subjects)*2
tpl=[None]*len(subjects)*2
subjl=[None]*len(subjects)*2
i=0
for subj in subjects:

    for tp in ['0','18']:
        f='/data/p_02205/TIME%s/%s/brain/DICOM/IM_0001' %(tp,subj)
        subjl[i]=subj
        tpl[i]=tp
        if os.path.isfile(f):
            d = pydicom.dcmread(f)
            #print d
            watfater[i]=d[0x2001,0x1022].value
            pesteps[i]=d[0x0018,0x0089].value
            group[i]=d[0x2001,0x10c8].value
            date[i]=d[0x0040, 0x0244].value
            age[i]=d[0x0010,0x1010].value[1:3]
            sex[i]=d[0x0010,0x0040].value
            name[i]=d[0x0010,0x0010].value
        i+=1   
        #print(d[(0x0018,0x9240)].value)
dictobj = {
     'subjid': subjl,
     'age': age,
     'sex': sex,
     'group': group,
     'tp':tpl,
     'data': date,
     'pesteps': pesteps,
     'watfater': watfater,
     'name' : name}    

test=pd.DataFrame(dictobj)        
#print(test)
test.to_csv('/data/p_02205/sample_description/Sample_characteristics_from_DICOM.csv')
