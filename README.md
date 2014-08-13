Group-Allocator
===============

Group-Allocator is a solution developed by Oscar Dowson and Michael Fairley for allocating students to groups in a way that balances the characteristics of the students between the groups. It was first used to group over 650 students for a systems engineering project at The University of Auckland with the goal to balance GPA, gender, engineering specialization and ethnicity between the groups. It is released under the MIT Licence.

The solution is implemented in a Microsoft Excel interface so it makes it easy for administrators to download and use. It requires SolverStudio, an add-in for Excel that provides "an integrated environment for optimization using modeling languages within Excel". SolverStudio can be downloaded from http://solverstudio.org. For further details, please read the "Instructions" sheet in the "Group_Allocator.xlsx" spreadsheet.

## Compatible Versions of Microsoft Excel and SolverStudio

Group-Allocator has been tested on Microsoft Excel 2010 and 2013, and SolverStudio 0.6.0 and 0.5.4.

## Technical Details

Group-Allocator uses a mixed integer program to minimize the difference between the maximum and minimum GPA and GPA variance over all the groups, and uses relaxed constraints to spread individuals from different groups (such as a particular gender or ethnicity) over all the groups. For the full model please consult the source code within "Group_Allocator.xlsx" by using the "Show Model" function of SolverStudio.

## Files
+ **Group_Allocator.xlsx** - the main spreadsheet that contains everything necessary to run Group-Allocator with SolverStudio installed
+ **solve_script.py** - a copy of the source code contained within Group_Allocator.xlsx for easy editing in a text editor and commit history in Git
+ **data_gen.xlsx** - a spreadsheet with formulae to demonstrate how test data can be generated
