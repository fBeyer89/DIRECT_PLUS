# DIRECT_PLUS
Effects of a mediterranean diet (GREEN-MED) on brain structure

These scripts are for preprocessing and analysing data from the DIRECT-PLUS trial (in cooperation with Prof. Irish Shai and Alon Kaplan)

For further information on the study see:
https://www.clinicaltrials.gov/ct2/show/record/NCT03020186?term=iris+shai&rank=1
or ClinicalTrials.gov Identifier: NCT03020186


#during copying
/media/fbeyer/SP PHD U3/Data/TIME18/22/brain/DICOM/IM_1246', as it was replaced while being copied
cp: skipping file '/media/fbeyer/SP PHD U3/Data/TIME18/22/brain/DICOM/IM_1253', as it was replaced while being copied
cp: skipping file '/media/fbeyer/SP PHD U3/Data/TIME18/220/brain/DICOM/IM_0394', as it was replaced while being copied
cp: skipping file '/media/fbeyer/SP PHD U3/Data/TIME18/220/brain/DICOM/IM_1928', as it was replaced while being copied
cp: skipping file '/media/fbeyer/SP PHD U3/Data/TIME18/284/brain/DICOM/IM_0915', as it was replaced while being copied
cp: skipping file '/media/fbeyer/SP PHD U3/Data/TIME18/284/brain/DICOM/IM_0916', as it was replaced while being copied
cp: skipping file '/media/fbeyer/SP PHD U3/Data/TIME18/284/brain/DICOM/IM_1075', as it was replaced while being copied


##Anatomical preprocessing (T1-weighted FFE)

- use raw image "*T1_3D_TFE_SENSE*.nii" (is called DBIEX_4_1.nii for some participants)
    (resolution is 240x240x150 mm3 (other versions of T1w seem reconstructed and therefore not suitable for Freesurfer)
- run Freesurfer version 6.0.0p1 to extract hippocampal subfields


##DWI preprocessing (32 directions, only one B0 at the beginning of the scan, no ap/pa acquisition)

- use DCM2nii to convert Philips DICOM data to nifti, unfortunately DCM2niix does not work (see: https://github.com/rordenlab/dcm2niix/tree/master/Philips)
- use series with prefix "x" as this represents raw images (https://www.nitrc.org/forum/forum.php?set=custom&forum_id=4703&style=flat&max_rows=50)
- MRTRX denoise
- check for gibbs ringing (necessary??)
- don't perform fieldmap correction as there is none
- derive acquisition parameters from header:
  according to: https://github.com/poldracklab/fmriprep/blob/260872273a1f4ef02de2cae20dd7d6948b531c4b/fmriprep/interfaces/fmap.py#L328
  Total readout time = WaterFatShift / (wfs_hz ) = 23.0209541/(434.21) = 0.05302 s
- run eddy with replacement of outliers, but without intra-volume motion correction
- run DTI model and fit
- register to crosssectional T1
