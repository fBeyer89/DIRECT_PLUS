# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 12:27:06 2015

@author: fbeyer
run:
python run_workflow.py f subjectlist.txt
"""

from workflow_nonhcp import create_workflow
#workflow_nonhcp_DBIEX
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

subjects=['s1','s4','s5','s9','s10','s11','s13','s15','s17','s19','s20','s21','s22','s23','s24','s27','s31','s34','s35','s36','s37','s39','s44','s46','s49','s50','s54','s55','s56','s58','s60','s61','s62','s63','s66','s72','s73','s75','s76','s81','s82','s83','s87','s88','s89','s90','s91','s92','s94','s96','s98','s99','s100']
        

#done
#['s74','s75','s76','s81','s82','s83','s87','s88','s90','s91','s92','s94','s96','s98','s99','s100','s101','s102','s104','s105','s106','s107','s108']
#['s151','s152','s153','s154','s155','s156','s157','s158','s159','s162','s163','s165','s166','s167','s168','s169','s170','s173','s176','s177','s178','s180','s181','s182','s183','s184','s185','s187','s188','s189','s190','s192','s193','s194','s196','s197','s198','s199','s200']
#['s109','s110','s112','s113','s114','s115','s116','s117',
#'s119','s121','s122','s124','s125','s126','s127','s128','s130','s131','s132','s133','s134','s136','s142','s143','s144','s145','s146',
#'s149','s150']
#'s280','s281','s282','s283','s284','s285','s289','s290','s293','s294','s295','s296','s297','s298','s299','s300','s301','s302','s305','s306','s309','s311','s312','s313','s314','s316','s317','s320','s322','s323','s324','s325','s326','s327','s328','s329','s332','s334','s335','s336','s338','s339','s340','s341','s342','s343','s344','s345','s347','s349','s350','s351','s352','s353','s354','s356','s357','s358','s359','s360','s362','s365','s366','s368','s369','s370','s371','s372','s373','s374','s375','s376','s378'
#['s111','s135', 's139', 's148']
#run but some errors (see table='s201','s204','s205','s206','s210','s211','s212','s213','s214','s215','s216','s217','s218','s219','s220','s221','s222','s224','s225','s226','s227','s228','s229','s230','s231','s232','s234','s235','s236','s237','s238','s239','s240','s241','s242','s243','s244','s246','s247','s248','s249','s250','s251','s252','s253','s254','s255','s256','s257','s258','s259','s260','s261','s262','s263','s264','s265','s266','s267','s268','s269','s271','s272','s273','s274','s275','s277']
#subjects with another anat name: 's1','s118','s164','s242'] (DBIEX_4_1) + 's346' DBIEX_3_1

root_dir = '/data/p_02205/TIME18/'
working_dir = '/data/pt_02205/wd/T18/'
data_dir = root_dir
out_dir = '/data/pt_02205/preprocessed/T18/'

freesurfer_dir = '/data/pt_02205/freesurfer/'

tp="fu"

create_workflow(subjectlist=subjects,
                     working_dir=working_dir,
                     data_dir=data_dir,
                     freesurfer_dir=freesurfer_dir,
                     out_dir=out_dir,
                     tp=tp)
