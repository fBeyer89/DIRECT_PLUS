#!/bin/bash

slist=`ls -d /data/pt_02205/freesurfer/*.long.* | cut -f5 -d"/"`

for elem in $slist 
do

tp=`echo $elem | cut -f1 -d'.' | cut -f2 -d'_'` 
subj=`echo $elem | cut -f1 -d'.' | cut -f1 -d'_'`

echo $subj
echo $tp

#if [ $tp == "bl" ];
#then echo "bl"
#fi

if [ -f /data/pt_02205/preprocessed/T0/structural/$subj/brain.nii.gz ] && [ -f /data/pt_02205/preprocessed/T0/diffusion/dti/$subj/fa2anat_bbreg.nii.gz ] && [ $tp == "bl" ];
then 
echo /data/pt_02205/preprocessed/T0/structural/$subj/brain.nii.gz /data/pt_02205/preprocessed/T0/diffusion/dti/$subj/fa2anat_bbreg.nii.gz >> forslicesdir.txt
fi
if [ -f /data/pt_02205/preprocessed/T18/structural/$subj/brain.nii.gz ] && [ -f /data/pt_02205/preprocessed/T18/diffusion/dti/$subj/fa2anat_bbreg.nii.gz ] && [ $tp == "fu" ];
then 
echo /data/pt_02205/preprocessed/T18/structural/$subj/brain.nii.gz /data/pt_02205/preprocessed/T18/diffusion/dti/$subj/fa2anat_bbreg.nii.gz >> forslicesdir.txt
fi


done
