# Diffusion MRI preprocessing pipeline for Agewell.de-MRI

+ denoise with MRTrix: dwidenoise tool

+ field distortion correction with FSL: topup

	- In the file of *acqparams_dwi.txt*, Total readout time (FSL) = (number of echoes - 1) * echo spacing = (64-1)x0.95ms=0.05985 ms. The reason of number of echoes needed to be devided by two is because of acceleration factor 2.
	BW in PE= 16.446999999999999 Hz/pix (DICOM-tag: (0019,1028)
		- Pix in PE= 128, u.a. DICOM-tag: (0051,100b)
		- dwelltime (echo spacing) = 1/(16.45*128)=0.475ms (effective echo spacing) (would need to be multiplied with reconstructed number of PE steps =128 -1)
	        - dwell time from protocol (0.95 ms) * actual number of PE steps (64) -1

+ motion correction and outliner replacement (FSL: eddy)
	- In the file *distor_correct.py*, the setting in *eddy.inputs.num_threads* must be smaller than the global setting (8 as default now), without defining a value here would cause the program only using one cpu, need to change it manually before running the script

+ tensor model fitting (FSL: dtifit)

+ use bbregister from FREESURFER to register T1 and FA for ROI analysis
