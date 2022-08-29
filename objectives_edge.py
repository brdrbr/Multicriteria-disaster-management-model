# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 06:08:17 2022
@author: Computer1
"""

## TODO: Optimal degerler esit olunca bir optimal solutionda obur objectiveleri kullanarak tiebreaker sağla, yüzde katsayılarını kullan
## TODO: Her objective için gelen optimal değerler diger objective'lerde nasıl bir sonuc yaratıyor?

from dataread import *
from pyomo.opt import SolverFactory
import math
from utils import *
import numpy as np

stream_solver = False    # True prints solver output to screen
keepfiles = False    # True prints intermediate file names (.nl,.sol,...)

for l in range(0, 3):
    Model = ConcreteModel()
    # Amount of commodity k sent on arc e in period t
    Model.X = Var(nE, nK, nT, within=NonNegativeReals)
    for t in nT:
        for k in nK:
            Model.X[11, k, t] = 0
            Model.X[22, k, t] = 0
            Model.X[33, k, t] = 0
            Model.X[44, k, t] = 0
            Model.X[55, k, t] = 0
            Model.X[66, k, t] = 0

    # Demand of commodity k at node j in period t
    Model.D = Var(nD, nK, nT, bounds=(0, np.inf), within=NonNegativeReals)

    # Unsatisfied demand of commodity k at node j in period t
    Model.H = Var(nD, nK, nT, bounds=(0, np.inf), within=NonNegativeReals)  # 0 for t-1 = 0 case.
    for k in nK:
        Model.H[1, k, 0] = 0
        Model.H[2, k, 0] = 0
        Model.H[3, k, 0] = 0
        Model.H[4, k, 0] = 0
        Model.H[5, k, 0] = 0
        Model.H[6, k, 0] = 0

    # Q = D - H (satisfied demand amount)
    Model.Q = Var(nD, nK, nT, bounds=(0, np.inf), within=NonNegativeReals)

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

     # all objectives for tiebreaking
    Model.objective1 = 0
    for t in nT:
        for k in nK:
            for i in Cijkt[t][k]:
                for e in nE:
                    if i[0] == e:
                        Model.objective1 += i[1] * Model.X[e, k, t]

    alpha = 1
    Model.objective2 = 0
    for t in nT:
        for k in nK:
            for d in nD:
                Model.objective2 += (Model.Q[d, k, t]) * math.exp((-alpha) * t)

    Model.objective3 = Var(bounds=(0, np.inf), within=NonNegativeReals)

    # scaling happens here
    Model.scaling_factor = Suffix(direction=Suffix.EXPORT)
    Model.scaling_factor[Model.objective1] = 105
    Model.scaling_factor[Model.objective2] = 16
    Model.scaling_factor[Model.objective3] = 0.15

    if l == 0:
        # OBJECTIVE 1
        Model.obj = Objective(expr=Model.objective1 + (0.0001 * Model.objective2) + (Model.objective3 * 0.0001), sense=1)
        Model.c1 = ConstraintList()

    elif l == 1:
        # OBJECTIVE 2
        Model.obj = Objective(expr=Model.objective2 + (Model.objective1 * 0.0001) + (Model.objective3 * 0.0001) , sense=-1)
        Model.c1 = ConstraintList()

    else:
        # OBJECTIVE 3
        Model.obj = Objective(expr=Model.objective3 + (Model.objective1 * 0.0001) + (Model.objective2 * 0.0001), sense=-1)
        Model.c1 = ConstraintList()

    # CONSTRAINT 0 for objective 3
    alpha = 1
    obj_sum = 0
    for t in nT:
        for k in nK:
            for d in nD:  # for all demand nodes
                if djkt[t][k][d] > 0:
                    obj_sum += djkt[t][k][d]
            for d in nD:
                if djkt[t][k][d] > 0:
                    Model.c1.add(Model.objective3 <= sum((Model.Q[d, k, t] / obj_sum) * math.exp((-alpha) * t) for k in nK for t in nT) * 0.0001)

    # CONSTRAINT 1
    into = 0
    out = 0
    for t in nT:
        for k in nK:
            for e in nS:  # for all supply nodes
                if Sikt[t][k][e] > 0:
                    for i in edge_dict.keys():
                        if int(str(i)[:-1]) == e:
                            into += Model.X[i, k, t]
                        if int(str(i)[1:2]) == e:
                            out += Model.X[i, k, t]
                    Model.c1.add(into - out == Sikt[t][k][e])
                    into = 0
                    out = 0

    # CONSTRAINT 2
    into = 0
    out = 0
    for t in nT:
        for k in nK:
            for e in nD:  # for all demand nodes
                if djkt[t][k][e] > 0:
                    for i in edge_dict.keys():
                        if int(str(i)[:-1]) == e:
                            out += Model.X[i, k, t]
                        if int(str(i)[1:2]) == e:
                            into += Model.X[i, k, t]
            
                    Model.c1.add(into - out + Model.H[e, k, t] == Model.D[e, k, t])
                    into = 0
                    out = 0

    # CONSTRAINT 3
    for t in nT:
        for k in nK:
            for e in nN:  # for all transition nodes ( neither supply nor demand )
                if Sikt[t][k][e] == 0 and djkt[t][k][e] == 0:
                    for i in edge_dict.keys():
                        if int(str(i)[:-1]) == e:
                            out += Model.X[i, k, t]
                        if int(str(i)[1:2]) == e:
                            into += Model.X[i, k, t]
            
                    Model.c1.add(into - out == 0)
                    into = 0
                    out = 0

    # CONSTRAINT 4
    for t in nT:
        for k in nK:
            for d in nD:
                if t == 0:
                    Model.c1.add(Model.D[d, k, t] == djkt[t][k][d])
                    Model.c1.add(Model.H[d, k, t] <= Model.D[d, k, t])
                    Model.c1.add(Model.Q[d, k, t] == Model.D[d, k, t] - Model.H[d, k, t])
                else:
                    Model.c1.add(Model.D[d, k, t] == Model.H[d, k, t-1] + djkt[t][k][d])
                    Model.c1.add(Model.H[d, k, t] <= Model.D[d, k, t])
                    Model.c1.add(Model.Q[d, k, t] == Model.D[d, k, t] - Model.H[d, k, t])

    # REMOVING BLOCKED ARCS FOR CONSTRAINTS 5 AND 6
    capacities = []
    for t in nT:
        for i in uijt[t]:
            for s in nS:
                for d in nD:
                    if int(str(i[0])[:-1]) == s and int(str(i[0])[1:2]) == d:
                        capacities.append(i[1])

    # CONSTRAINT 5
    for t in nT:
        for index, i in enumerate(uijt[t]):
            if i[1] != 0:  # its not blocked
                Model.c1.add(sum(Model.X[i[0], k, t] for k in nK) <= capacities[index])

    # CONSTRAINT 6
    for t in nT:
        for index, i in enumerate(uijt[t]):
            if i[1] == 0:  # its blocked
                Model.c1.add(sum(Model.X[i[0], k, t] for k in nK) <= capacities[i[1]] * Model.Y[i[0], t])

    # CONSTRAINT 7
    origin_list = []
    destination_list = []
    time_list = []
    for t in nT:
        for index, i in enumerate(uijt[t]):
            if i[1] == 0:  # its blocked
                origin_list.append(int(str(i[0])[:-1]))
                destination_list.append(int(str(i[0])[1:2]))
                time_list.append(t)
    for t in nT:
        Model.c1.add(sum(Model.W[int(str(o)+str(d)), t] for (o, d) in zip(origin_list, destination_list)) <= bt[t])

    # CONSTRAINT 8
    for t in nT:
        nT2 = RangeSet(0, t)
        for index, i in enumerate(uijt[t]): 
            if i[1] == 0:  # its blocked
                Model.c1.add(sum(Model.W[i[0], t2] for t2 in nT2) >= aij[i[0]] * Model.Y[i[0], t])
    
    # CONSTRAINT 9
    for t in nT:
        for k in nK:
            for index, i in enumerate(uijt[t]):
                if i[1] == 0:
                    Model.c1.add(Model.X[int(str(i[0])), k, t] >= 0)
                    Model.c1.add(Model.D[int(str(i[0])[1:2]), k, t] >= 0)
                    Model.c1.add(Model.H[int(str(i[0])[1:2]), k, t] >= 0)
    
    counter = 0
    for t in nT:
        for k in nK:
            for index, i in enumerate(uijt[t]):
                if i[1] != 0:
                    if counter == 2:
                        break
                    Model.c1.add(Model.X[int(str(i[0])), k, t] >= 0)
                    Model.c1.add(Model.D[int(str(i[0])[1:2]), k, t] >= 0)
                    counter += 1

    opt = SolverFactory('glpk')
    Msolution = opt.solve(Model,keepfiles=keepfiles,tee=stream_solver)

    print(f'\nObjective {l+1} Solution = ', Model.obj())

    graph_drawer(nT, nK, nN, nS, Sikt, djkt, Model, l)
    excel_writer(nT, nK, djkt, Model, l)
