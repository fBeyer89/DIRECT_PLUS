# Diffusion MRI preprocessing pipeline for DIRECT PLUS

+ denoise with MRTrix 3.0: dwidenoise + MRDegibbs tool

+ motion correction and outliner replacement (FSL 6.0.1: eddy) (and with bash script slice2vol correction -> **final** data version)

+ tensor model fitting (FSL: dtifit)

+ use bbregister from FREESURFER to register T1 and FA for ROI analysis
