#Load different elements of QA

#GENERAL
overview=read.csv("/data/p_02205/sample_description/participants_overview.csv")
overview_long=reshape(overview[,-c(2,7)], varying = list(c(2,6), 
                                                         c(3,7), c(4,8),
                                                         c(5,9), c(10,11)), 
                      v.names=c("DWIcomment", "DWIdone", "T1comment",
                                "Fsdone", "HC_MD_comment"), 
                      times=c('bl', 'fu'), idvar='Subj.T0', direction='long')
write.csv(overview_long, "/data/p_02205/sample_description/participants_overview_long.csv" )
colnames(overview_long)[1]="subj"
colnames(overview_long)[2]="tp"

#FREESURFER
#load QoalaT data
qoalat=read.csv("/data/pt_02205/Analysis/Preprocessing/qa/freesurfer/outputQoala_T_predictions_model_based_pt_02205.csv")
head(qoalat)
for (i in 1:nrow(qoalat)){
  qoalat[i,"subj"]=strsplit(toString(qoalat[i,"VisitID"]), "_")[[1]][1]
  qoalat[i,"tp"]=strsplit(toString(qoalat[i,"VisitID"]), "_")[[1]][2]
}

overview_qoalat=merge(overview_long, qoalat[,c("subj","tp","Scan_QoalaT","Recommendation",
                                               "manual_QC_adviced")], by=c("subj","tp"))


#DWI:
#VISUAL QA SLICESDIR
visual_qa=read.csv("VISUAL/Visual_Check_TBSS_HC_MD.csv", skip=1)
visual_qa_long=reshape(visual_qa[], varying = list(c(2,3),c(4,5)), 
                       v.names=c("visual_qa_tbss","DTI_anat_coreg"), 
                       times=c('bl', 'fu'), idvar='subj', direction='long')
colnames(visual_qa_long)[2]="tp"

overview_qoalat_visual=merge(overview_qoalat, visual_qa_long, by=c("subj","tp"))

#VISUAL QA FREEVIEW
visual_qafv=read.csv("/data/pt_02205/Analysis/Preprocessing/qa/diffusion/VISUAL/Visual_Check_Freeview.csv")
overview_qoalat_visual_fv=merge(overview_qoalat_visual, visual_qafv, by=c("subj","tp"))

#Diffusion:
#Measures from SQUAD
library("rjson")
setwd("/data/pt_02205/Analysis/Preprocessing/qa/diffusion/")

subjT0=read.table("/data/pt_02205/Analysis/Preprocessing/qa/diffusion/SQUAD/eddy_squad_list_T0.txt")
for (i in 1:nrow(subjT0)){
  #print(strsplit(toString(rs_QA[i,1]),'_')[[1]][1])
  subjT0[i,"subj"]=strsplit(toString(subjT0[i,1]),'/')[[1]][8]
  }

tmp <- fromJSON(file = "/data/pt_02205/Analysis/Preprocessing/qa/diffusion/SQUAD/squad_T0/group_db.json")
cnr_vals=tmp$qc_cnr
cnr_t0 <- data.frame(matrix(unlist(cnr_vals), nrow=length(cnr_vals), byrow=T))
cnr_t0$subj.id=subjT0$subj
colnames(cnr_t0)[1:2]=c("snr_t0","cnr_t0")

subjT18=read.table("/data/pt_02205/Analysis/Preprocessing/qa/diffusion/SQUAD/eddy_squad_list_T18.txt")
for (i in 1:nrow(subjT18)){
  #print(strsplit(toString(rs_QA[i,1]),'_')[[1]][1])
  subjT18[i,"subj"]=strsplit(toString(subjT18[i,1]),'/')[[1]][8]
}

tmp <- fromJSON(file = "/data/pt_02205/Analysis/Preprocessing/qa/diffusion/SQUAD/squad_T18/group_db.json")
cnr_vals=tmp$qc_cnr
cnr_t18 <- data.frame(matrix(unlist(cnr_vals), nrow=length(cnr_vals), byrow=T))
cnr_t18$subj.id=subjT18$subj
colnames(cnr_t18)[1:2]=c("snr_t18","cnr_t18")

cnr_all=merge(cnr_t0,cnr_t18,by="subj.id",all.x=TRUE)

cnr=reshape(cnr_all, varying = list(c(2,4),c(3,5)), v.names=c("snr","cnr"), 
            times=c('bl', 'fu'), idvar='subj', direction='long')
cnr=cnr[,c(1,2,3,4)]
colnames(cnr)[1:2]=c("subj","tp")

overview_qoalat_visual_fv_cnr=merge(overview_qoalat_visual_fv, cnr[,c("subj","tp","cnr")])

#### Get motion data from eddy
files <- list.files(path="/data/pt_02205/Data/wd/",
                    pattern = "corrected.eddy_movement_rms$",
                    recursive = TRUE,
                    all.files=TRUE,
                    full.names = TRUE)

rms=data.frame(mean_rms=double(),
               max_rms=double(),
               stringsAsFactors=FALSE)
for (i in 1:length(files)){
  tmp=read.table(files[i])
  if (strsplit(files[i],'/')[[1]][11]=="eddy")
  {
  print("bl")
  rms[i,"subj"]=strsplit(strsplit(files[i],'/')[[1]][10],'_')[[1]][3]
  rms[i,"tp"]="bl"
  rms[i,"mean_rms"]=mean(tmp$V1)
  rms[i,"max_rms"]=max(tmp$V1)
  }

  else
  {
    print("fu")
  rms[i,"subj"]=strsplit(strsplit(files[i],'/')[[1]][11],'_')[[1]][3]
  rms[i,"tp"]="fu"
  rms[i,"mean_rms"]=mean(tmp$V1)
  rms[i,"max_rms"]=max(tmp$V1)
  }
  }

length(unique(rms$subj))
rms$subj=as.factor(rms$subj)
rms$tp=as.factor(rms$tp)



overview_qoalat_visual_fv_cnr_rms=merge(overview_qoalat_visual_fv_cnr, rms, by=c("tp", "subj"), all.x=TRUE)
colnames(overview_qoalat_visual_fv_cnr_rms)[13]="Visual_Comment_TBSS_with_anatomy"
write.csv(overview_qoalat_visual_fv_cnr_rms, "/data/pt_02205/Analysis/Preprocessing/qa/QA_final.csv", row.names = FALSE)

##Select subjects for Christian QoalaT estimation

finalwc=read.csv("/data/pt_02205/Analysis/Preprocessing/qa/QA_final_with_manual_edits.csv")


manual_labels=finalwc[finalwc$FS_Exclude==1, c("subj","tp","FS_Exclude")]
tmp=finalwc[finalwc$FS_Exclude==0,]
zeros=tmp[sample(nrow(tmp), 40),
              c("subj","tp","FS_Exclude")]

manual_labels=rbind(manual_labels,zeros)

write.csv(manual_labels,
          "/data/pt_02205/Analysis/Preprocessing/qa/manual_labels_QC.csv",
          row.names = FALSE)
# read final labels and merge with sample-trained 

final_label=read.csv("/data/pt_02205/Analysis/Preprocessing/qa/QA_final_with_manual_edits.csv")
sample_trained=read.csv("/data/pt_02205/Analysis/Preprocessing/qa/freesurfer/QC/output/Qoala_T_predictions_subset_basedpt_02205.csv")
final_label_with_st=merge(final_label,sample_trained, by=c("subj","tp") )
