#!/bin/bash

SUBJECTS_DIR="/data/pt_02205/freesurfer/"


for subj in s1 s101 s102 s128 s163 s165 s166 s168 s204 s205 s206 s210 s255 s256 s257 s300 s301 s302 s306 s311 s313 s314 s81 s82 s83 s87 s88 s89  

do
echo ${subj}


if [ -d ${SUBJECTS_DIR}/${subj}_bl -a -d ${SUBJECTS_DIR}/${subj}_fu ];
then
echo "two timepoints bl+fu"

freeview ${SUBJECTS_DIR}/${subj}_bl.long.${subj}/mri/brainmask.mgz ${SUBJECTS_DIR}/${subj}_fu.long.${subj}/mri/brainmask.mgz -f ${SUBJECTS_DIR}/${subj}_bl.long.${subj}/surf/lh.pial:edgecolor=lightgreen ${SUBJECTS_DIR}/${subj}_bl.long.${subj}/surf/rh.pial:edgecolor=lightgreen ${SUBJECTS_DIR}/${subj}_fu.long.${subj}/surf/lh.pial:edgecolor=white ${SUBJECTS_DIR}/${subj}_fu.long.${subj}/surf/rh.pial:edgecolor=white

elif [ -d ${SUBJECTS_DIR}/${subj}_bl ];
then
echo "only bl"
freeview ${SUBJECTS_DIR}/${subj}_bl.long.${subj}/mri/brainmask.mgz -f ${SUBJECTS_DIR}/${subj}_bl.long.${subj}/surf/lh.pial:edgecolor=white ${SUBJECTS_DIR}/${subj}_bl.long.${subj}/surf/rh.pial:edgecolor=white
elif [ -d ${SUBJECTS_DIR}/${subj}_fu ];
then
echo "only fu"

freeview ${SUBJECTS_DIR}/${subj}_fu.long.${subj}/mri/brainmask.mgz -f ${SUBJECTS_DIR}/${subj}_fu.long.${subj}/surf/lh.pial:edgecolor=white ${SUBJECTS_DIR}/${subj}_fu.long.${subj}/surf/rh.pial:edgecolor=white

else 
echo "nothing for this subj at all"

fi
done





