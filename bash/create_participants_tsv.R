bl=read.csv('/data/pt_02161/scripts/bash/BL.txt', sep=' ', header=F)
bl_rs=read.csv('/data/pt_02161/scripts/bash/BL_rs.txt', sep=' ', header=F)
bl_dwi=read.csv('/data/pt_02161/scripts/bash/BL_dwi.txt', sep=' ', header=F)
fu=read.csv('/data/pt_02161/scripts/bash/FU.txt', sep=' ', header=F)
fu_rs=read.csv('/data/pt_02161/scripts/bash/FU_rs.txt', sep=' ', header=F)
fu_dwi=read.csv('/data/pt_02161/scripts/bash/FU_dwi.txt', sep=' ', header=F)
fu2=read.csv('/data/pt_02161/scripts/bash/FU2.txt', sep=' ', header=F)
fu2_rs=read.csv('/data/pt_02161/scripts/bash/FU2_rs.txt', sep=' ', header=F)
fu2_dwi=read.csv('/data/pt_02161/scripts/bash/FU2_dwi.txt', sep=' ', header=F)


participants=data.frame(bl)
colnames(participants)[1]="ID"
colnames(participants)[2]="bl_DICOM"

temp=data.frame(bl_rs)
colnames(temp)[1]="ID"
colnames(temp)[2]="bl_rs"

participants=merge(participants, temp, by="ID",all = T)
nrow(participants)
nrow(temp)

temp=data.frame(bl_dwi)
colnames(temp)[1]="ID"
colnames(temp)[2]="bl_dwi"

participants=merge(participants, temp, by="ID",all = T)
nrow(participants)
nrow(temp)

temp=data.frame(fu)
colnames(temp)[1]="ID"
colnames(temp)[2]="fu_DICOM"

participants=merge(participants, temp, by="ID",all = T)


temp=data.frame(fu_rs)
colnames(temp)[1]="ID"
colnames(temp)[2]="fu_rs"

participants=merge(participants, temp, by="ID",all = T)
nrow(participants)
nrow(temp)

temp=data.frame(fu_dwi)
colnames(temp)[1]="ID"
colnames(temp)[2]="fu_dwi"

participants=merge(participants, temp, by="ID",all = T)
nrow(participants)
nrow(temp)

temp=data.frame(fu2)
colnames(temp)[1]="ID"
colnames(temp)[2]="fu2_DICOM"

participants=merge(participants, temp, by="ID",all = T)
nrow(participants)
nrow(temp)

temp=data.frame(fu2_rs)
colnames(temp)[1]="ID"
colnames(temp)[2]="fu2_rs"

participants=merge(participants, temp, by="ID",all = T)
nrow(participants)
nrow(temp)

temp=data.frame(fu2_dwi)
colnames(temp)[1]="ID"
colnames(temp)[2]="fu2_dwi"

participants=merge(participants, temp, by="ID",all = T)
nrow(participants)
nrow(temp)


#some special cases
participants$comments="none"

participants[participants$ID=="ADI041",]$bl_rs=2
participants[participants$ID=="ADI041",]$comments="two bl rs scans"
participants[participants$ID=="ADI061",]$fu2_dwi=3
participants[participants$ID=="ADI061",]$fu2_rs=2
participants[participants$ID=="ADI061",]$comments="two fu2 rs/three dwi scans"
participants[participants$ID=="ADI088",]$fu2_rs=2
participants[participants$ID=="ADI088",]$comments="two bl rs scans"
participants[participants$ID=="ADI002",]$comments="T1 weighted image non-isotropic"

write.table(participants, "/data/p_02161/BIDS/participants.tsv", row.names = F, sep='\t')


##number of participants with complete resting state data
compl_rs=participants[!is.na(participants$bl_rs)&!is.na(participants$fu_rs)&!is.na(participants$fu2_rs),]
nrow(compl_rs)

compl_dwi=participants[!is.na(participants$bl_dwi)&!is.na(participants$fu_dwi),]
nrow(compl_dwi)
#only 6 participants have complete DTI

compl_dwi=participants[!is.na(participants$fu_dwi)&!is.na(participants$fu2_dwi),]
nrow(compl_dwi)
