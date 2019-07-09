 ##copy ADI data structure into BIDS   



for subj in ADI009 #ADI003 ADI006 ADI014 ADI016 ADI020 ADI025 ADI029 ADI036 ADI041 ADI045 ADI046 ADI047 ADI048 ADI049 ADI050 ADI053 ADI061 ADI062 ADI063 ADI064 ADI068 ADI069 ADI072 ADI082 ADI087 ADI088 ADI091 ADI093 ADI095 ADI097 ADI102 ADI107 ADI111 ADI116 ADI124 ADI139 ADI140
do

mkdir -p /data/p_02161/BIDS/sub-${subj}/ses-bl/func 
mkdir -p /data/p_02161/BIDS/sub-${subj}/ses-bl/anat
mkdir -p /data/p_02161/BIDS/sub-${subj}/ses-bl/fmap
mkdir -p /data/p_02161/BIDS/sub-${subj}/ses-fu/anat
mkdir -p /data/p_02161/BIDS/sub-${subj}/ses-fu/func
mkdir -p /data/p_02161/BIDS/sub-${subj}/ses-fu/fmap
mkdir -p /data/p_02161/BIDS/sub-${subj}/ses-fu2/anat
mkdir -p /data/p_02161/BIDS/sub-${subj}/ses-fu2/func
mkdir -p /data/p_02161/BIDS/sub-${subj}/ses-fu2/fmap

echo $subj "bl" "fu" "fu2" >> summary_rs.txt
echo $subj >> summary_rs.txt

shopt -s nullglob

##for functional imaging..
#for baseline
set -- /data/p_02161/ADI_studie/Adipositas_BL/${subj}*/*BOLD_resting_state*/*.nii 

echo "$1"
echo "$2"

if [ ! "$2" ];
then 
echo "no second acquisition"
    if [ ! "$1" ];
    then 
    echo "no acquisition"
    echo 0 >> summary_rs.txt
    else
    echo 1 >> summary_rs.txt
    cp  "$1" /data/p_02161/BIDS/sub-${subj}/ses-bl/func/sub-${subj}_ses-bl_task-rest_bold.nii
    cp /data/p_02161/scripts/raw_task_ses-bl_rest_bold.json /data/p_02161/BIDS/sub-${subj}/ses-bl/func/sub-${subj}_ses-bl_task-rest_bold.json
    fi
else 
echo 2 >> summary_rs.txt
cp  "$2" /data/p_02161/BIDS/sub-${subj}/ses-bl/func/sub-${subj}_ses-bl_task-rest_run­-2_bold.nii
cp  "$1" /data/p_02161/BIDS/sub-${subj}/ses-bl/func/sub-${subj}_ses-bl_task-rest_run­-1_bold.nii
cp /data/p_02161/scripts/raw_task_ses-bl_rest_bold.json /data/p_02161/BIDS/sub-${subj}/ses-bl/func/sub-${subj}_ses-bl_task-rest_bold.json
fi

#for followup

set -- /data/p_02161/ADI_studie/Adipositas_FU/${subj}*/*BOLD_resting_state*/*.nii

echo "$1"
echo "$2"

if [ ! "$2" ];
then 
echo "no second acquisition"
    if [ ! "$1" ];
    then 
    echo "no acquisition"
    echo 0 >> summary_rs.txt
    else
    echo 1 >> summary_rs.txt
    cp  "$1" /data/p_02161/BIDS/sub-${subj}/ses-fu/func/sub-${subj}_ses-fu_task-rest_bold.nii
    cp /data/p_02161/scripts/raw_task_ses-fu_rest_bold.json /data/p_02161/BIDS/sub-${subj}/ses-fu/func/sub-${subj}_ses-fu_task-rest_bold.json
    

    fi
else 
echo 2 >> summary_rs.txt
cp  "$2" /data/p_02161/BIDS/sub-${subj}/ses-fu/func/sub-${subj}_ses-fu_task-rest_run­-2_bold.nii
cp  "$1" /data/p_02161/BIDS/sub-${subj}/ses-fu/func/sub-${subj}_ses-fu_task-rest_run­-1_bold.nii
cp /data/p_02161/scripts/raw_task_ses-fu_rest_bold.json /data/p_02161/BIDS/sub-${subj}/ses-fu/func/sub-${subj}_ses-fu_task-rest_bold.json
fi


#for followup2

set -- /data/p_02161/ADI_studie/Adipositas_FU2/${subj}*/*BOLD_resting_state*/*.nii

echo "$1"
echo "$2"

if [ ! "$2" ];
then 
echo "no second acquisition"
    if [ ! "$1" ];
    then 
    echo "no acquisition"
    echo 0 >> summary_rs.txt
    else
    echo 1 >> summary_rs.txt
    cp  "$1" /data/p_02161/BIDS/sub-${subj}/ses-fu2/func/sub-${subj}_ses-fu2_task-rest_bold.nii
    cp /data/p_02161/scripts/raw_task_ses-fu_rest_bold.json /data/p_02161/BIDS/sub-${subj}/ses-fu2/func/sub-${subj}_ses-fu2_task-rest_bold.json
    fi
else 
echo 2 >> summary_rs.txt
cp  "$2" /data/p_02161/BIDS/sub-${subj}/ses-fu2/func/sub-${subj}_ses-fu2_task-rest_run­-2_bold.nii
cp  "$1" /data/p_02161/BIDS/sub-${subj}/ses-fu2/func/sub-${subj}_ses-fu2_task-rest_run­-1_bold.nii
cp /data/p_02161/scripts/raw_task_ses-fu_rest_bold.json /data/p_02161/BIDS/sub-${subj}/ses-fu2/func/sub-${subj}_ses-fu2_task-rest_bold.json
fi

##fieldmaps
set -- /data/p_02161/ADI_studie/Adipositas_BL/${subj}*/*_BOLD_FieldMapping_*

if [ $1 ];
then
cp  $2/*.nii /data/p_02161/BIDS/sub-${subj}/ses-bl/fmap/sub-${subj}_ses-bl_phasediff.nii
cd /data/p_02161/BIDS/sub-${subj}/ses-bl/fmap/
fslsplit $1/*.nii split
cp  split0000.nii.gz /data/p_02161/BIDS/sub-${subj}/ses-bl/fmap/sub-${subj}_ses-bl_magnitude1.nii.gz
cp  split0001.nii.gz /data/p_02161/BIDS/sub-${subj}/ses-bl/fmap/sub-${subj}_ses-bl_magnitude2.nii.gz
rm -rf split000*.nii.gz
cd /data/p_02161/scripts
echo 1 >> summary_rs.txt
cp /data/p_02161/scripts/raw_phasediff_bl.json /data/p_02161/BIDS/sub-${subj}/ses-bl/fmap/sub-${subj}_ses-bl_phasediff.json
echo 1 >> summary_rs.txt
else
echo "no fieldmap acquired"
echo 0 >> summary_rs.txt
fi

set -- /data/p_02161/ADI_studie/Adipositas_FU/${subj}*/*_BOLD_FieldMapping_*
if [ $1 ];
then
cp  $2/*.nii /data/p_02161/BIDS/sub-${subj}/ses-fu/fmap/sub-${subj}_ses-fu_phasediff.nii
cd /data/p_02161/BIDS/sub-${subj}/ses-fu/fmap/
fslsplit $1/*.nii split
cp  split0000.nii.gz /data/p_02161/BIDS/sub-${subj}/ses-fu/fmap/sub-${subj}_ses-fu_magnitude1.nii.gz
cp  split0001.nii.gz /data/p_02161/BIDS/sub-${subj}/ses-fu/fmap/sub-${subj}_ses-fu_magnitude2.nii.gz
cp /data/p_02161/scripts/raw_phasediff_fu.json /data/p_02161/BIDS/sub-${subj}/ses-fu/fmap/sub-${subj}_ses-fu_phasediff.json
rm -rf split000*.nii.gz
cd /data/p_02161/scripts
echo 1 >> summary_rs.txt
else
echo "no fieldmap acquired"
echo 0 >> summary_rs.txt
fi



set -- /data/p_02161/ADI_studie/Adipositas_FU2/${subj}*/*_BOLD_FieldMapping_*
if [ $1 ];
then
cp  $2/*.nii /data/p_02161/BIDS/sub-${subj}/ses-fu2/fmap/sub-${subj}_ses-fu2_phasediff.nii
cd /data/p_02161/BIDS/sub-${subj}/ses-fu2/fmap/
fslsplit $1/*.nii split
cp  split0000.nii.gz /data/p_02161/BIDS/sub-${subj}/ses-fu2/fmap/sub-${subj}_ses-fu2_magnitude1.nii.gz
cp  split0001.nii.gz /data/p_02161/BIDS/sub-${subj}/ses-fu2/fmap/sub-${subj}_ses-fu2_magnitude2.nii.gz
cp /data/p_02161/scripts/raw_phasediff_fu2.json /data/p_02161/BIDS/sub-${subj}/ses-fu2/fmap/sub-${subj}_ses-fu2_phasediff.json
rm -rf split000*.nii.gz
cd /data/p_02161/scripts
echo 1 >> summary_rs.txt
else
echo "no fieldmap acquired"
echo 0 >> summary_rs.txt
fi



#for anatomical imaging
set -- /data/p_02161/ADI_studie/Adipositas_BL/*/*T1*Head-Brain*/
if [ $1 ];
then
cp  $1/*.nii /data/p_02161/BIDS/sub-${subj}/ses-bl/anat/sub-${subj}_ses-bl_T1w.nii
echo 1 >> summary_rs.txt
else
echo "no anatomical scan acquired"
echo 0 >> summary_rs.txt
fi

set -- /data/p_02161/ADI_studie/Adipositas_FU/*/*T1*Head-Brain*/
if [ $1 ];
then
cp  $1/*.nii /data/p_02161/BIDS/sub-${subj}/ses-fu/anat/sub-${subj}_ses-fu_T1w.nii
echo 1 >> summary_rs.txt
else
echo "no anatomical scan acquired"
echo 0 >> summary_rs.txt
fi

set -- /data/p_02161/ADI_studie/Adipositas_FU2/*/*T1*Head-Brain*/
if [ $1 ];
then
cp  $1/*.nii /data/p_02161/BIDS/sub-${subj}/ses-fu2/anat/sub-${subj}_ses-fu2_T1w.nii
echo 1 >> summary_rs.txt
else
echo "no anatomical scan acquired"
echo 0 >> summary_rs.txt
fi
done
