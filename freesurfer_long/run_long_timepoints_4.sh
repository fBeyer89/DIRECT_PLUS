#!/bin/bash

SUBJECTS_DIR="/data/pt_02205/freesurfer/"   

for subj in s73 s74






#running slowly s210, s257
#rerun template s104

#for later: s73 s74 s75 s76 s210 s128

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
