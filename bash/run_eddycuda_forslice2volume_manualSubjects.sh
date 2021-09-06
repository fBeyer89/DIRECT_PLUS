#!/bin/bash

#Go to maki server
#Type FSL --version 6.0.1, CUDA --version 9.1, FREESURFER --version 6.0.0

SUBJECTS_DIR="/data/pt_02205/Data/freesurfer"
#This script was implemented to run advanced eddy for all Direct_Plus participants with the "slice2volume" correction option as in October 2020 motion artifacts/zig-zag stripes were noticed.

#Change acquisition params according to date of scan!!
#s48 s67 s89:acqp="/data/pt_02205/Analysis/Preprocessing/bash/acqparams_dwi_0.053.txt 
#s278 s231 s333 s59 s70 s98 s104 s220 s244; /data/pt_02205/Analysis/Preprocessing/bash/acqparams_dwi_0.041.txt

#for s50 FU: /data/pt_02205/Analysis/Preprocessing/bash/slsspec_s50_fu.txt

cd /data/pt_02205/Data/preprocessed/T0/diffusion/

for subj in s333 
do
echo $subj
for tp in T0
do
echo $tp

if [ $tp == "T0" ];
then

acqp="/data/pt_02205/Analysis/Preprocessing/bash/acqparams_dwi_0.041.txt"

#if [ ! -d /data/pt_02205/Data/wd/direct_preproc/_subject_${subj}/dicom_convert/ ];
#then 
bval=`ls /data/p_02205/TIME0/${subj}/brain/*.bval`
#else
#bval=`ls /data/pt_02205/Data/wd/direct_preproc/_subject_${subj}/dicom_convert/*.bval`
#fi




#if [ ! -d /data/pt_02205/Data/wd/direct_preproc/_subject_${subj}/dicom_convert/ ];
#then 
bvec=`ls /data/p_02205/TIME0/${subj}/brain/*.bvec`
#else 
#bvec=`ls /data/pt_02205/Data/wd/direct_preproc/_subject_${subj}/dicom_convert/*.bvec`
#fi

input=`ls /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/unring/*_denoised_unringed.nii*`
mask=`ls /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/bet/*_denoised_unringed_roi_brain_mask.nii.gz`

echo $input
echo $bvec
echo $bval

if [ ! -f /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.nii.gz ]; then
eddy_cuda9.1 --cnr_maps --ff=10.0 --acqp=$acqp --bvals=${bval} --bvecs=${bvec} --imain=${input} --index=/data/pt_02205/Data/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/mk_index/index.txt --mask=${mask} --out=/data/pt_02205/Data/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol --repol --residuals --niter=5 --mporder=4 --s2v_niter=5 --s2v_lambda=1 --s2v_interp=trilinear --slspec=/data/pt_02205/Analysis/Preprocessing/bash/slsspec.txt

#--fwhm=10,0,0,0,0 mporder 6
else

echo "eddy already done"
fi

if [ ! -f /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_FA.nii.gz ];
then 
cd /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/_subject_${subj}/dti/

dtifit -k /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol -o dtifit_slice2vol -m ${mask} -r /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.eddy_rotated_bvecs -b ${bval}
else 
echo "dti done"
fi

if [ ! -f /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/_subject_${subj}/bbregister/fa_slice2vol2anat_bbreg.nii.gz ];
then 
cd /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/_subject_${subj}/bbregister/

bbregister --t1 --init-fsl --fslmat fa_slice2vol2anat.mat --reg fa_slice2vol2anat.dat --o fa_slice2vol2anat_bbreg.nii.gz --mov //data/pt_02205/Data/wd/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_FA.nii.gz --s ${subj}_bl
else
echo "bbregister done"
fi

##Copy the data to the final output
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.eddy_cnr_maps.nii.gz /data/pt_02205/Data/preprocessed/T0/diffusion/eddy/${subj}/eddy_corrected_slicetovol.eddy_cnr_maps.nii.gz
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.eddy_movement_rms /data/pt_02205/Data/preprocessed/T0/diffusion/eddy/${subj}/eddy_corrected_slicetovol.eddy_movement_rms
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.eddy_outlier_report /data/pt_02205/Data/preprocessed/T0/diffusion/eddy/${subj}/eddy_corrected_slicetovol.eddy_outlier_report
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.eddy_parameters /data/pt_02205/Data/preprocessed/T0/diffusion/eddy/${subj}/eddy_corrected_slicetovol.eddy_parameters
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.eddy_post_eddy_shell_alignment_parameters /data/pt_02205/Data/preprocessed/T0/diffusion/eddy/${subj}/eddy_corrected_slicetovol.eddy_post_eddy_shell_alignment_parameters
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.eddy_residuals.nii.gz /data/pt_02205/Data/preprocessed/T0/diffusion/eddy/${subj}/eddy_corrected_slicetovol.eddy_residuals.nii.gz
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.eddy_rotated_bvecs /data/pt_02205/Data/preprocessed/T0/diffusion/eddy/${subj}/eddy_corrected_slicetovol.eddy_rotated_bvecs
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.nii.gz /data/pt_02205/Data/preprocessed/T0/diffusion/eddy/${subj}/eddy_corrected_slicetovol.nii.gz

cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_V3.nii.gz /data/pt_02205/Data/preprocessed/T0/diffusion/dti/${subj}/dtifit_slice2vol_V3.nii.gz
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_V2.nii.gz /data/pt_02205/Data/preprocessed/T0/diffusion/dti/${subj}/dtifit_slice2vol_V2.nii.gz
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_V1.nii.gz /data/pt_02205/Data/preprocessed/T0/diffusion/dti/${subj}/dtifit_slice2vol_V1.nii.gz
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_L3.nii.gz /data/pt_02205/Data/preprocessed/T0/diffusion/dti/${subj}/dtifit_slice2vol_L3.nii.gz
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_L2.nii.gz /data/pt_02205/Data/preprocessed/T0/diffusion/dti/${subj}/dtifit_slice2vol_L2.nii.gz
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_L1.nii.gz /data/pt_02205/Data/preprocessed/T0/diffusion/dti/${subj}/dtifit_slice2vol_L1.nii.gz
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_FA.nii.gz /data/pt_02205/Data/preprocessed/T0/diffusion/dti/${subj}/dtifit_slice2vol_FA.nii.gz
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_MD.nii.gz /data/pt_02205/Data/preprocessed/T0/diffusion/dti/${subj}/dtifit_slice2vol_MD.nii.gz
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/_subject_${subj}/bbregister/fa_slice2vol2anat_bbreg.nii.gz /data/pt_02205/Data/preprocessed/T0/diffusion/dti/${subj}/fa_slice2vol2anat_bbreg.nii.gz
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/_subject_${subj}/bbregister/fa_slice2vol2anat.mat /data/pt_02205/Data/preprocessed/T0/diffusion/dti/${subj}/fa_slice2vol2anat.mat
cp /data/pt_02205/Data/wd/direct_preproc/dwi_preproc/_subject_${subj}/bbregister/fa_slice2vol2anat.dat /data/pt_02205/Data/preprocessed/T0/diffusion/dti/${subj}/fa_slice2vol2anat.dat


else

if [ -f /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected.nii.gz ];
then

acqp="/data/pt_02205/Analysis/Preprocessing/bash/acqparams_dwi_0.041.txt"

#if [ -d /data/pt_02205/Data/wd/T18/direct_preproc/_subject_${subj}/dicom_convert/ ]; then
#echo "directory exists"
#bval=`ls /data/pt_02205/Data/wd/T18/direct_preproc/_subject_${subj}/dicom_convert/*.bval`
#bvec=`ls /data/pt_02205/Data/wd/T18/direct_preproc/_subject_${subj}/dicom_convert/*.bvec`
#else 
bval=`ls /data/p_02205/TIME18/${subj}/brain/*.bval`
bvec=`ls /data/p_02205/TIME18/${subj}/brain/*.bvec`
#fi



input=`ls /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/unring/*_denoised_unringed.nii*`
mask=`ls /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/bet/*_denoised_unringed_roi_brain_mask.nii.gz`

if [ ! -f /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.nii.gz ]; then
eddy_cuda9.1 --cnr_maps --ff=10.0 --acqp=$acqp --bvals=${bval} --bvecs=${bvec} --imain=${input} --index=/data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/mk_index/index.txt --mask=${mask} --out=/data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol --repol --residuals --niter=5 --fwhm=10,0,0,0,0 --mporder=6 --s2v_niter=5 --s2v_lambda=1 --s2v_interp=trilinear --slspec=/data/pt_02205/Analysis/Preprocessing/bash/slsspec.txt
else

echo "eddy already done"
fi

if [ ! -f /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_FA.nii.gz ];
then 
cd /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/_subject_${subj}/dti/

dtifit -k /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol -o dtifit_slice2vol -m ${mask} -r /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.eddy_rotated_bvecs -b ${bval}

else 
echo "dti done"
fi

if [ ! -f /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/_subject_${subj}/bbregister/fa_slice2vol2anat_bbreg.nii.gz ];
then 
cd /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/_subject_${subj}/bbregister/

bbregister --t1 --init-fsl --fslmat fa_slice2vol2anat.mat --reg fa_slice2vol2anat.dat --o fa_slice2vol2anat_bbreg.nii.gz --mov /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_FA.nii.gz --s ${subj}_fu
else
echo "bbregister done"
fi




##Copy the data to the final output
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.eddy_cnr_maps.nii.gz /data/pt_02205/Data/preprocessed/T18/diffusion/eddy/${subj}/ddy_corrected_slicetovol.eddy_cnr_maps.nii.gz
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.eddy_movement_rms /data/pt_02205/Data/preprocessed/T18/diffusion/eddy/${subj}/eddy_corrected_slicetovol.eddy_movement_rms
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.eddy_outlier_report /data/pt_02205/Data/preprocessed/T18/diffusion/eddy/${subj}/eddy_corrected_slicetovol.eddy_outlier_report
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.eddy_parameters /data/pt_02205/Data/preprocessed/T18/diffusion/eddy/${subj}/eddy_corrected_slicetovol.eddy_parameters
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.eddy_post_eddy_shell_alignment_parameters /data/pt_02205/Data/preprocessed/T18/diffusion/eddy/${subj}/eddy_corrected_slicetovol.eddy_post_eddy_shell_alignment_parameters
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.eddy_residuals.nii.gz /data/pt_02205/Data/preprocessed/T18/diffusion/eddy/${subj}/eddy_corrected_slicetovol.eddy_residuals.nii.gz
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.eddy_rotated_bvecs /data/pt_02205/Data/preprocessed/T18/diffusion/eddy/${subj}/eddy_corrected_slicetovol.eddy_rotated_bvecs
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/distor_correct/_subject_${subj}/eddy/eddy_corrected_slicetovol.nii.gz /data/pt_02205/Data/preprocessed/T18/diffusion/eddy/${subj}/eddy_corrected_slicetovol.nii.gz

cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_V3.nii.gz /data/pt_02205/Data/preprocessed/T18/diffusion/dti/${subj}/dtifit_slice2vol_V3.nii.gz
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_V2.nii.gz /data/pt_02205/Data/preprocessed/T18/diffusion/dti/${subj}/dtifit_slice2vol_V2.nii.gz
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_V1.nii.gz /data/pt_02205/Data/preprocessed/T18/diffusion/dti/${subj}/dtifit_slice2vol_V1.nii.gz
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_L3.nii.gz /data/pt_02205/Data/preprocessed/T18/diffusion/dti/${subj}/dtifit_slice2vol_L3.nii.gz
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_L2.nii.gz /data/pt_02205/Data/preprocessed/T18/diffusion/dti/${subj}/dtifit_slice2vol_L2.nii.gz
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_L1.nii.gz /data/pt_02205/Data/preprocessed/T18/diffusion/dti/${subj}/dtifit_slice2vol_L1.nii.gz
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_FA.nii.gz /data/pt_02205/Data/preprocessed/T18/diffusion/dti/${subj}/dtifit_slice2vol_FA.nii.gz
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/_subject_${subj}/dti/dtifit_slice2vol_MD.nii.gz /data/pt_02205/Data/preprocessed/T18/diffusion/dti/${subj}/dtifit_slice2vol_MD.nii.gz
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/_subject_${subj}/bbregister/fa_slice2vol2anat_bbreg.nii.gz /data/pt_02205/Data/preprocessed/T18/diffusion/dti/${subj}/fa_slice2vol2anat_bbreg.nii.gz
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/_subject_${subj}/bbregister/fa_slice2vol2anat.mat /data/pt_02205/Data/preprocessed/T18/diffusion/dti/${subj}/fa_slice2vol2anat.mat
cp /data/pt_02205/Data/wd/T18/direct_preproc/dwi_preproc/_subject_${subj}/bbregister/fa_slice2vol2anat.dat /data/pt_02205/Data/preprocessed/T18/diffusion/dti/${subj}/fa_slice2vol2anat.dat


else

echo "no followup data for this subject"
fi

fi
done
done





