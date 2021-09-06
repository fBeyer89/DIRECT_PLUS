#!/bin/bash

SUBJECTS_DIR="/data/pt_02205/freesurfer/"

for subj in s204
do

##newer Version (not available in Freesurfer6.0.0p1
#segmentHA_T1_long.sh ${subj}

#older version
longHippoSubfieldsT1.sh ${subj}

done
