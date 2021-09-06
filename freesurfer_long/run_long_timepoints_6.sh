#!/bin/bash

SUBJECTS_DIR="/data/pt_02205/freesurfer/"   

for subj in s63 s299 s153 s66 s154 s155 s67 s70 s72 s29

#running
#s257 s29 s258 s130 s259 s31 s260 s131 s261 s34 s262 s132 s263 s35 s36 s264 s265 s133 s37 s266 s267 s134 s38 s268 s269 s135 s39 s271 s136 s272 s41 s273 s139 s274 s44 s142 s275 s277 s46 s143 s48 s280 s281 s49 s144 s282 s283 s50 s145 s284 s285 s54 s146 s289 s290 s55 s148 s293 s294 s296 s56 s149 s150 s295 s297 s58 s59 s60 s61 s151 s298 s62 s152 s63 s299 s153 s66 s154 s155 s67 s70 s72

#s210 s104 s211 s4 s212 s213 s105 s5 s6 s214 s215 s106 s7 s107 s216 s217 s9 s218 s108 s219 s10 s109 s220 s221 s11 s110 s222 s224 s12 s111 s225 s13 s226 s227 s14 s112 s228 s15 s113 s229 s230 s114 s16 s231 s232 s115 s17 s234 s235 s116 s236 s19 s237 s117 s238 s239 s20 s118 s240 s241 s21 s242 s119 s243 s22 s244 s121 s246 s247 s23 s122 s248 s249 s24 s124 s250 s125 s251 s252 s126 s253 s27 s254 s127 

#running slowly s210, s257
#rerun template s104

#for later: s73 s74 s75 s76 s210 s128

do

if [ -d ${SUBJECTS_DIR}/${subj}_bl -a -d ${SUBJECTS_DIR}/${subj}_fu ];
then
echo "two timepoints bl+fu"

recon-all -long ${subj}_fu ${subj} -all -openmp 64
recon-all -long ${subj}_bl ${subj} -all -openmp 64

elif [ -d ${SUBJECTS_DIR}/${subj}_bl ];
then
echo "only bl"

recon-all -long ${subj}_bl ${subj} -all -openmp 64

else 
echo "nothing for this subj at all"

fi

done
