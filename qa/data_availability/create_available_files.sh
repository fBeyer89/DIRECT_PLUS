rm -rf /data/pt_02205/Analysis/Preprocessing/qa/available_*.txt

ls -d /data/pt_02205/freesurfer/*_bl.long.*/ >> /data/pt_02205/Analysis/Preprocessing/qa/available_bl.txt
ls -d /data/pt_02205/freesurfer/*_fu.long.*/ >> /data/pt_02205/Analysis/Preprocessing/qa/available_fu.txt
ls /data/pt_02205/preprocessed/T18/diffusion/dti/*/dtifit__FA.nii.gz >> /data/pt_02205/Analysis/Preprocessing/qa/available_fu_dwi.txt
ls /data/pt_02205/preprocessed/T0/diffusion/dti/*/dtifit__FA.nii.gz >> /data/pt_02205/Analysis/Preprocessing/qa/available_bl_dwi.txt
