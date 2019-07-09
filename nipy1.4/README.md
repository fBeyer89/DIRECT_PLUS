# preproc_ADI

Preprocessing pipelines for the ADI study

+ BIDS format: bring imaging data into BIDS data convention (bids_conversion.py).

+ Structural preprocessing:  Freesurfer v.6.0.0rc1 + registration to MNI152 1mm space (ANTS)

+ Functional (rsfMRI) preprocessing: 
    - removal of first 4 volumes, motion correction (MCFlirt), coregistration to anatomical (BBREGISTER)
      unwarping with fieldmaps in FUGUE, all transforms applied in a single step.
    - smoothing with 6mm FWHM, ICA AROMA to correct for motion artifacts, regression of 5 WM/CSF compcor components and additionally global signal
    - output denoised, smoothed rsfmri timeseries in native space
    
+ Diffusion MRI preprocessing: artefacts correction including denoising (MRTrix: dwidenoise) ; distortion correction based on fieldmaps, used together with motion correction and outliner replacement (FSL: eddy); tensor model fitting (FSL: dtifit)


Based on the implementation of HCP pipelines for nipype (https://github.com/beOn/hcpre)

Using software packages and nipype:
MRICRON AFNI --version '19.1.05' ANTSENV --version '2.3.1' FSL --version '6.0.1' FREESURFER --version '6.0.0p1' 

To run it do:
python run_workflow_hcplike.py --run -n 8 --config conf_for_ADI.conf 

conf_for_ADI.conf: configuration file where only ID of participant (subjects = ['ADIXXX_XX'] should be changed.

working directory is defined in "run_workflow_hcplike.py", ll.76: working_dir="" (don't change, unless directory is full)

