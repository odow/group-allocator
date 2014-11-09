# This script makes box plots for gpa, gpa variance, gender, specialisation and ethnicity

man2013.df <- read.csv("2013_manual_summary_r.csv", header=TRUE)
man2013.df["Type"] <- 1
auto2013.df <- read.csv("2013_automatic_summary_r.csv", header=TRUE)
auto2013.df["Type"] <- 2
auto2014.df <- read.csv("2014_automatic_summary_r.csv", header=TRUE)
auto2014.df["Type"] <- 3
# Combine dataframes
all.df <- rbind(man2013.df, auto2013.df, auto2014.df)
all.df$Type <- factor(all.df$Type, levels=c(1,2,3), labels=c("Manual", "GA 2013", "GA 2014"))

# GPA
par(mfrow=c(1,2))
boxplot(Mean.GPA ~ Type, data=all.df, main="Mean GPA of Group")
boxplot(GPA.Variance ~ Type, data=all.df, main="Variance of GPA within Group")
mtext("GA = Group-Allocator", side = 3, line = -47, outer = TRUE)
# Gender
par(mfrow=c(1,2))
gen_ylim=c(0, 20)
boxplot(Males ~ Type, data=all.df, main="Number of Males Per Group", ylim=gen_ylim)
boxplot(Females ~ Type, data=all.df, main="Number of Females Per Group", ylim=gen_ylim)
mtext("GA = Group-Allocator", side = 3, line = -47, outer = TRUE)

# Discpline
par(mfrow=c(3,3))
dis_ylim=c(0, 10)
boxplot(Biomedical ~ Type, data=all.df, main="Number of Biomedical Students Per Group", ylim=dis_ylim)
boxplot(Chemical...Materials ~ Type, data=all.df, main="Number of Chemmat Students Per Group", ylim=dis_ylim)
boxplot(Civil ~ Type, data=all.df, main="Number of Civil Students Per Group", ylim=dis_ylim)
boxplot(Computer.Systems ~ Type, data=all.df, main="Number of CompSys Students Per Group", ylim=dis_ylim)
boxplot(Electrical ~ Type, data=all.df, main="Number of Electrical Students Per Group", ylim=dis_ylim)
boxplot(Engineering.Science ~ Type, data=all.df, main="Number of Engineering Science Students Per Group", ylim=dis_ylim)
boxplot(Mechanical ~ Type, data=all.df, main="Number of Mechanical Students Per Group", ylim=dis_ylim)
boxplot(Mechatronics ~ Type, data=all.df, main="Number of Mechatronics Students Per Group", ylim=dis_ylim)
boxplot(Software ~ Type, data=all.df, main="Number of Software Students Per Group", ylim=dis_ylim)
mtext("GA = Group-Allocator", side = 3, line = -73, outer = TRUE)

# Ethnicity
par(mfrow=c(2,2))
eth_ylim=c(0, 15)
boxplot(Pakeha ~ Type, data=all.df, main="Number of Pakeha Students Per Group", ylim=eth_ylim)
boxplot(Maori ~ Type, data=all.df, main="Number of Maori Students Per Group", ylim=eth_ylim)
boxplot(Asian ~ Type, data=all.df, main="Number of Asian Students Per Group", ylim=eth_ylim)
boxplot(Other ~ Type, data=all.df, main="Number of Students of Other Ethnicity Per Group", ylim=eth_ylim)
mtext("GA = Group-Allocator", side = 3, line = -56, outer = TRUE)
