#!/bin/bash

SUBJECTS_DIR="/data/pt_02205/freesurfer/"   

for subj in s162

do

if [ -d ${SUBJECTS_DIR}/${subj}_bl -a -d ${SUBJECTS_DIR}/${subj}_fu ];
then
echo "two timepoints bl+fu"

recon-all -long ${subj}_fu ${subj} -all -openmp 64
recon-all -long ${subj}_bl ${subj} -all -openmp 64

elif [ -d ${SUBJECTS_DIR}/${subj}_bl ];
then
echo "only bl"

recon-all -long ${subj}_bl ${subj} -all -openmp 64

else 
echo "nothing for this subj at all"

fi

done
