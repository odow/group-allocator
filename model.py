# ==========================================
#   Group Allocator
#   Oscar Dowson 2014
#   odow003@aucklanduni.ac.nz
from pulp import *
prob = LpProblem('ENGGEN403', LpMinimize)

# ==========================================
#   Calculated
SPECIALISATIONS = list()
for s in STUDENTS:
    if Spec[s] not in SPECIALISATIONS:
        SPECIALISATIONS.append(Spec[s])

ETHNICITIES = list()
for s in STUDENTS:
    if Ethnicity[s] not in ETHNICITIES:
        ETHNICITIES.append(Ethnicity[s])


GROUPS = range(1, int(ngroups)+1)
SG = [(s, g) for s in STUDENTS for g in GROUPS]

M1 = int(len(STUDENTS)/ngroups)
M2 = M1+1

J2 = int(len(STUDENTS) - M1*ngroups)
J1 = int(ngroups-J2)
GROUPS1 = range(1, J1+1)
GROUPS2 = range(J1+1, int(ngroups)+1)

Smin = {}
for s in SPECIALISATIONS:
    Smin[s] = int(sum([Spec[i].lower()==s.lower() for i in STUDENTS]) / ngroups)

Emin = {}
for e in ETHNICITIES:
    Emin[e] = int(sum([Ethnicity[i].lower()==e.lower() for i in STUDENTS]) / ngroups)

Fmin = int(sum([Gender[i].lower()=='f' for i in STUDENTS]) / ngroups)
GPAmean = sum([Gpa[i] for i in STUDENTS])/len(STUDENTS)

Sart = [(s, g) for s in SPECIALISATIONS for g in GROUPS]
Eart = [(e, g) for e in ETHNICITIES for g in GROUPS]
# =====================
#   Variables
x = LpVariable.dicts('x_var', SG, None, None, LpBinary)
SA = LpVariable.dicts('specialisation_artificial', Sart)
FA = LpVariable.dicts('female_artificial', GROUPS, 0, 500)
EA = LpVariable.dicts('ethnicity_artificial', Eart, 0, 500)
GPAmin = LpVariable('gpamin', 0, 9)
GPAmax = LpVariable('gpamax', 0, 9)
GPAvarmin = LpVariable('gpavarmin', 0, 25)
GPAvarmax = LpVariable('gpavarmax', 0, 25)

# =====================
#   Objective
prob += mean_weight*(GPAmax-GPAmin) + var_weight*(GPAvarmax-GPAvarmin) + 1e4*(spec_weight*lpSum([SA[i] for i in Sart])+ gender_weight*lpSum([FA[i] for i in GROUPS])+ ethnicity_weight*lpSum([EA[i] for i in Eart])),'objective'

# =====================
#   Constraints
for s in STUDENTS:
    prob += lpSum([x[(s,g)] for g in GROUPS])==1,'singleGroup_%s'%s

for g in GROUPS1:
    prob += lpSum([x[(s,g)] for s in STUDENTS]) == M1, 'size_g%d'%g
    prob += lpSum([Gpa[s]*x[(s,g)] for s in STUDENTS]) >= M1*GPAmin, 'cMinGPA_g%d'%g
    prob += lpSum([Gpa[s]*x[(s,g)] for s in STUDENTS]) <= M1*GPAmax, 'cMaxGPA_g%d'%g
    prob += lpSum([pow(Gpa[s]-GPAmean,2)*x[(s,g)] for s in STUDENTS]) >= M1*GPAvarmin, 'cGPAvarmin_g%d'%g
    prob += lpSum([pow(Gpa[s]-GPAmean,2)*x[(s,g)] for s in STUDENTS]) <= M1*GPAvarmax, 'cGPAvarmax_g%d'%g

for g in GROUPS2:
    prob += lpSum([x[(s,g)] for s in STUDENTS]) == M2, 'size_g%d'%g
    prob += lpSum([Gpa[s]*x[(s,g)] for s in STUDENTS]) >= M2*GPAmin, 'cMinGPA_g%d'%g
    prob += lpSum([Gpa[s]*x[(s,g)] for s in STUDENTS]) <= M2*GPAmax, 'cMaxGPA_g%d'%g
    prob += lpSum([pow(Gpa[s]-GPAmean,2)*x[(s,g)] for s in STUDENTS]) >= M2*GPAvarmin, 'cGPAvarmin_g%d'%g
    prob += lpSum([pow(Gpa[s]-GPAmean,2)*x[(s,g)] for s in STUDENTS]) <= M2*GPAvarmax, 'cGPAvarmax_g%d'%g

# Semi-relaxed constraints to enforce gender, specialisation and ethnicity equality
for g in GROUPS:
    prob += lpSum([x[(s,g)] for s in STUDENTS if Gender[s].lower()=='f']) + FA[g] >= Fmin, 'minF_g%d'%g
    for k in SPECIALISATIONS:
        prob += lpSum([x[(s,g)] for s in STUDENTS if Spec[s].lower()==k.lower()]) + SA[(k,g)]>= Smin[k],'min_s%s_g%d'%(k,g)
    for e in ETHNICITIES:
        prob += lpSum([x[(s,g)] for s in STUDENTS if Ethnicity[s].lower()==e.lower()]) + EA[(e,g)]>= Emin[e],'min_e%s_g%d'%(e,g)
    
# =====================
#   Solve
print 'Solving...'
prob.solve(solvers.PULP_CBC_CMD(msg=1,maxSeconds=timelimit))

# =====================
#   Solution
print LpStatus[prob.status]
for s,g in SG:
    if x[(s,g)].value()==1:
        Groups[s]=g
GPADIFF = GPAmax.value()-GPAmin.value()
GPASD = GPAvarmax.value()-GPAvarmin.value()


#Application.ActiveWorkbook.Charts('PuLPSolutionQuality').PivotTable.RefreshTable