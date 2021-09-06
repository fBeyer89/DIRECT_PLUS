#!/bin/bash


#run eddy qc for DIRECT PLUS (needs FSL version > 6.0)
slist=`ls -d /data/pt_02205/preprocessed/T0/diffusion/eddy/*/ | cut -f8 -d"/"`

for subj in ${slist}
do
echo ${subj}

for tp in T0 T18
do

if [ ${tp} == "T0" ];
then 
echo "tp 0"

if [ ! -d /data/pt_02205/preprocessed/${tp}/diffusion/eddy/${subj}/eddy_corrected.qc ];
then
mask=`ls /data/pt_02205/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/bet/*denoised_unringed_roi_brain_mask.nii.gz`
bvals=`ls /data/pt_02205/wd/direct_preproc/_subject_${subj}/dicom_convert/*.bval`
acqparams=`/data/pt_02205/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/mk_acq/acqparams_dwi.txt`

if [ $subj == "s67" ] || [ $subj == "s89" ] || [ $subj == "s48" ] || [ $subj == 's278' ] || [ $subj == 's333' ];
then 
echo "new bvals"
bvals=`ls /data/p_02205/TIME0/${subj}/brain/*.bval`
acqparams=/data/pt_02205/wd/direct_preproc/dwi_preproc/distor_correct/mk_acq/acqparams_dwi.txt
fi

eddy_quad /data/pt_02205/preprocessed/T0/diffusion/eddy/${subj}/eddy_corrected --eddyIdx /data/pt_02205/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/mk_index/index.txt --eddyParams ${acqparams} --mask ${mask} --bvals ${bvals}
fi

else 
echo "QC baseline was done already"
fi


if [ ${tp} == "T18" ];
then 

echo "tp 18"

if [ ! -d /data/pt_02205/preprocessed/${tp}/diffusion/eddy/${subj}/eddy_corrected.qc ] && [ -d /data/pt_02205/preprocessed/${tp}/diffusion/eddy/${subj}/ ];
then
mask=`ls /data/pt_02205/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/bet/*denoised_unringed_roi_brain_mask.nii.gz`
acqparams=/data/pt_02205/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/mk_acq/acqparams_dwi.txt
bvals=`ls /data/pt_02205/wd/T18/direct_preproc/_subject_${subj}/dicom_convert/*.bval`

if [ $subj == "s59" ] ||[ $subj == "s70" ] || [ $subj == "s98" ] || [ $subj == "s299" ] || [ $subj == "s342" ] || [ $subj == 's284' ] || [ $subj == 's142' ] || [ $subj == 's104' ];
then 
bvals=`ls /data/p_02205/TIME18/${subj}/brain/*.bval`
acqparams=/data/pt_02205/wd/T18/direct_preproc/dwi_preproc/distor_correct/mk_acq/acqparams_dwi.txt
fi

eddy_quad /data/pt_02205/preprocessed/T18/diffusion/eddy/${subj}/eddy_corrected --eddyIdx /data/pt_02205/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/mk_index/index.txt --eddyParams ${acqparams} --mask ${mask} --bvals ${bvals}

else 
echo "QC followup was done already or no followup acquired"
fi

fi

done



done


# Usage: eddy_quad <eddyBase> -idx <eddyIndex> -par <eddyParams> -m <mask> -b <bvals> [options]
#    
#    
# Compulsory arguments:
#        eddyBase             Basename (including path) specified when running EDDY
#        -idx, --eddyIdx      File containing indices for all volumes into acquisition parameters
#        -par, --eddyParams   File containing acquisition parameters
#        -m, --mask           Binary mask file
#        -b, --bvals          b-values file
#    
# Optional arguments:
#        -g, --bvecs          b-vectors file - only used when <eddyBase>.eddy_residuals file is present
#        -o, --output-dir     Output directory - default = '<eddyBase>.qc' 
#        -f, --field          TOPUP estimated field (in Hz)
#        -s, --slspec         Text file specifying slice/group acquisition
#        -v, --verbose        Display debug messages
# 
# 
# 
# eddy_quad /data/pt_life/LIFE_fu/wd_preprocessing/redo_eddy/hcp_prep_workflow/dwi_preproc/distor_correct/_subject_LI0026893X/eddy/eddy_corrected -idx /home/raid1/fbeyer/Documents/Scripts/LIFE_followup/preprocessing/nipy1.4/diffusion/index.txt -par /home/raid1/fbeyer/Documents/Scripts/LIFE_followup/preprocessing/nipy1.4/diffusion/acqparams_dwi.txt -m /data/pt_life/LIFE_fu/wd_preprocessing/redo_eddy/hcp_prep_workflow/dwi_preproc/distor_correct/_subject_LI0026893X/bet/dwi_appa_corrected_maths_brain_mask.nii.gz -b /data/pt_life/LIFE_fu/wd_preprocessing/redo_eddy/hcp_prep_workflow/_subject_LI0026893X/dicom_convert/cmrrmbep2ddiffs009a001.bval --bvecs /data/pt_life/LIFE_fu/wd_preprocessing/redo_eddy/hcp_prep_workflow/_subject_LI0026893X/dicom_convert/cmrrmbep2ddiffs009a001.bvec -f /data/pt_life/LIFE_fu/wd_preprocessing/redo_eddy/hcp_prep_workflow/dwi_preproc/distor_correct/_subject_LI0026893X/topup/dwi_appa_field.nii.gz
# 
# 
# works:
# eddy_quad /data/pt_life_dti_followup/diffusion/LI0026893X/eddy_corrected --eddyIdx /home/raid1/fbeyer/Documents/Scripts/LIFE_followup/preprocessing/nipy1.4/diffusion/index.txt --eddyParams /home/raid1/fbeyer/Documents/Scripts/LIFE_followup/preprocessing/nipy1.4/diffusion/acqparams_dwi.txt --mask /data/pt_life_dti_followup/diffusion/LI0026893X/dwi_appa_corrected_maths_brain_mask.nii.gz --bvals /data/pt_life_dti_followup/diffusion/LI0026893X/cmrrmbep2ddiffs009a001.bval
# 
# doesnt work
# eddy_quad /data/pt_life_dti_followup/diffusion/LI0026893X/eddy_corrected --eddyIdx=/home/raid1/fbeyer/Documents/Scripts/LIFE_followup/preprocessing/nipy1.4/diffusion/index.txt --eddyParams=/home/raid1/fbeyer/Documents/Scripts/LIFE_followup/preprocessing/nipy1.4/diffusion/acqparams_dwi.txt --mask=/data/pt_life_dti_followup/diffusion/LI0026893X/dwi_appa_corrected_maths_brain_mask.nii.gz --bvals=/data/pt_life_dti_followup/diffusion/LI0026893X/cmrrmbep2ddiffs009a001.bval
# 
