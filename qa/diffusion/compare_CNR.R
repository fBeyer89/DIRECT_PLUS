library("rjson")


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


visual_qa=read.csv("VISUAL/Visual_Check_TBSS_HC_MD.csv", skip=1)
visual_qa_long=reshape(visual_qa[], varying = list(c(5,6)), 
                      v.names=c("DTI_anat_coreg"), 
                      times=c('bl', 'fu'), idvar='subj', direction='long')
colnames(visual_qa_long)[5]="tp"

merged_qa=merge(visual_qa_long, cnr, by=c("subj","tp"))
write.csv(merged_qa, "Visual_Check_TBSS_HC_MD_with_cnr.csv")

overview=read.csv("/data/p_02205/sample_description/participants_overview.csv")
overview_long=reshape(overview[,-c(2,7)], varying = list(c(2,6), 
                                               c(3,7), c(4,8),
                                               c(5,9), c(10,11)), 
                      v.names=c("DWI_comment", "DWI_done", "T1comment",
                                "Fsdone", "HC_MD_comment"), 
            times=c('bl', 'fu'), idvar='Subj.T0', direction='long')
write.csv(overview_long, "/data/p_02205/sample_description/participants_overview_long.csv" )
colnames(overview_long)[1]="subj"
colnames(overview_long)[2]="tp"
merged_info_qa=merge(overview_long, merged_qa, by=c("tp", "subj"))
write.csv(merged_info_qa, "Visual_Check_TBSS_HC_MD_with_cnr_info.csv")

###Here some other data is needed.
cnr_seq=merge(cnr,hcdata_group_seq[hcdata_group_seq$hemi=="right",
              c("subj","tp","group","without_seq_change","acq_pre0_after1_seqchange","mean_MD_HC")], by=c("subj","tp"))
cnr_seq$without_seq_change=as.factor(cnr_seq$without_seq_change)
cnr_seq$acq_pre0_after1_seqchange=as.factor(cnr_seq$acq_pre0_after1_seqchange)

#Histogram of CNR change
hist(cnr_seq$cnr,breaks=30)
cnr_seq[cnr_seq$cnr>10000,"subj"]
cnr_seq=cnr_seq[cnr_seq$cnr<10000&!is.na(cnr_seq$cnr),]

ggplot(cnr_seq, aes(x=tp, y=cnr, group=group, color=group)) +
  stat_summary(fun.y = mean, geom = "point") +
  stat_summary(fun.y = mean, geom = "line")

ggplot(cnr_seq, aes(x=tp, y=cnr, group=subj)) +
  geom_line(aes(color=subj)) + geom_point(aes(color=subj)) + guides(colour=FALSE)+
  labs(title="cnr change with/without acq changes")

ggplot(cnr_seq, aes(x=tp, y=cnr, color=without_seq_change, group=without_seq_change)) +
  stat_summary(fun.y = mean, geom = "point") +
  stat_summary(fun.y = mean, geom = "line") +
  facet_grid(. ~ group)

ggplot(cnr_seq, aes(x=tp, y=cnr, color=acq_pre0_after1_seqchange, group=acq_pre0_after1_seqchange)) +
  stat_summary(fun.y = mean, geom = "point") +
  stat_summary(fun.y = mean, geom = "line") +
  facet_grid(. ~ group)

ggplot(cnr_seq, aes(x=tp, y=mean_MD_HC, color=without_seq_change, group=without_seq_change)) +
  stat_summary(fun.y = mean, geom = "point") +
  stat_summary(fun.y = mean, geom = "line") +
  facet_grid(. ~ group)

ggplot(cnr_seq, aes(x=tp, y=mean_MD_HC, color=acq_pre0_after1_seqchange, group=acq_pre0_after1_seqchange)) +
  stat_summary(fun.y = mean, geom = "point") +
  stat_summary(fun.y = mean, geom = "line") +
  facet_grid(. ~ group)

ggplot(cnr_seq, aes(x=tp, y=cnr, color=acq_pre0_after1_seqchange, group=acq_pre0_after1_seqchange)) +
  stat_summary(fun.y = mean, geom = "point") +
  stat_summary(fun.y = mean, geom = "line") +
  facet_grid(. ~ group)

ggplot(cnr_seq, aes(x=tp, y=mean_MD_HC)) +
  stat_summary(fun.y = mean, geom = "point") +
  stat_summary(fun.y = mean, geom = "line") +
  facet_grid(. ~ group)

ggplot(hcdata_group[hcdata_group$hemi=="left",], aes(x=tp, y=mean_MD_HC)) +
  stat_summary(fun.y = mean, geom = "point") +
  stat_summary(fun.y = mean, geom = "line") +
  facet_grid(. ~ group)

ggplot(hcdata_group[hcdata_group$hemi=="right",], aes(x=tp, y=mean_MD_HC)) +
  stat_summary(fun.y = mean, geom = "point") +
  stat_summary(fun.y = mean, geom = "line") +
  facet_grid(. ~ group)

##does the cnr differ before/after sequence change
res=lmer(cnr ~ acq_pre0_after1_seqchange + (1|subj), cnr_seq)
null=lmer(cnr ~ (1|subj), cnr_seq)
anova(res,null)
summary(res)

#different across groups?
res=lmer(cnr ~ acq_pre0_after1_seqchange*group + (1|subj), cnr_seq)
null=lmer(cnr ~ acq_pre0_after1_seqchange + group+ (1|subj), cnr_seq)
anova(res,null)
summary(res)

#no, although group A improves in CNR, the others don't and the interaction is not significant.

#what if we differentiate between pre/post changing?
res=lmer(mean_MD_HC ~ tp*group + acq_pre0_after1_seqchange + (1|subj), cnr_seq)
null=lmer(mean_MD_HC ~ tp + group + acq_pre0_after1_seqchange + (1|subj), cnr_seq)
anova(res,null)
summary(res)
summary(null)

#what if using only those who did not get an upgrade?
res=lmer(mean_MD_HC ~ tp*group + (1|subj), cnr_seq[cnr_seq$without_seq_change==1,])
null=lmer(mean_MD_HC ~ tp + group + (1|subj), cnr_seq[cnr_seq$without_seq_change==1,])
anova(res,null)
summary(res)
summary(null)

#there is significantly less increase in MD in the group B.