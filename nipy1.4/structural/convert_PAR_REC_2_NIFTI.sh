#!/bin/bash

#USE MRICRON environment


for subj in s108 s116 s185 s197 s216 s241 s252 s260 s273 s275 s313 s372 s378

#s41

do


dcm2nii -g N -f Y -o /data/p_02205/TIME18/${subj}/brain/ /data/p_02205/TIME18/${subj}/brain/*_T1_3D_TFE_SENSE_3_1.*

done
