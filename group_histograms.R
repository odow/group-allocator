# This script uses a csv file with the group allocations and plots a histogram for GPA for each group
library(lattice)
gpa_bins=c(0,1,2,3,4,5,6,7,8,9)
ylabp="Percent of Group"
xlabp="GPA"

# 2013 Group Labels
labels_2013=c("Group 1","Group 2","Group 3","Group 4","Group 5",
              "Group 6","Group 7","Group 8","Group 9","Group 10",
              "Group 11","Group 12","Group 13","Group 14","Group 15",
              "Group 16","Group 17","Group 18","Group 19","Group 20",
              "Group 21","Group 22","Group 23","Group 24")

# 2013 Manual Allocation
manv.df <- read.csv("2013_manual_allocation_r.csv",header=TRUE)
histogram( ~ Cumulative.GPA | factor(Allocated.Group, labels=labels_2013),
           data=manv.df, breaks=gpa_bins, ylab=ylabp,GPA=xlabp,
           main="Manual Allocation GPA Histogram for Groups in 2013")

# 2013 Group-Allocator
autov.df <- read.csv("2013_group_allocator_r.csv",header=TRUE)
histogram( ~ Cumulative.GPA | factor(Allocated.Group, labels=labels_2013),
           data=autov.df, breaks=gpa_bins, ylab=ylabp,GPA=xlabp,
           main="Automatic Allocation GPA Histogram for Groups using 2013 Data")

# 2013 Entire Class
histogram( ~ Cumulative.GPA, data=manv.df, breaks=gpa_bins, ylab=ylabp,GPA=xlabp, main="GPA Histogram for 2013 Class")

# 2014 Group Labels
labels_2014=c("Group 1","Group 2","Group 3","Group 4","Group 5",
              "Group 6","Group 7","Group 8","Group 9","Group 10",
              "Group 11","Group 12","Group 13","Group 14","Group 15",
              "Group 16","Group 17","Group 18","Group 19","Group 20",
              "Group 21","Group 22","Group 23")

# 2014 Group-Allocator
auto14.df <- read.csv("2014_group_allocator_r.csv",header=TRUE)
histogram( ~ Cumulative.GPA | factor(Allocated.Group, labels=labels_2014),
           data=auto14.df, breaks=gpa_bins, ylab=ylabp,GPA=xlabp,
           main="Automatic Allocation GPA Histogram for Groups in 2014")

# 2014 Entire Class
histogram( ~ Cumulative.GPA, data=auto14.df, breaks=gpa_bins, ylab=ylabp,GPA=xlabp, main="GPA Histogram for 2014 Class")