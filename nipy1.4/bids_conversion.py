# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 11:08:45 2019

@author: fbeyer
"""


def strip_subj(subj):
    import re
    subject=re.sub('[.]','',subj)
    return subject


def create_bids(dicom_info,bids_info,bids_output,subj):
    import os
    import shutil
    import re
    import json

    ##check which subject and session
    [subj,ses]=re.split("_", subj)

    #print dicom_info
    if not (os.path.isdir('%ssub-%s/ses-%s' %(bids_output,subj,ses))):
        os.makedirs('%ssub-%s/ses-%s' %(bids_output,subj,ses))

    #create necessary folders.
    if not (os.path.isdir('%ssub-%s/ses-%s/anat' %(bids_output,subj,ses))):
        os.mkdir('%ssub-%s/ses-%s/anat' %(bids_output,subj,ses))
    if not (os.path.isdir('%ssub-%s/ses-%s/func' %(bids_output,subj,ses))):
        os.mkdir('%ssub-%s/ses-%s/func' %(bids_output,subj,ses))
    if not (os.path.isdir('%ssub-%s/ses-%s/dwi' %(bids_output,subj,ses))):
        os.mkdir('%ssub-%s/ses-%s/dwi' %(bids_output,subj,ses))
    if not (os.path.isdir('%ssub-%s/ses-%s/fmap' %(bids_output,subj,ses))):
        os.mkdir('%ssub-%s/ses-%s/fmap' %(bids_output,subj,ses))

    for sm in dicom_info:
        if sm['protocol_name']=="FLAIR_tra":
            #find list element from json
            r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))

            sel_json=list(filter(r.match,bids_info))

            shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_FLAIR.nii.gz' %(bids_output,subj,ses,subj,ses))
            shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_FLAIR.json' %(bids_output,subj,ses,subj,ses))

        elif sm['series_desc']=="T1_MPR_sag_Head-Brain":
            print "t1 is found"
            #find list element from json
            r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))

            sel_json=list(filter(r.match,bids_info))

            shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_T1w.nii.gz' %(bids_output,subj,ses,subj,ses))
            shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_T1w.json' %(bids_output,subj,ses,subj,ses))


        elif sm['series_desc']=="BOLD resting state":


            #because the series description contains spaces, the json file has to be defined differently        
            x=re.split('/',sm['nifti_file'])
            rs=x[-1][:-7]

            r = re.compile('.*%s.json' %rs)
            sel_json=list(filter(r.match,bids_info))

            shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/func/sub-%s_ses-%s_task-rest_bold.nii.gz' %(bids_output,subj,ses,subj,ses))
            shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/func/sub-%s_ses-%s_task-rest_bold.json' %(bids_output,subj,ses,subj,ses))


            fname='%ssub-%s/ses-%s/func/sub-%s_ses-%s_task-rest_bold.json' %(bids_output,subj,ses,subj,ses)
            with open(fname, 'r') as f:
                data = json.load(f)
                #print data
                data['TaskName']='rest'

            f.close()
            with open(fname, 'w') as f:
                json.dump(data, f)

        elif sm['series_desc']=="BOLD_FieldMapping" and sm['image_type'][2]=='M':

            #find list element from json
            r = re.compile('.*%s_s%s.*.json' %(sm['protocol_name'],sm['series_num']))
            sel_json=list(filter(r.match,bids_info))

            shutil.copyfile(sm['nifti_file'],'%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-rs_magnitude1.nii.gz' %(bids_output,subj,ses,subj,ses))
            fname='%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-rs_phasediff.json' %(bids_output,subj,ses,subj,ses)
            shutil.copyfile(sel_json[0], fname)

            with open(fname, 'r') as f:
                data = json.load(f)
                data['EchoTime1']=sm['echo_times'][1]*0.001
                data['EchoTime2']=sm['echo_times'][0]*0.001
                data['IntendedFor']='ses-%s/func/sub-%s_ses-%s_task-rest_bold.nii.gz' %(ses,subj,ses)
                f.close()
            with open(fname, 'w') as f:
                json.dump(data, f)

        elif sm['series_desc']=="BOLD_FieldMapping" and sm['image_type'][2]=='P':
            #find list element from json
            r = re.compile('.*%s_s%s.*.json' %(sm['protocol_name'],sm['series_num']))
            sel_json=list(filter(r.match,bids_info))


            shutil.copyfile(sm['nifti_file'],'%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-rs_phasediff.nii.gz' %(bids_output,subj,ses,subj,ses))


        elif sm['series_desc']=="DTI_64dir_23iso_86ms_TR7500":

                #find list element from json
                r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
                sel_json=list(filter(r.match,bids_info))


                shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/dwi/sub-%s_ses-%s_dwi.nii.gz' %(bids_output,subj,ses,subj,ses))
                shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/dwi/sub-%s_ses-%s_dwi.json' %(bids_output,subj,ses,subj,ses))


                #copy bval/bvec
                #get dir name of bval/bvex
                dirname=os.path.dirname(sel_json[0])
                shutil.copyfile('%s/%s_s%s.bvec' %(dirname,sm['protocol_name'],sm['series_num']), '%ssub-%s/ses-%s/dwi/sub-%s_ses-%s_dwi.bvec' %(bids_output,subj,ses,subj,ses))
                shutil.copyfile('%s/%s_s%s.bval' %(dirname,sm['protocol_name'],sm['series_num']), '%ssub-%s/ses-%s/dwi/sub-%s_ses-%s_dwi.bval' %(bids_output,subj,ses,subj,ses)) 
                bval_file='%s/%s_s%s.bval' %(dirname,sm['protocol_name'],sm['series_num'])
                bvec_file='%s/%s_s%s.bvec' %(dirname,sm['protocol_name'],sm['series_num'])


        elif sm['series_desc']=="gre_field_mapping_2.3iso"and sm['image_type'][2]=='M':
                r = re.compile('.*%s_s%s.*.json' %(sm['protocol_name'],sm['series_num']))
                sel_json=list(filter(r.match,bids_info))


                shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-dwi_magnitude1.nii.gz' %(bids_output,subj,ses,subj,ses))
                shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-dwi_phasediff.json' %(bids_output,subj,ses,subj,ses))

                fname='%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-dwi_phasediff.json' %(bids_output,subj,ses,subj,ses)
                with open(fname, 'r') as f:
                    data = json.load(f)
                    #print data

                    data['EchoTime1']=sm['echo_times'][0]*0.001
                    data['EchoTime2']=sm['echo_times'][1]*0.001
                    data['IntendedFor']='ses-%s/dwi/sub-%s_ses-%s_dwi.nii.gz' %(ses,subj,ses)

                f.close()
                with open(fname, 'w') as f:
                    json.dump(data, f)
        elif sm['series_desc']=="gre_field_mapping_2.3iso"and sm['image_type'][2]=='P':

                r = re.compile('.*%s_s%s.*.json' %(sm['protocol_name'],sm['series_num']))
                sel_json=list(filter(r.match,bids_info))


                shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-dwi_phasediff.nii.gz' %(bids_output,subj,ses,subj,ses))

    return bval_file, bvec_file