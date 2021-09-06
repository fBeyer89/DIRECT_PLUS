#!/bin/bash

cd /data/p_02205/participants_sep19/
for subj in 231 #4 7 48 59 59.1 67 70 89 98 98.1 104 104.1 220 220.1 231 244 244.1 278 333 333.1 
do
dcm2niix -o ${subj}/ ${subj}/${subj}.3/DICOMDIR

done
