# Quality Control for DIRECT PLUS

## data_availability

Text files describing the availability of the data and baseline and followup.

## diffusion

Diffusion QA was based on visual inspection of slicesdir views from FA images during TBSS & HC to MD coregistration.
When significant issues with registration or stripy patterns were noticed, images were further inspected in FSLEYES.

## freesurfer
QoalaT was used to identify issues in FreeSurfer. Here, only the predictions based on the model approach `/data/pt_02205/Analysis/Preprocessing/qa/freesurfer/model_based` were used, and all with QoalaT score between 30 and 40 were manually inspected. When using self-ratings, QoalaT did not perform well `/data/pt_02205/Analysis/Preprocessing/qa/freesurfer/subset_based`.

## QA_final_with_manual_edits.csv
This table summarizes all information about the MRI scan quality.

tp  
subj  
DWIcomment  
DWIdone  
T1comment  
Fsdone  
HC_MD_comment  
Scan_QoalaT  
Recommendation  
manual_QC_adviced  
Visual_Comment_FreeSurfer  
**FS_Exclude**  -> which subjects should be excluded due to wrong FS segmentation   
FS_correction_necessary  
visual_qa_tbss  
DTI_anat_coreg  
Visual_Comment_TBSS_with_anatomy  
**DWI_exclude	DWI_exclude_afterslice2vol**  -> which subjects should be excluded due to bad DWI data quality or wrong data  
cnr  
mean_rms  
max_rms
