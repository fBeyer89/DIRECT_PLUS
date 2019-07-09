##history of preprocessing of Agewell.de-MRI data

september 2018: first participant was preprocessed

**DWI**: - included denoising, gibbs ringing, distortion correction, eddy, dtifit
	 - EDDY is run with --repol but without slice-to-volume correction (even if multiband data).
	 
**anatomical**: - using CBStools for difficult skull-stripping on MP2RAGE
		- Freesurfer v. 6.0.0p1 because it is latest development, and enables better hippocampus segmentation.

**functional**: - minimal standard preprocessing.

21.05.2019: 

**DWI**
	- removed gibbs ringing correction because no ringing was present (raw-data filter at scanner switched on)
	- changed DWI total acquisition time from 0.0603ms to 0.05985ms (128/2-1)*0.95 ms (compatible with LIFE-FU)
	- changed EDDY output to return all files in datasink (to run EDDY quad, for the moment with bash-script)
	- edited option dontpeas==TRUE because of dispersed B0 acquisition, and single-shell data no further interpolation is needed.
	- kept slice-to-volume correction off because in N~20 participants, even with higher head motion, no zebra/zig-zag artifact was observed.
**functional**
        - changed output parameters of resting-workflow to also save EPI-brainmask, motion coregistered volume, stddev-file from dvars calculation.

- rerun everybody with these new features.
