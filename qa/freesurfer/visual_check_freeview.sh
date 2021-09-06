#run freesurfer quality checks according to   
SUBJECTS_DIR="/data/pt_02205/Data/freesurfer"  

#Klapwijk: Qoala-T: A supervised-learning tool for quality control of FreeSurfer segmented MRI data  

for subj in s220 s169 s196 s234 s249 s271 s341 s353 s36 s368 s376 s376 s67 s70 s9
#s295 s278 s275 s104 s295 s5 s145 s275 s119 s228 s344 s306 s153 s316 s74 s228 s334 s343 s119 s326 s184 s104 s343 s316 s5 s46 s163 s133 s23 s306 s357 s252 s215 s91 s264 s62 s81 s62 s60 s345 s214 s322 s46 s23 s297 s60 s150 s341 s264 s281 s35 s334 s369 s100 s176 s150 s333 s251 s333 s322 s224 s177 s220 s213 s133 s187 s198 s83 s91 s2 s220 s347 s50 s278 s55 s145 s153 s231 s257 s112 s117 s200 s339 s112 s252 s372 s348 s155 s219 s312 s341 s213 s339 s117 s19 s102 s283 s206 s139 s320 s344 s173 s311 s55 s83 s162 s241 s169 s271 s12 s177 s241 s251 s236 s302  
do 
for tp in bl fu 
do
view="tkmedit ${subj}_${tp}.long.$subj brainmask.mgz -surfs -aux wm.mgz" 
eval $view 
done
done

#run detailed freeview inspection 
#cross 
subj="s104";tp="fu"
freeview ${SUBJECTS_DIR}/${subj}_${tp}/mri/T1.mgz ${SUBJECTS_DIR}/${subj}_${tp}/mri/brainmask.mgz:colormap=heat -f ${SUBJECTS_DIR}/${subj}_${tp}/surf/lh.pial:edgecolor=lightgreen ${SUBJECTS_DIR}/${subj}_${tp}/surf/lh.white:edgecolor=white ${SUBJECTS_DIR}/${subj}_${tp}/surf/rh.pial:edgecolor=lightgreen ${SUBJECTS_DIR}/${subj}_${tp}/surf/rh.white:edgecolor=white  

#run detailed freeview inspection long 

#freeview ${SUBJECTS_DIR}/${subj}_bl.long.${subj}/mri/brainmask.mgz ${SUBJECTS_DIR}/${subj}_fu.long.${subj}/mri/brainmask.mgz -f ${SUBJECTS_DIR}/${subj}_bl.long.${subj}/surf/lh.pial:edgecolor=lightgreen ${SUBJECTS_DIR}/${subj}_bl.long.${subj}/surf/rh.pial:edgecolor=lightgreen ${SUBJECTS_DIR}/${subj}_fu.long.${subj}/surf/lh.pial:edgecolor=white ${SUBJECTS_DIR}/${subj}_fu.long.${subj}/surf/rh.pial:edgecolor=white  
