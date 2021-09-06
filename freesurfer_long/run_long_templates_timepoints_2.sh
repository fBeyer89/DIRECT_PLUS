#!/bin/bash   

##create freesurfer longitudinal templates.  

#Processing single time point data through the longitudinal stream is now possible (usefull for LME where subjects with only a single time point can be included) (FS 5.2 or later).   

SUBJECTS_DIR="/data/pt_02205/freesurfer/"   

for subj in s346

do 
echo ${subj} 

if [ -d ${SUBJECTS_DIR}/${subj}_bl -a -d ${SUBJECTS_DIR}/${subj}_fu ]; 
then echo "both timepoints" 
recon-all -base ${subj} -tp ${subj}_bl -tp ${subj}_fu -all -openmp 64
recon-all -long ${subj}_fu ${subj} -all -openmp 64
recon-all -long ${subj}_bl ${subj} -all -openmp 64

elif [ -d ${SUBJECTS_DIR}/${subj}_bl ]; 
then echo "only bl" 
recon-all -base ${subj} -tp ${subj}_bl -all -openmp 64
recon-all -long ${subj}_bl ${subj} -all -openmp 64

elif [ -d ${SUBJECTS_DIR}/${subj}_fu ]; 
then echo "only fu" 
recon-all -base ${subj} -tp ${subj}_fu -all -openmp 64
recon-all -long ${subj}_fu ${subj} -all -openmp 64

else  echo "nothing for this subject at all"  
fi  

done
