# Preprocessing pipelines for the DIRECT-PLUS study

Using [nipype](https://github.com/beOn/hcpre) to implement structural and functional preprocessing for the DIRECT-PLUS study. Code is shared on [github](https://github.com/fBeyer89/DIRECT_PLUS).

## Overview workflows
All workflows rely on the same modules in folders `structural` and `diffusion`. Yet, the input is differently generated depending on timepoint and state of input data.
See summary of subjects and preprocessing types in `/data/p_02205/sample_description/participants_overview.csv`.

**Workflow for default baseline subjects**
`run_workflow.py` runs the workflow defined in `workflow_nonhcp.py`.
This workflow is for default subjects with DWI files as DICOM and anatomical images called *T1_3D_TFE_SENSE*.nii

**Workflow for baseline subjects with different anatomical image namings**
 `run_workflow.py` runs the workflow defined in `workflow_nonhcp_DBIEX.py`.
  In these subjects DWI files are present as DICOM and anatomical image are called *DBIEX_4_1.nii* or *DBIEX_3_1.nii*.
  In the table `/data/p_02205/sample_description/participants_overview.csv` these participants are labelled with the respective T1 sequence name.
  For subject s242, the readout of the total readout time was changed in `workflow_nonhcp_DBIEX.py` ll. 69-72.

**Workflow for default followup subjects**
  `run_workflow_followup.py` runs the workflow defined in `workflow_nonhcp.py`.
   Default subjects if DWI files are present as DICOM and anatomical image is called *T1_3D_TFE_SENSE*.nii

**Workflow for faulty baseline and followup subjects**
   `run_workflow_corrected_subjects.py` runs the workflow defined in `workflow_nonhcp_corrected_subjects.py`.
    Faulty subjects which had incomplete data and were re-sent by Alon are processed with this script. Here, DWI files and anatomical image are read directly from NIFTI files. Here, total readout time has to be specified manually as it can not be extracted from the DICOM files.
    In the table `/data/p_02205/sample_description/participants_overview.csv` these participants are labelled with  **rerun with corrected subjects workflow**.

## The workflow uses software packages:
MRICRON AFNI --version '19.1.05' ANTSENV --version '2.3.1' FSL --version '6.0.1' FREESURFER --version '6.0.0p1'

Uses python 2.7.15 with packages: (conda environment can be built from agewell_env.2.yml)

| package | version |
| ------- | -------|
|bids-validator|1.2.3|
|nibabel|2.2.0|
|nipy|0.4.1|
|nipype|1.2.0|
|nitime|0.7|
|pandas|0.23.4|
|pydicom|1.2.2|
|python|2.7.15|
|nilearn|0.5.2|                     
|niworkflows|0.8.0|                
|numpy|1.13.1|              
|pydicom|1.2.2|                
|scikit-image|0.14.2|    
|scikit-learn|0.19.0|       
|scipy|0.19.1|     
|seaborn|0.7.1|


working directory is defined in "run_workflow_*.py" files.

#### Preprocessing steps and outputs:

##### Anatomical, T1-weighted anatomical imaging:

- **input**: raw image `*T1_3D_TFE_SENSE*.nii` (= `*DBIEX_3/4_1*.nii` in some participants). Its resolution is 240x240x150 mm3. Other T1w files in subject folders have different resolutions and are not suitable for Freesurfer.
+ **Structural preprocessing** wrapped in `structural/structural.py`:  Freesurfer v.6.0.0rc1 + registration to MNI152 1mm space (ANTS)
- **outputs**:
  - **Freesurfer output** in /data/pt_02205/Data/freesurfer.
  - **Registration output** in /data/pt_02205/Data/preprocessed/T*/structural:

    * /X/T1_brain_mask.nii.gz (brainmask.mgz as nifti)
    * /X/T1.nii.gz (T1.mgz (before skullstrip) as nifti)
    * /X/brain.nii.gz (brain.mgz as nifti, input of the transform)

##### Diffusion-weighted imaging

- **input**: raw DICOMS or converted NIFTIS `*DWI_high_iso*`. DWI imaging was done with 32 directions and only one B0 at the beginning of the scan, no ap/pa acquisition.
- **Diffusion MRI preprocessing** wrapped in `diffusion\diffusion.py`.

    Preprocessing steps are:
    0. DCM2nii to convert Philips DICOM data to nifti, unfortunately DCM2niix does [not work](https://github.com/rordenlab/dcm2niix/tree/master/Philips). Conversion from Philips scanner has the special issue that the regular conversion creates a DWI series with ADC as additional volume (so in our case N=34). This volume has to be discarded for analysis (resulting in a N=33 volumes DWI with one B0 and 32 directions). MRICRON creates a DWI file `/x*DTIhighiso*.nii` without the additional ADC image.
    1. artefacts correction including denoising (MRTrix: dwidenoise)
    2. removal of Gibbs ringing artifacts (MRDegibbs)
    3. calculate total readout time from WaterFatShift parameter in [DICOM header](https://github.com/poldracklab/fmriprep/blob/260872273a1f4ef02de2cae20dd7d6948b531c4b/fmriprep/interfaces/fmap.py#L328).         

    Total readout time = WaterFatShift / (wfs_hz ) = taken from DICOM header /(434.21).

    Before March 2017 TRT=0.053s, then scanner software update, TRT changed to 0.0415s. See also WaterFatShift information in `Sample_characteristics.csv`.
    4.
      - first: Eddy motion correction, outlier replacement (FSL: eddy)
      - second (final): Eddy motion correction, outlier replacement, slice2vol (FSL: eddy_cuda with bash-script)
    5. tensor model fitting (FSL: dtifit)
    6. register FA maps to crosssectional T1 using bbregister.

- **outputs** in /data/pt_02205/Data/preprocessed/T*/diffusion:

    * `/X/*DTIhighiso*denoised_unringed_roi_brain.nii.gz` (denoised, unringed, skullstripped brain)  
    * `/X/*DTIhighiso*denoised_unringed_roi_brain_mask.nii.gz` (denoised, unringed, skullstripped brain mask)      
    * `/X/*DTIhighiso*denoised_unringed.nii.gz` (denoised + unringed DWI)
    * `/X/*DTIhighiso*denoised.nii.gz` (denoised DWI)

    * dti
       * `/X/fa2anat.mat` (bbregister FA to anat reg matrix)
       * `/X/fa2anat.dat` (bbregister FA to anat reg matrix)
       * `/X/fa2anat_bbreg.nii.gz` (bbregister FA to anat reg result)
       * `/X/dtifit__V3.nii.gz`
       * `/X/dtifit__MD.nii.gz` (MD map in individual's anatomical space)
       * `/X/dtifit__L3.nii.gz`
       * `/X/dtifit__L2.nii.gz`
       * `/X/dtifit__L1.nii.gz`
       * `/X/dtifit__V2.nii.gz`
       * `/X/dtifit__V1.nii.gz  `
       * `/X/dtifit__FA.nii.gz  (FA map in individual's anatomical space)`
    * eddy
       * `/X/eddy_corrected.eddy_residuals.nii.gz` (eddy residuals)
       * `/X/eddy_corrected.eddy_cnr_maps.nii.gz` (CNR maps from eddy)
       * `/X/eddy_corrected.eddy_movement_rms` (movement params)
       * `/X/eddy_corrected.nii.gz` (eddy result)
       * `/X/eddy_corrected.eddy_rotated_bvecs` (rotated bvecs)
       * `/X/eddy_corrected.eddy_outlier_report`
       * `/X/eddy_corrected.eddy_post_eddy_shell_alignment_parameters`




## History of preprocessing of Direct-PLUS study

**DWI**:
- extensive quality control and combination with FS control, final version located in `/data/pt_02205/Analysis/Preprocessing/qa/QA_final_with_manual_edits.csv`
- re-run with `eddycuda9.1` in a bash script to implement slice2vol correction and remove stripy pattern due to head motion (November 2020) -> yields final data
- changed total acquisition time from manual input to automatic calculation (June/Juli 2019)
- changed extraction of sequence parameter from taking IM0001 (hard coded) to taking the first DICOM with dwiSE in description (in workflow_nonhcp.py)
- changed DICOM selection to use only scan with x in the beginning (as this is the correct DWI file (without ADC volume) created by dcm2nii, and this operation excludes falsely using non-DWI images that may be present in the DICOM folder into the analysis)
- missing/faulty DICOM were sent again by Alon in Sep-Oct19 (see `/data/p_02205/participants_sep19/`). `T0/T18` contain those subjects where the correction was successful. `still_issues` contains the data sent by Alon for subjects where still some files (such as B0) are missing or corrupt. For those who were sucessfully sent, the DICOMs were converted into NIFTIs separately using dcm2niix and copied directly into the original folders in `/data/p_02205/TIME*/X/brain`. Then, the `run_workflow_corrected_subjects.py` was used to process these participants.

**anatomical**:
- adapted workflow for participants where anatomical image was called DBIEX_3/4_1.nii instead of *T1_3D_TFE_SENSE*.nii (in workflow_nonhcp_DBIEX.py)
- added a script to transform .PAR/.REC files into niftis (at T18, anatomical images were often saved like this).
