# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 06:08:17 2022
@author: Computer1
"""
from declaration_edge import *
#from dataread import *
from pyomo.opt import SolverFactory
import math
import networkx as nx
import matplotlib.pyplot as plt

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
"optimize 1 first, katsayi 1/1000, lexographic, weightlerle sum,scaling objective functoins,scalleri kontrol et"
"optimize1, get the best results for ibj 2 and 3, input network, hangi arclar bloke ve de ne kadar kaldi acilmasina"
"mantikli sonuc veremiycekdata input"
"3 objective degerleri 1 cozum runda"
"her time period icin discount satisfied demand, tabloya dok"
"3. objectivei olusturan nodelarin degerleri"
# OBJECTIVE 1
"""
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
"""
"""
# OBJECTIVE 2
alpha = 1
objective = 0
for t in nT:
    for k in nK:
        for d in nD:
            objective += (Model.D[d, k, t] - Model.H[d, k, t]) * math.exp((-alpha)*t)
# Sense = 1 is maximizing
Model.obj = Objective(expr=objective, sense=-1)
Model.c1 = ConstraintList()
"""

# Z Declaration
Model.Z = Var(bounds=(0, np.inf), within=NonNegativeReals)
# OBJECTIVE 3
objective = Model.Z
Model.obj = Objective(expr=objective, sense=-1)
Model.c1 = ConstraintList()
# CONSTRAINT 0 for objective 3
alpha = 1
for d in nD:  # for all demand nodes
    if djkt[t][k][d] > 0:  
        Model.c1.add( Model.Z <= sum(Model.D[d, k, t] - Model.H[d, k, t] * math.exp((-alpha)*t) for k in nK for t in nT))
"high demand at a specific node, make it easy to "
"her commodity icin demand pointlerin demandinin yuzde kaci satisfy edilmis + how much demand"

"objective 3 degisiminden sonra 3 time period 1 commodity"

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
                Model.c1.add(Model.H[d, k, t] == 0)
                Model.c1.add(Model.D[d, k, t] == djkt[t][k][d])
            else:
                Model.c1.add(Model.D[d, k, t] == Model.H[d, k, t-1] + djkt[t][k][d])


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
    for index, i in enumerate(uijt[t]):  # aij shape: 36
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

Model.obj.pprint()
Model.c1.pprint()

opt = SolverFactory('glpk')
Msolution = opt.solve(Model)
""""supply demand node renkleri farkli yap, transhipment nodes"""
# Display solution
print(Msolution)
print('\nMinimum total travel time = ', Model.obj())
#print(Model.X.display())
#print(Model.D.display())
print(Model.Z.display())
counter = 1
periodcounter = 1
commoditycounter = 1
edgelabeldictionary = {}
for i in nT:
    for j in nK:
        G = nx.Graph()
        for k in nS:
            G.add_node(str(k))
        for k in nS:
            for key, value in Model.X.get_values().items():
                if str(key[0])[0] == str(k) and str(key[1]) == str(i) and str(key[2]) == str(j):
                    if value != 0.0:
                        G.add_edge(str(k), str(key[0])[1], weight = str(value))
                        edgelabeldictionary[k, int(str(key[0])[1])] = str(value)
        plt.figure(counter)
        plt.title("Period: " + str(periodcounter) + " Commodity: " + str(commoditycounter))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, arrows = True)
        nx.draw_networkx_edge_labels(G, pos, edge_labels = nx.get_edge_attributes(G, 'weight'),label_pos=0.5,  rotate=False, font_size=8)
        commoditycounter = commoditycounter+  1
        counter = counter + 1
    commoditycounter = 1
    periodcounter = periodcounter +  1
plt.show()
print(Model.Z.get_values())
