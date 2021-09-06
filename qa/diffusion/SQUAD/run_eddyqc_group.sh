#!/bin/bash

#run group-wise QA

#remove old group file
rm -rf ./eddy_squad_list.txt
rm -rf ./squad

ls -d /data/pt_02205/preprocessed/T0/diffusion/eddy/*/eddy_corrected.qc >> ./eddy_squad_list_T0.txt
eddy_squad eddy_squad_list_T0.txt -o /data/pt_02205/Analysis/Preprocessing/qa/diffusion/squad_T0

ls -d /data/pt_02205/preprocessed/T18/diffusion/eddy/*/eddy_corrected.qc >> ./eddy_squad_list_T18.txt
eddy_squad eddy_squad_list_T18.txt -o /data/pt_02205/Analysis/Preprocessing/qa/diffusion/squad_T18
