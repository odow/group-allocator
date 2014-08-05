data.df <- read.csv('results.csv')

pdf('GPA distribution.pdf')

plot(density(data.df$GPA),col='red',
     ylim=c(0,0.4),xlim=c(1,9),
     bty='l',
     xlab = 'GPA',
     yaxt='n',ylab='',
     main = 'GPA distribution')
for (i in c(1:20)) {
  lines(density(subset(data.df$GPA,data.df$Group==i)))  
}
lines(density(data.df$GPA),col='red',lwd=4)

dev.off()


boxplot(GPA~Group,data=data.df,
        xlab='Group',ylab='GPA')
