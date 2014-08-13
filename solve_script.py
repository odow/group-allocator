# ============================================================================
# Group Allocator - allocates students to balanced groups
# ============================================================================

# The MIT License (MIT)

# Copyright (c) 2014 Michael Fairley (mfai035@aucklanduni.ac.nz)

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# ============================================================================
# Authors : Oscar Dowson odow003@aucklanduni.ac.nz
#           Michael Fairley mfai035@aucklanduni.ac.nz
# Date : 8 August 2014
#
# ============================================================================
from pulp import *
from System import Array
import datetime
problem = LpProblem('ENGGEN403', LpMinimize)
print('Creating model...')

# ============================================================================
# Pre-computed variables and constants

# Weightings
gpa_mean_weight = 1
gpa_variance_weight = 1
specialisation_weight = 1
gender_weight = 1
ethnicity_weight = 1

SPECIALISATIONS = list()
for s in STUDENTS:
    if specialisation[s] not in SPECIALISATIONS:
        SPECIALISATIONS.append(specialisation[s])

ETHNICITIES = list()
for s in STUDENTS:
    if ethnicity[s] not in ETHNICITIES:
        ETHNICITIES.append(ethnicity[s])

# Set for all groups
GROUPS = range(1, int(number_groups) + 1)

# Set for students assigned to group
STUDENT_GROUP = [(s, g) for s in STUDENTS for g in GROUPS]

# Number of students
number_students = len(STUDENTS)

# Group sizes
m1 = int(number_students / number_groups)
m2 = m1+1

# Number of each group size
j2 = int(number_students - m1 * number_groups)
j1 = int(number_groups - j2)

# Sets for each group size
GROUPS1 = range(1, j1 + 1)
GROUPS2 = range(j1 + 1, int(number_groups) + 1)

# Average GPA of all students
gpa_mean = sum([gpa[i] for i in STUDENTS]) / number_students

# Minimum number of females and males in each group
number_males = sum([gender[i].lower() == 'm' for i in STUDENTS])
male_min = int(number_males / number_groups)
number_females = sum([gender[i].lower() == 'f' for i in STUDENTS])
female_min = int(number_females / number_groups)

# Number in each specialisation
specialisation_counts = {}
for s in SPECIALISATIONS:
    specialisation_counts[s] = sum([specialisation[i].lower()
                                   == s.lower() for i in STUDENTS])

# Minimum number of each specialisation in each group
specialisation_min = {}
for s in SPECIALISATIONS:
    specialisation_min[s] = int(specialisation_counts[s] / number_groups)

# Number from each ethnicity
ethnicity_counts = {}
for e in ETHNICITIES:
    ethnicity_counts[e] = sum([ethnicity[i].lower()
                              == e.lower() for i in STUDENTS])

# Minimum number of each ethnicity in each group
ethnicity_min = {}
for e in ETHNICITIES:
    ethnicity_min[e] = int(ethnicity_counts[e] / number_groups)

# Artificial variables sets for specialisations and ethnicities in each group
# Penalises violating constraint for number of each in group
SPECIALISATION_ARTIFICIAL = [(s, g) for s in SPECIALISATIONS for g in GROUPS]
ETHNICITY_ARTIFICIAL = [(e, g) for e in ETHNICITIES for g in GROUPS]

# ============================================================================
#   Decision Variables

# x = 1 if student s is assigned to group g, else 0
x = LpVariable.dicts('x', STUDENT_GROUP, None, None, LpBinary)
female_artificial = LpVariable.dicts('female_artificial',
                                     GROUPS,
                                     0, number_students)
male_artificial = LpVariable.dicts('male_artificial',
                                   GROUPS,
                                   0, number_students)
specialisation_artificial = LpVariable.dicts('specialisation_artificial',
                                             SPECIALISATION_ARTIFICIAL,
                                             0, number_students)
ethnicity_artificial = LpVariable.dicts('ethnicity_artificial',
                                        ETHNICITY_ARTIFICIAL,
                                        0, number_students)
gpa_min = LpVariable('gpa_min', 0, 9)
gpa_max = LpVariable('gpa_max', 0, 9)
gpa_variance_min = LpVariable('gpa_variance_min', 0, 25)
gpa_variance_max = LpVariable('gpa_variance_max', 0, 25)

# ============================================================================
#   Objective Function

problem += gpa_mean_weight * (gpa_max - gpa_min) \
    + gpa_variance_weight * (gpa_variance_max - gpa_variance_min) \
    + 1e4 * (specialisation_weight * lpSum([specialisation_artificial[i] \
                                           for i in SPECIALISATION_ARTIFICIAL]) \
             + gender_weight * lpSum([female_artificial[i] \
                                     for i in GROUPS]) \
             + ethnicity_weight * lpSum([ethnicity_artificial[i] \
                                        for i in ETHNICITY_ARTIFICIAL]) \
             ), 'objective'

# ============================================================================
#   Constraints

# Every student is assigned to exactly one group
for s in STUDENTS:
    problem += lpSum([x[(s, g)] for g in GROUPS]) == 1, 'single_group_%s' % s

# Constraint for first group size
for g in GROUPS1:
    # Size if group is m1
    problem += lpSum([x[(s, g)] for s in STUDENTS]) == m1, 'size_g%d' % g

    # Minimum GPA is given by group with lowest GPA
    problem += lpSum([gpa[s] * x[(s, g)] for s in STUDENTS]) >= m1 * gpa_min, \
        'calculate_min_gpa_g%d' % g

    # Maximum GPA is given by group with highest GPA
    problem += lpSum([gpa[s] * x[(s, g)] for s in STUDENTS]) <= m1 * gpa_max, \
        'calculate_max_gpa_g%d' % g

    # Minimum variance of GPA is given by group with lowest variance
    problem += lpSum([pow(gpa[s] - gpa_mean, 2) * x[(s, g)] for s in STUDENTS]) \
        >= m1 * gpa_variance_min, 'calculate_gpa_variance_min_g%d' % g

    # Maximum variance of GPA is given by group with highest variance
    problem += lpSum([pow(gpa[s] - gpa_mean, 2) * x[(s, g)] for s in STUDENTS]) \
        <= m1 * gpa_variance_max, 'calculate_gpa_variance_max_g%d' % g

# Constraint for second group size
for g in GROUPS2:
    # Size if group is m2
    problem += lpSum([x[(s, g)] for s in STUDENTS]) == m2, 'size_g%d' % g

    # Minimum GPA is given by group with lowest GPA
    problem += lpSum([gpa[s] * x[(s, g)] for s in STUDENTS]) >= m2 * gpa_min, \
        'calculate_min_gpa_g%d' % g

    # Maximum GPA is given by group with highest GPA
    problem += lpSum([gpa[s] * x[(s, g)] for s in STUDENTS]) <= m2 * gpa_max, \
        'calculate_max_gpa_g%d' % g

    # Minimum variance of GPA is given by group with lowest variance
    problem += lpSum([pow(gpa[s] - gpa_mean, 2) * x[(s, g)] for s in STUDENTS]) \
        >= m2 * gpa_variance_min, 'calculate_gpa_variance_min_g%d' % g

    # Maximum variance of GPA is given by group with highest variance
    problem += lpSum([pow(gpa[s] - gpa_mean, 2) * x[(s, g)] for s in STUDENTS]) \
        <= m2 * gpa_variance_max, 'calculate_gpa_variance_max_g%d' % g

# Semi-relaxed constraints to enforce gender,
# specialisation and ethnicity distribution
for g in GROUPS:
    # Gender must be at least minimum (relaxed)
    problem += lpSum([x[(s, g)] for s in STUDENTS if gender[s].lower() == 'f']) \
        + female_artificial[g] >= female_min, \
        'min_females_g%d' % g

    problem += lpSum([x[(s, g)] for s in STUDENTS if gender[s].lower() == 'm']) \
        + male_artificial[g] >= male_min, \
        'min_males_g%d' % g

    # Number from each specialisation must be at least min (relaxed)
    for k in SPECIALISATIONS:
        problem += lpSum([x[(s, g)] for s in STUDENTS
                         if specialisation[s].lower() == k.lower()]) \
            + specialisation_artificial[(k, g)] >= specialisation_min[k], \
            'min_spec%s_g%d' % (k, g)

    # Number from each ethnicity must be at least min (relaxed)
    for e in ETHNICITIES:
        problem += lpSum([x[(s, g)] for s in STUDENTS
                         if ethnicity[s].lower() == e.lower()]) \
            + ethnicity_artificial[(e, g)] >= ethnicity_min[e], \
            'min_eth%s_g%d' % (e, g)

# ============================================================================
#   Solve

print('Solving . . .')
try:
    # SolverStudio version < 0.6
    problem.solve(solvers.PULP_CBC_CMD(msg=1, maxSeconds=time_limit))
except:
    # new version >= 0.6
    problem.solve(COIN_CMD(msg=1, maxSeconds=time_limit))

# ============================================================================
#   Solution Post Processing and Display in Excel spreadsheet

print('Finished Solving')


# Write group number for each student and add to group list
for s, g in STUDENT_GROUP:
    if x[(s, g)].value() == 1:
        groups[s] = g

# Make list to hold groups
students_in_group = {}

for g in GROUPS:
    students_in_group[g] = list()

for s in STUDENTS:
    for g in GROUPS:
        if groups[s] == g:
            students_in_group[g].append(s)


gpa_difference = gpa_max.value() - gpa_min.value()
gpa_variance_difference = gpa_variance_max.value() - gpa_variance_min.value()
gpa_variance_total = (sum(pow(gpa[s] - gpa_mean, 2)
                      for s in STUDENTS)) \
    / number_students
# Perform calculations for each group
students_group = {}
males_group = {}
females_group = {}
gpa_total_group = {}
specialisations_group = {}
for s in SPECIALISATIONS:
    specialisations_group[s] = {}
ethnicities_group = {}
for e in ETHNICITIES:
    ethnicities_group[e] = {}

# Initialise python sets
for g in GROUPS:
    students_group[g] = 0
    males_group[g] = 0
    females_group[g] = 0
    gpa_total_group[g] = float(0.00)
    for s in SPECIALISATIONS:
        specialisations_group[s][g] = 0
    for e in ETHNICITIES:
        ethnicities_group[e][g] = 0

# Count the number of males, females etc in each group
for s in STUDENTS:
    g = groups[s]
    if gender[s].lower() == 'f':
        females_group[g] += 1
    elif gender[s].lower() == 'm':
        males_group[g] += 1
    gpa_total_group[g] += gpa[s]
    for k in SPECIALISATIONS:
        if specialisation[s] == k:
            specialisations_group[k][g] += 1
    for e in ETHNICITIES:
        if ethnicity[s] == e:
            ethnicities_group[e][g] += 1
    students_group[g] += 1

# Compute average GPA for each group
gpa_mean_group = {}
for g in GROUPS:
    gpa_mean_group[g] = float(gpa_total_group[g]) / float(students_group[g])

# Compute GPA variance for each group
gpa_variance_group = {}
for g in GROUPS:
    gpa_variance_group[g] = float((sum(pow(gpa[s] - gpa_mean_group[g], 2)
                                  for s in students_in_group[g]))) \
        / float(len(students_in_group[g]))

print('\n')
print('Biggest difference in mean GPA: %.2f'
      % gpa_difference)
print('Biggest difference in GPA variance: %.2f'
      % gpa_variance_difference)
print('\n')
print('Maximum number of people under limit')
print('Specialisations: %.0f' %
      sum([specialisation_artificial[i].value()
          for i in SPECIALISATION_ARTIFICIAL]))
print('Females: %.0f' % sum([female_artificial[i].value()
      for i in GROUPS]))
print('Ethnicities: %.0f' %
      sum([ethnicity_artificial[i].value() for i in ETHNICITY_ARTIFICIAL]))
print('\n')

# Print data to spreadsheet
# Summary Results
ws = Application.Worksheets('Summary_Results')
ws.Cells.Clear()

# Results for each group
ws.Cells(1, 1).Value = 'Group'
ws.Cells(1, 1).Font.Bold = True
# Rows of table
ws.Cells(2, 1).Value = 'Whole Class'
cell_index = 2
for g in GROUPS:
    cell_index += 1
    ws.Cells(cell_index, 1).Value = g

# Columns of Table
ws.Cells(1, 2).Value = 'Students'
ws.Cells(1, 2).Font.Bold = True
ws.Cells(1, 3).Value = 'Males'
ws.Cells(1, 3).Font.Bold = True
ws.Cells(1, 4).Value = 'Females'
ws.Cells(1, 4).Font.Bold = True
ws.Cells(1, 5).Value = 'Mean GPA'
ws.Cells(1, 5).Font.Bold = True
ws.Cells(1, 6).Value = 'GPA Variance'
ws.Cells(1, 6).Font.Bold = True
cell_index = 6
for s in SPECIALISATIONS:
    cell_index += 1
    ws.Cells(1, cell_index).Value = s
    ws.Cells(1, cell_index).Font.Bold = True
    ws.Range(ws.Cells(1, cell_index), ws.Cells(1, cell_index)).Interior.ThemeColor = 5
for e in ETHNICITIES:
    cell_index += 1
    ws.Cells(1, cell_index).Value = e
    ws.Cells(1, cell_index).Font.Bold = True
    ws.Range(ws.Cells(1, cell_index), ws.Cells(1, cell_index)).Interior.ThemeColor = 6

# Fill in table data by column
# Whole Class frst
ws.Cells(2, 2).Value = number_students
ws.Cells(2, 3).Value = number_males
ws.Cells(2, 4).Value = number_females
ws.Cells(2, 5).Value = '%.2f' % gpa_mean
ws.Cells(2, 6).Value = '%.2f' % gpa_variance_total
cell_index = 6
for s in SPECIALISATIONS:
    cell_index += 1
    ws.Cells(2, cell_index).Value = specialisation_counts[s]

for e in ETHNICITIES:
    cell_index += 1
    ws.Cells(2, cell_index).Value = ethnicity_counts[e]

    # Each group
cell_index = 2
for g in GROUPS:
    cell_index += 1
    ws.Cells(cell_index, 2).Value = students_group[g]
    ws.Cells(cell_index, 3).Value = males_group[g]
    ws.Cells(cell_index, 4).Value = females_group[g]
    ws.Cells(cell_index, 5).Value = '%.2f' % gpa_mean_group[g]
    ws.Cells(cell_index, 6).Value = '%.2f' % gpa_variance_group[g]
    col_index = 6
    for s in SPECIALISATIONS:
        col_index += 1
        ws.Cells(cell_index, col_index).Value = specialisations_group[s][g]
    for e in ETHNICITIES:
        col_index += 1
        ws.Cells(cell_index, col_index).Value = ethnicities_group[e][g]

# Insert data for box plots
col_index += 1
ws.Cells(1, col_index + 1).Value = 'gpa_min'
ws.Cells(1, col_index + 2).Value = 'gpa_q1'
ws.Cells(1, col_index + 3).Value = 'gpa_median'
ws.Cells(1, col_index + 4).Value = 'gpa_q3'
ws.Cells(1, col_index + 5).Value = 'gpa_max'
ws.Cells(1, col_index + 6).Value = 'gpa_d_min'
ws.Cells(1, col_index + 7).Value = 'gpa_d_q1'
ws.Cells(1, col_index + 8).Value = 'gpa_d_median'
ws.Cells(1, col_index + 9).Value = 'gpa_d_q3'
ws.Cells(1, col_index + 10).Value = 'gpa_d_max'

# Create array for each group containing gpas
data_summary = {}
for g in GROUPS:
    array = Array.CreateInstance(object, len(students_in_group[g]))
    for i in range(len(students_in_group[g])):
        student = students_in_group[g][i]
        array[i] = gpa[student]
    min_gpa = Application.WorksheetFunction.Min(array)
    q1_gpa = Application.WorksheetFunction.Quartile(array, 1)
    med_gpa = Application.WorksheetFunction.Median(array)
    q3_gpa = Application.WorksheetFunction.Quartile(array, 3)
    max_gpa = Application.WorksheetFunction.Max(array)
    data_summary[g] = [min_gpa, q1_gpa, med_gpa, q3_gpa, max_gpa]

row_index = 2
for g in GROUPS:
    row_index += 1
    ws.Cells(row_index, col_index + 1).Value = '%.2f' % data_summary[g][0]
    ws.Cells(row_index, col_index + 2).Value = '%.2f' % data_summary[g][1]
    ws.Cells(row_index, col_index + 3).Value = '%.2f' % data_summary[g][2]
    ws.Cells(row_index, col_index + 4).Value = '%.2f' % data_summary[g][3]
    ws.Cells(row_index, col_index + 5).Value = '%.2f' % data_summary[g][4]

    # Differences needed for charting
    ws.Cells(row_index, col_index + 6).Value = '%.2f' % data_summary[g][0]
    ws.Cells(row_index, col_index + 7).Value = '%.2f' % (data_summary[g][1] -  data_summary[g][0])
    ws.Cells(row_index, col_index + 8).Value = '%.2f' % (data_summary[g][2] -  data_summary[g][1])
    ws.Cells(row_index, col_index + 9).Value = '%.2f' % (data_summary[g][3] -  data_summary[g][2])
    ws.Cells(row_index, col_index + 10).Value = '%.2f' % (data_summary[g][4] -  data_summary[g][3])

# Autofit columns in Summary_Results
ws.Activate()
ws.Cells.Select()
Application.Selection.Columns.AutoFit()
ws.Range(ws.Cells(2, 5), ws.Cells(number_groups+2, 6)).NumberFormat = '0.00'
ws.Range(ws.Cells(2, 1), ws.Cells(2, 6 + len(SPECIALISATIONS) + len(ETHNICITIES))).Style = 'Good'
ws.Range(ws.cells(1, 1), ws.Cells(number_groups+2, 1)).Borders(10).LineStyle = 1
ws.Range(ws.cells(1, 1), ws.Cells(number_groups+2, 1)).HorizontalAlignment = -4131
ws.Cells(number_groups+5, 1).Select()

# Generate graphs
wb = Application.ActiveWorkbook

# Delete all existing charts
for sheet in Application.Charts:
    if sheet.Name.endswith('_Chart') is True:
        Application.DisplayAlerts = False
        sheet.Delete()
        Application.DisplayAlerts = True


# GPA Box Plot Chart
# Select data range
print('Charting GPA . . .')
ws.Range(ws.Cells(3, col_index + 6), ws.Cells(2 + number_groups, col_index + 10)).Select()
Application.Worksheets('Summary_Results').Shapes.AddChart2(297, 52).Select()
a = Application.ActiveChart
a.FullSeriesCollection(1).Select()
Application.Selection.Format.Fill.Visible = 0
Application.Selection.Format.Line.Visible = 0
a.FullSeriesCollection(2).Select()
Application.Selection.Format.Fill.Visible = 0
Application.Selection.Format.Line.Visible = 0
a.FullSeriesCollection(2).HasErrorBars = True
#a.FullSeriesCollection(2).ErrorBars.Select()
a.FullSeriesCollection(2).ErrorBar(Direction=1, Include=3, Type=2, Amount=100)


a.FullSeriesCollection(5).Select()
Application.Selection.Format.Fill.Visible = 0
Application.Selection.Format.Line.Visible = 0


a.FullSeriesCollection(4).HasErrorBars = True
a.FullSeriesCollection(4).ErrorBar(Direction=1, Include=2, Type=2, Amount=100)

a.FullSeriesCollection(4).Select()
Application.Selection.Format.Fill.Visible = 0
Application.Selection.Format.Line.Visible = 1
Application.Selection.Format.Line.ForeColor.ObjectThemeColor = 13

a.FullSeriesCollection(3).Select()
Application.Selection.Format.Fill.Visible = 0
Application.Selection.Format.Line.Visible = 1
Application.Selection.Format.Line.ForeColor.ObjectThemeColor = 13

a.SetElement(2)
a.SetElement(306)
a.SetElement(301)
a.SetElement(102)
a.Legend.Select()
Application.Selection.Delete()
a.ChartTitle.Text = 'GPA spread per group (lines bottom to top = Min, Q1, Median, Q3, Max)'
a.Axes(1, 1).HasTitle = True
a.Axes(1, 1).AxisTitle.Text = 'Group'
a.Axes(2, 1).HasTitle = True
a.Axes(2, 1).AxisTitle.Text = 'GPA'
a.Axes(2).MaximumScale = 9
a.Axes(2).MinimumScale = 0
a.Location(Where=1, Name='GPA_Chart')
a.deselect()

# GPA mean and variance graph
# print('Charting GPA . . .')
# Application.Worksheets('Summary_Results').Activate()
# ws.Cells(number_groups+5, 1).Select()
# Application.Worksheets('Summary_Results').Shapes.AddChart(201, 54).Select()
# a = Application.ActiveChart
# a.SeriesCollection().NewSeries()
# a.FullSeriesCollection(1).Name = 'GPA'
# a.FullSeriesCollection(1).Values = ws.Range(ws.Cells(3, 5), ws.Cells(2 + number_groups, 5))
# a.FullSeriesCollection(1).XValues = x_axis_range
# a.SeriesCollection().NewSeries()
# a.FullSeriesCollection(2).Name = 'GPA Variance'
# a.FullSeriesCollection(2).Values = ws.Range(ws.Cells(3, 6), ws.Cells(2 + number_groups, 6))
# a.FullSeriesCollection(2).XValues = x_axis_range
# a.SetElement(2)
# a.SetElement(306)
# a.SetElement(301)
# a.SetElement(102)
# a.ChartTitle.Text = 'Mean GPA and Variance of GPA'
# a.Axes(1, 1).HasTitle = True
# a.Axes(1, 1).AxisTitle.Text = 'Group'
# a.Axes(2, 1).HasTitle = True
# a.Axes(2, 1).AxisTitle.Text = 'GPA'
# a.Axes(2).MaximumScale = 9
# a.Axes(2).MinimumScale = 0
# a.Location(Where=1, Name='GPA_Chart')
# a.deselect()

x_axis_range = ws.Range(ws.Cells(3, 1), ws.Cells(2 + number_groups, 1))

# Gender
print('Charting Gender . . .')
Application.Worksheets('Summary_Results').Activate()
ws.Cells(number_groups+5, 1).Select()
Application.Worksheets('Summary_Results').Shapes.AddChart(201, 54).Select()
a = Application.ActiveChart
a.SeriesCollection().NewSeries()
a.FullSeriesCollection(1).Name = 'Male'
a.FullSeriesCollection(1).Values = ws.Range(ws.Cells(3, 3), ws.Cells(2 + number_groups, 3))
a.FullSeriesCollection(1).XValues = x_axis_range
a.SeriesCollection().NewSeries()
a.FullSeriesCollection(2).Name = 'Female'
a.FullSeriesCollection(2).Values = ws.Range(ws.Cells(3, 4), ws.Cells(2 + number_groups, 4))
a.FullSeriesCollection(2).XValues = x_axis_range
a.SetElement(2)
a.SetElement(306)
a.SetElement(301)
a.SetElement(102)
a.ChartTitle.Text = 'Number of Males and Females in each group'
a.Axes(1, 1).HasTitle = True
a.Axes(1, 1).AxisTitle.Text = 'Group'
a.Axes(2, 1).HasTitle = True
a.Axes(2, 1).AxisTitle.Text = 'Number of Students'
a.Axes(2).MaximumScale = m2 + 1
a.Axes(2).MinimumScale = 0
a.Location(Where=1, Name='Gender_Chart')
a.deselect()

# Specialisations
print('Charting Specialisations . . .')
col_index = 6
for s in SPECIALISATIONS:
    col_index += 1
    ws = Application.Worksheets('Summary_Results')
    y_axis_range = ws.Range(ws.Cells(3, col_index),
                            ws.Cells(2 + number_groups, col_index))
    ws.Activate()
    ws.Cells(number_groups+5, 1).Select()
    ws.Shapes.AddChart(201, 54).Select()
    a = Application.ActiveChart
    a.SeriesCollection().NewSeries()
    a.FullSeriesCollection(1).Name = s
    a.FullSeriesCollection(1).Values = y_axis_range
    a.FullSeriesCollection(1).XValues = x_axis_range
    a.SetElement(2)
    a.SetElement(306)
    a.SetElement(301)
    a.SetElement(102)
    a.ChartTitle.Text = '%s students in each group' % s.title()
    a.Axes(1, 1).HasTitle = True
    a.Axes(1, 1).AxisTitle.Text = 'Group'
    a.Axes(2, 1).HasTitle = True
    a.Axes(2, 1).AxisTitle.Text = 'Number of Students'
    a.Axes(2).MaximumScale = m2 + 1
    a.Axes(2).MinimumScale = 0
    title = '%s_Chart' % s
    a.Location(Where=1, Name=title)
    wb.Sheets(title).Tab.ThemeColor = 9
    wb.Sheets(title).Tab.TintAndShade = 0
    a.deselect()

# Ethnicities
print('Charting Ethnic Groups . . .')
for e in ETHNICITIES:
    col_index += 1
    ws = Application.Worksheets('Summary_Results')
    y_axis_range = ws.Range(ws.Cells(3, col_index),
                            ws.Cells(2 + number_groups, col_index))
    ws.Activate()
    ws.Cells(number_groups+5, 1).Select()
    ws.Shapes.AddChart(201, 54).Select()
    a = Application.ActiveChart
    a.SeriesCollection().NewSeries()
    a.FullSeriesCollection(1).Name = e
    a.FullSeriesCollection(1).Values = y_axis_range
    a.FullSeriesCollection(1).XValues = x_axis_range
    a.SetElement(2)
    a.SetElement(306)
    a.SetElement(301)
    a.SetElement(102)
    a.ChartTitle.Text = '%s students in each group' % e.title()
    a.Axes(1, 1).HasTitle = True
    a.Axes(1, 1).AxisTitle.Text = 'Group'
    a.Axes(2, 1).HasTitle = True
    a.Axes(2, 1).AxisTitle.Text = 'Number of Students'
    a.Axes(2).MaximumScale = m2 + 1
    a.Axes(2).MinimumScale = 0
    title = '%s(E)_Chart' % e
    a.Location(Where=1, Name=title)
    wb.Sheets(title).Tab.ThemeColor = 6
    wb.Sheets(title).Tab.TintAndShade = 0
    a.deselect()

Application.Worksheets('Summary_Results').Move(after=Application.Worksheets('Student_Data'))

# Group Lists in Separate Workbook
# Setup paths
now = datetime.datetime.now()
path = Application.ActiveWorkbook.path
append_string = now.strftime('%Y-%m-%d_%H.%M.%S')
instructor_workbook_name = 'Groups_InstructorView_%s' % (append_string)
student_workbook_name = 'Groups_StudentView_%s' % (append_string)

save_path_instructor = '%s\\%s.xlsx' % (path, instructor_workbook_name)
save_path_student = '%s\\%s.xlsx' % (path, student_workbook_name)

# Instructor View
# Create new workbook
Application.Workbooks.Add()
Application.ActiveWorkbook.SaveAs(Filename=save_path_instructor)
wb = Application.Workbooks(instructor_workbook_name)

# All groups
wb.Sheets.Add()
wb.ActiveSheet.Name = 'All_Groups'
ws = wb.Worksheets('All_Groups')

# Headers
ws.Cells(1, 1).Value = 'Group'
ws.Cells(1, 1).Font.Bold = True

ws.Cells(1, 2).Value = 'Name'
ws.Cells(1, 2).Font.Bold = True

ws.Cells(1, 3).Value = 'UPI'
ws.Cells(1, 3).Font.Bold = True

ws.Cells(1, 4).Value = 'Discipline'
ws.Cells(1, 4).Font.Bold = True

ws.Cells(1, 5).Value = 'UoA Email'
ws.Cells(1, 5).Font.Bold = True

ws.Cells(1, 6).Value = 'GPA'
ws.Range(ws.Cells(1, 6), ws.Cells(1, 6)).Style = 'Bad'
ws.Cells(1, 6).Font.Bold = True

ws.Cells(1, 7).Value = 'Ethnic Group'
ws.Range(ws.Cells(1, 7), ws.Cells(1, 7)).Style = 'Bad'
ws.Cells(1, 7).Font.Bold = True

# Data
row_index = 1
for g in GROUPS:
    for s in students_in_group[g]:
        row_index += 1
        ws.Cells(row_index, 1).Value = g
        ws.Cells(row_index, 2).Value = NAMES[s]
        ws.Cells(row_index, 3).Value = UPI[s]
        ws.Cells(row_index, 4).Value = specialisation[s]
        ws.Cells(row_index, 5).Value = '%s@aucklanduni.ac.nz' % UPI[s]
        ws.Cells(row_index, 6).Value = '%.2f' % gpa[s]
        ws.Range(ws.Cells(row_index, 6), ws.Cells(row_index, 6)).NumberFormat = '0.00'
        ws.Cells(row_index, 7).Value = ethnicity[s]
        # Space between each group
    row_index += 1

ws.Activate()
ws.Cells.Select()
Application.Selection.Columns.AutoFit()
ws.Cells(1, 1).Select()

for sheet in wb.Worksheets:
    if sheet.Name != 'All_Groups':
        print(sheet.Name)
        Application.DisplayAlerts = False
        sheet.Delete()
        Application.DisplayAlerts = True


# Make a sheet for each group
for g in GROUPS:
    count = Application.Worksheets.Count
    wb.Sheets.Add(After=wb.Sheets(count))
    wb_name = 'Group_%s' % g
    wb.ActiveSheet.Name = wb_name
    ws = wb.Worksheets(wb_name)

    # Headers
    ws.Cells(1, 1).Value = 'Group'
    ws.Cells(1, 1).Font.Bold = True

    ws.Cells(1, 2).Value = 'Name'
    ws.Cells(1, 2).Font.Bold = True

    ws.Cells(1, 3).Value = 'UPI'
    ws.Cells(1, 3).Font.Bold = True

    ws.Cells(1, 4).Value = 'Discipline'
    ws.Cells(1, 4).Font.Bold = True

    ws.Cells(1, 5).Value = 'UoA Email'
    ws.Cells(1, 5).Font.Bold = True

    ws.Cells(1, 6).Value = 'GPA'
    ws.Range(ws.Cells(1, 6), ws.Cells(1, 6)).Style = 'Bad'
    ws.Cells(1, 6).Font.Bold = True

    ws.Cells(1, 7).Value = 'Ethnic Group'
    ws.Range(ws.Cells(1, 7), ws.Cells(1, 7)).Style = 'Bad'
    ws.Cells(1, 7).Font.Bold = True

    # Data
    row_index = 1
    for s in students_in_group[g]:
        row_index += 1
        ws.Cells(row_index, 1).Value = g
        ws.Cells(row_index, 2).Value = NAMES[s]
        ws.Cells(row_index, 3).Value = UPI[s]
        ws.Cells(row_index, 4).Value = specialisation[s]
        ws.Cells(row_index, 5).Value = '%s@aucklanduni.ac.nz' % UPI[s]
        ws.Cells(row_index, 6).Value = '%.2f' % gpa[s]
        ws.Range(ws.Cells(row_index, 6), ws.Cells(row_index, 6)).NumberFormat = '0.00'
        ws.Cells(row_index, 7).Value = ethnicity[s]

    # Mean GPA
    row_index += 2
    ws.Cells(row_index, 5).Value = 'Mean GPA'
    ws.Cells(row_index, 5).Font.Bold = True
    ws.Cells(row_index, 6).Value = '%.2f' % gpa_mean_group[g]
    ws.Range(ws.Cells(row_index, 6), ws.Cells(row_index, 6)).NumberFormat = '0.00'

    # Activate and autofit
    ws.Activate()
    ws.Cells.Select()
    Application.Selection.Columns.AutoFit()
    ws.Cells(1, 1).Select()

wb.Worksheets('All_Groups').Activate()
wb.Save()

# Student View
# Create new workbook
Application.Workbooks.Add()
Application.ActiveWorkbook.SaveAs(Filename=save_path_student)
wb = Application.Workbooks(student_workbook_name)

# All groups
wb.Sheets.Add()
wb.ActiveSheet.Name = 'All_Groups'
ws = wb.Worksheets('All_Groups')

# Headers
ws.Cells(1, 1).Value = 'Group'
ws.Cells(1, 1).Font.Bold = True

ws.Cells(1, 2).Value = 'Name'
ws.Cells(1, 2).Font.Bold = True

ws.Cells(1, 3).Value = 'UPI'
ws.Cells(1, 3).Font.Bold = True

ws.Cells(1, 4).Value = 'Discipline'
ws.Cells(1, 4).Font.Bold = True

ws.Cells(1, 5).Value = 'UoA Email'
ws.Cells(1, 5).Font.Bold = True

# Data
row_index = 1
for g in GROUPS:
    for s in students_in_group[g]:
        row_index += 1
        ws.Cells(row_index, 1).Value = g
        ws.Cells(row_index, 2).Value = NAMES[s]
        ws.Cells(row_index, 3).Value = UPI[s]
        ws.Cells(row_index, 4).Value = specialisation[s]
        ws.Cells(row_index, 5).Value = '%s@aucklanduni.ac.nz' % UPI[s]
        # Space between each group
    row_index += 1

ws.Activate()
ws.Cells.Select()
Application.Selection.Columns.AutoFit()
ws.Cells(1, 1).Select()

for sheet in wb.Worksheets:
    if sheet.Name != 'All_Groups':
        print(sheet.Name)
        Application.DisplayAlerts = False
        sheet.Delete()
        Application.DisplayAlerts = True


# Make a sheet for each group
for g in GROUPS:
    count = Application.Worksheets.Count
    wb.Sheets.Add(After=wb.Sheets(count))
    wb_name = 'Group_%s' % g
    wb.ActiveSheet.Name = wb_name
    ws = wb.Worksheets(wb_name)

    # Headers
    ws.Cells(1, 1).Value = 'Group'
    ws.Cells(1, 1).Font.Bold = True

    ws.Cells(1, 2).Value = 'Name'
    ws.Cells(1, 2).Font.Bold = True

    ws.Cells(1, 3).Value = 'UPI'
    ws.Cells(1, 3).Font.Bold = True

    ws.Cells(1, 4).Value = 'Discipline'
    ws.Cells(1, 4).Font.Bold = True

    ws.Cells(1, 5).Value = 'UoA Email'
    ws.Cells(1, 5).Font.Bold = True

    # Data
    row_index = 1
    for s in students_in_group[g]:
        row_index += 1
        ws.Cells(row_index, 1).Value = g
        ws.Cells(row_index, 2).Value = NAMES[s]
        ws.Cells(row_index, 3).Value = UPI[s]
        ws.Cells(row_index, 4).Value = specialisation[s]
        ws.Cells(row_index, 5).Value = '%s@aucklanduni.ac.nz' % UPI[s]

    # Activate
    ws.Activate()
    ws.Cells.Select()
    Application.Selection.Columns.AutoFit()
    ws.Cells(1, 1).Select()

wb.Worksheets('All_Groups').Activate()
wb.Save()
