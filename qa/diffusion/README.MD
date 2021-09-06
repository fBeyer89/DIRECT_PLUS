# DWI QA for DIRECT PLUS

## SQUAD

EDDY DWI QA is based on [eddyqc](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddyqc/UsersGuide).

1. QUAD = single-subject QA

The script `run_eddyqc_subject.sh` creates individual EDDY QA pdfs and summary file `qc.json` in `/data/pt_02205/preprocessed/*/diffusion/eddy/*/eddy_corrected.qc`

2. SQUAD = group-level QA

This script `run_eddyqc_group` creates group-level EDDY QA pdf and overview over data quality in `squad` folder based on `eddy_squad_list.txt`.

## VISUAL

Results of visual inspection (note everything which could alter FA/MD values, like large ventricles, artifacts, registration errors) in `Visual_Check_TBSS_HC_MD.csv`

1. column *visual_qa_tbss_bl*: Inspection of raw FA images from baseline assessment (N=293) `slicesdir_crosssectional`

2. column *visual_qa_tbss_fu*: Inspection of base raw FA images from longitudinal TBSS (N=224) `slicesdir_longitudinal`

3. column *DTI_anat_coreg_bl*: Inspection of baseline/T0 coregistraiton of anatomical to DWI `
`slicesdir_DWI_anat_coreg/`

4. column *DTI_anat_coreg_fu*: Inspection of followup/T18 coregistraiton of anatomical to DWI `
`slicesdir_DWI_anat_coreg/`

Results of visual inspection in FreeView (after some issues were noticed with slicesdir)
`Visual_Check_Freeview.csv` with columns `Visual_Comment_FreeSurfer` & `Exclude`

*October 2020*
During visual inspection, motion artifacts (zig-zag pattern) were noticed in many participants. These may be partially resolved by using the newest eddy's slicetovolume correction.
Rerun this for all participants, and exclude only those who still show zig-zag pattern in FA images, registration or other gross artifacts.
