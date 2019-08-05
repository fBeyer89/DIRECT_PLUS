#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 10:49:21 2019

@author: fbeyer
"""

import pydicom
import os
import pandas
import numpy

    
print "running program"
subjects=["s2","s3","s5","s6","s7","s9","s10","s11","s12","s13",'s31','s34','s34','s35','s36','s37','s38','s39','s41','s44','s46','s49','s50','s54','s55',
             's56','s58','s59','s60','s61','s62','s63','s66','s70','s72','s73','s74','s75','s76','s81','s82','s83','s87','s88','s89','s90','s91','s92','s94',
             's96','s98','s99','s100','s101','s102','s104','s105','s106','s107','s108','s109','s110','s111','s112','s113','s114','s115','s116','s117','s118',
             's119','s121','s122','s124','s125','s126','s127','s128','s130','s131','s132','s133','s134','s135','s136','s139','s142','s143','s144','s145','s146',
             's148','s149','s150','s151','s152','s153','s154','s155','s156','s157','s158','s159','s162','s163','s164','s165','s166','s167','s168','s169','s170',
             's173','s176','s177','s178','s180','s181','s182','s183','s184','s185','s187','s188','s189','s190','s192','s193','s194','s196','s197','s198','s199',
             's200','s201','s204','s205','s206','s210','s211','s212','s213','s214','s215','s216','s217','s218','s219','s220','s221','s222','s224','s225','s226',
             's227','s228','s229','s230','s231','s232','s234','s235','s236','s237','s238','s239','s240','s241','s242','s243','s244','s246','s247','s248','s249',
             's250','s251','s252','s253','s254','s255','s256','s257','s258','s259','s260','s261','s262','s263','s264','s265','s266','s267','s268','s269','s271',
             's272','s273','s274','s275','s277','','s280','s281','s282','s283','s284','s285','s289','s290','s293','s294','s295','s296','s297','s298','s299','s300',
             's301','s302','s305','s306','s309','s311','s312','s313','s314','s316','s317','s320','s322','s323','s324','s325','s326','s327','s328','s329','s332','s333',
             's334','s335','s336','s338','s339','s340','s341','s342','s343','s344','s345','s346','s347','s348','s349','s350','s351','s352','s353','s354','s356','s357',
             's358','s359','s360','s362','s364','s365','s366','s368','s369','s370','s371','s372','s373','s374','s375','s376','s378']

watfater=[None]*len(subjects)*2
pesteps=[None]*len(subjects)*2
date=[None]*len(subjects)*2
group=[None]*len(subjects)*2
age=[None]*len(subjects)*2
sex=[None]*len(subjects)*2
tpl=[None]*len(subjects)*2
subjl=[None]*len(subjects)*2
i=0
for subj in subjects:

    for tp in ['0','18']:
        f='/data/p_02205/TIME%s/%s/brain/DICOM/IM_0001' %(tp,subj)

        if os.path.isfile(f):
            d = pydicom.dcmread(f)
            #print d
            subjl[i]=subj
            watfater[i]=d[0x2001,0x1022].value
            pesteps[i]=d[0x0018,0x0089].value
            group[i]=d[0x2001,0x10c8].value
            date[i]=d[0x0040, 0x0244].value
            age[i]=d[0x0010,0x1010].value[1:3]
            sex[i]=d[0x0010,0x0040].value
            tpl[i]=tp
    
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
     'watfater': watfater}    

test=pandas.DataFrame(dictobj)        
test.to_csv('/data/pt_02205/scripts/subjects.csv')