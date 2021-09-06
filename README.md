# DIRECT_PLUS
Effects of a mediterranean diet (GREEN-MED) on brain structure

These scripts are for preprocessing and analysing data from the DIRECT-PLUS trial (in cooperation with Prof. Irish Shai and Alon Kaplan).

For further information on the study see [ClinicalTrials.gov](https://www.clinicaltrials.gov/ct2/show/record/NCT03020186?term=iris+shai&rank=1)
with Identifier: NCT03020186

For more information, please see `README` inside folders.

# qa
Scripts and Results for quality assessment of FreeSurfer (based of `QoalaFS`) and DWI (based on `eddy_squad`)

# nipy1.4
Nipype workflows to run anatomical and DWI processing for different file naming schemes. `eddy` was first run within the workflow (without slice2vol correction), but for the final version (`eddycuda9.1`) run with bash scripts (see below).

# bash
Mainly contains script to run `eddycuda9.1` for performing slice2vol correction with eddy (`run_eddycuda_forslice2volume.sh`). Also contains other bash scripts for copying data.

# testing
for playing around

# freesurfer_long
Bash scripts for running longitudinal FreeSurfer after the cross-sectional runs have been started by the pipeline.
