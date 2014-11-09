# This script makes box plots for gpa, gpa variance, gender, specialisation and ethnicity

man2013.df <- read.csv("2013_manual_summary_r.csv", header=TRUE)
man2013.df["Type"] <- "Manual"
auto2013.df <- read.csv("2013_automatic_summary_r.csv", header=TRUE)
auto2013.df["Type"] <- "Automatic"
# Combine dataframes
all.df <- rbind(man2013.df, auto2013.df)
all.df$Type <- factor(all.df$Type, levels=c("Manual","Automatic"), labels=c("Manual", "Automatic"))

# GPA
par(mfrow=c(1,2))
boxplot(Mean.GPA ~ Type, data=all.df, main="Mean GPA")
boxplot(GPA.Variance ~ Type, data=all.df, main="Variance of GPA")

# Gender
par(mfrow=c(1,2))
gen_ylim=c(0, 20)
boxplot(Males ~ Type, data=all.df, main="Number of Males", ylim=gen_ylim)
boxplot(Females ~ Type, data=all.df, main="Number of Females", ylim=gen_ylim)

# Discpline
par(mfrow=c(3,3))
dis_ylim=c(0, 10)
boxplot(Biomedical ~ Type, data=all.df, main="Number of Biomedical Students", ylim=dis_ylim)
boxplot(Chemical...Materials ~ Type, data=all.df, main="Number of Chemmat Students", ylim=dis_ylim)
boxplot(Civil ~ Type, data=all.df, main="Number of Civil Students", ylim=dis_ylim)
boxplot(Computer.Systems ~ Type, data=all.df, main="Number of CompSys Students", ylim=dis_ylim)
boxplot(Electrical ~ Type, data=all.df, main="Number of Electrical Students", ylim=dis_ylim)
boxplot(Engineering.Science ~ Type, data=all.df, main="Number of Engineering Science Students", ylim=dis_ylim)
boxplot(Mechanical ~ Type, data=all.df, main="Number of Mechanical Students", ylim=dis_ylim)
boxplot(Mechatronics ~ Type, data=all.df, main="Number of Mechatronics Students", ylim=dis_ylim)
boxplot(Software ~ Type, data=all.df, main="Number of Software Students", ylim=dis_ylim)

# Ethnicity
par(mfrow=c(2,2))
eth_ylim=c(0, 15)
boxplot(Pakeha ~ Type, data=all.df, main="Number of Pakeha Students", ylim=eth_ylim)
boxplot(Maori ~ Type, data=all.df, main="Number of Maori Students", ylim=eth_ylim)
boxplot(Asian ~ Type, data=all.df, main="Number of Asian Students", ylim=eth_ylim)
boxplot(Other ~ Type, data=all.df, main="Number of Students of Other Ethnicity", ylim=eth_ylim)
