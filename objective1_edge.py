# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 06:08:17 2022

@author: Computer1
"""

from declaration_edge import *
from pyomo.opt import SolverFactory

Model = ConcreteModel()


# Amount of commodity k sent on arc e in period t
Model.X = Var(nE, nK, nT, within=NonNegativeReals)
for t in nT:
    for k in nK:
        Model.X[11, k ,t] = 0
        Model.X[22, k ,t] = 0
        Model.X[33, k ,t] = 0
        Model.X[44, k ,t] = 0
        Model.X[55, k ,t] = 0
        Model.X[66, k ,t] = 0

# Demand of commodity k at node j in period t
Model.D = Var(nD, nK, nT, bounds=(0, np.inf), within=NonNegativeReals)
"""Model.D[1] = djkt[0][0][1]
Model.D[2] = djkt[0][0][2]
Model.D[3] = djkt[0][0][3]
Model.D[4] = djkt[0][0][4]
Model.D[5] = djkt[0][0][5]
Model.D[6] = djkt[0][0][6]"""  # i believe that this is unneccessary due to constraint 4

# Unsatisfied demand of commodity k at node j in period t
Model.H = Var(nD, nK, nT, xbounds=(0, 0), within=NonNegativeReals)  # 0 for t-1 = 0 case.
for k in nK:
    Model.H[1, k, 0] = 0
    Model.H[2, k, 0] = 0
    Model.H[3, k, 0] = 0
    Model.H[4, k, 0] = 0
    Model.H[5, k, 0] = 0
    Model.H[6, k, 0] = 0

# Units of resources allocated to blocked arc e in period t
Model.W = Var(nE, nT, bounds=(0, np.inf), within=NonNegativeReals)
for t in nT:
    Model.W[11, t] = 0
    Model.W[22, t] = 0
    Model.W[33, t] = 0
    Model.W[44, t] = 0
    Model.W[55, t] = 0
    Model.W[66, t] = 0

# 1 if blocked arc e is open in period t, 0, otherwise
Model.Y = Var(nE, nT, within=Binary)
for t in nT:
    Model.Y[11, t] = 0
    Model.Y[22, t] = 0
    Model.Y[33, t] = 0
    Model.Y[44, t] = 0
    Model.Y[55, t] = 0
    Model.Y[66, t] = 0

# OBJECTIVE
objective = 0
for t in nT:
    for k in nK:
        for i in Cijkt[t][k]:
            for e in nE:
                if i[0] == e:
                    objective += i[1]*Model.X[e, k, t]
# Sense = 1 is minimizing
Model.obj = Objective(expr=objective, sense=1)
Model.c1 = ConstraintList()

# CONSTRAINT 1
into = 0
out = 0
for t in nT:
    for k in nK:
        for e in nS:  # for all supply nodes
            if Sikt[t][k][e-1] > 0:
                for i in edge_dict.keys():
                    if int(str(i)[:-1]) == e-1:
                        into += Model.X[i, k, t]
                    if int(str(i)[1:2]) == e-1:
                        out += Model.X[i, k, t]
        
                Model.c1.add(into - out == Sikt[t][k][e-1])
                into = 0
                out = 0


# CONSTRAINT 2
into = 0
out = 0
for t in nT:
    for k in nK:
        for e in nD:  # for all demand nodes
            if djkt[t][k][e-1] > 0:
                for i in edge_dict.keys():
                    if int(str(i)[:-1]) == e-1:
                        out += Model.X[i, k, t]
                    if int(str(i)[1:2]) == e-1:
                        into += Model.X[i, k, t]
        
                Model.c1.add(into - out + Model.H[e-1, k, t] == Model.D[e-1, k, t])
                into = 0
                out = 0


# CONSTRAINT 3
for t in nT:
    for k in nK:
        for e in nN:  # for all transition nodes ( neither supply nor demand )
            if Sikt[t][k][e-1] == 0 and djkt[t][k][e-1] == 0:
                for i in edge_dict.keys():
                    if int(str(i)[:-1]) == e-1:
                        out += Model.X[i, k, t]
                    if int(str(i)[1:2]) == e-1:
                        into += Model.X[i, k, t]
        
                Model.c1.add(into - out == 0)
                into = 0
                out = 0

# CONSTRAINT 4
for t in nT:
    for k in nK:
        for d in nD:
            Model.c1.add(Model.D[d, k, t] == Model.H[d, k, t] + djkt[t][k][d-1])


#MODIFIED CONSTRAINTS TILL HERE

# REMOVING BLOCKED ARCS FOR CONSTRAINTS 5 AND 6
capacities = []
for i in uijt[0][0]:
    for e in nS:
        for k in nD:
            if int(str(i[0])[:-1]) == e and int(str(i[0])[1:2]) == k:
                capacities.append(i[1])

# CONSTRAINT 5
for index, i in enumerate(uijt[0][0]):
    if i[1] != 0:  # its not blocked
        Model.c1.add(Model.X[i[0]] <= capacities[index])

# CONSTRAINT 6
for index, i in enumerate(uijt[0][0]):
    if i[1] == 0:  # its blocked
        Model.c1.add(Model.X[i[0]] <= capacities[index] * Model.Y[i[0]])

# CONSTRAINT 7
origin_list = []
destination_list = []
for index, i in enumerate(uijt[0][0]):
    if i[1] == 0:  # its blocked
        origin_list.append(int(str(i[0])[:-1]))
        destination_list.append(int(str(i[0])[1:2]))

Model.c1.add(sum(Model.W[int(str(o)+str(d))] for (o, d) in zip(origin_list, destination_list)) <= sum([bt[0][a][1] for a in range(len(bt[0]))]))

# CONSTRAINT 8
origin_list = []
destination_list = []
blocked_indexes = []
counter = 0
for index, i in enumerate(uijt[0][0]):
    if i[1] == 0:  # its blocked
        origin_list.append(int(str(i[0])[:-1]))
        destination_list.append(int(str(i[0])[1:2]))
        blocked_indexes.append(counter)
        Model.c1.add(Model.W[i[0]] >= aij[0][0][counter][1] * Model.Y[i[0]])
        counter += 1

# CONSTRAINT 9
for index, i in enumerate(uijt[0][0]):
    if i[1] == 0:
        Model.c1.add(Model.X[int(str(i[0]))] >= 0)
        Model.c1.add(Model.D[int(str(i[0])[1:2])] >= 0)
        Model.c1.add(Model.H[int(str(i[0])[1:2])] >= 0)

counter = 0
for index, i in enumerate(uijt[0][0]):
    if i[1] != 0:
        if counter == 2:
            break
        Model.c1.add(Model.X[int(str(i[0]))] >= 0)
        Model.c1.add(Model.D[int(str(i[0])[1:2])] >= 0)
        Model.c1.add(Model.H[int(str(i[0])[1:2])] >= 0)
        counter += 1

Model.obj.pprint()
Model.c1.pprint()

opt = SolverFactory('glpk')
Msolution = opt.solve(Model)

# Display solution
print(Msolution)
print('\nMinimum total travel time = ', Model.obj())
print(Model.X.display())