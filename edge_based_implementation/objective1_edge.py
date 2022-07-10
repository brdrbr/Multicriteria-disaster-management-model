from edge_based_implementation.declaration_edge import *
from pyomo.opt import SolverFactory

Model = ConcreteModel()

# We need time periods too. I kept it as 1 for simplicity.
# I also kept commodity number as 1 for simplicity.

# Amount of commodity k sent on arc e in period t
Model.X = Var(nE, within=NonNegativeReals)
Model.X[11] = 0
Model.X[22] = 0
Model.X[33] = 0
Model.X[44] = 0
Model.X[55] = 0
Model.X[66] = 0

# Demand of commodity k at node j in period t
Model.D = Var(nD, bounds=(0, np.inf), within=NonNegativeReals)
Model.D[1] = djkt[0][0][1]
Model.D[2] = djkt[0][0][2]
Model.D[3] = djkt[0][0][3]
Model.D[4] = djkt[0][0][4]
Model.D[5] = djkt[0][0][5]
Model.D[6] = djkt[0][0][6]

# Unsatisfied demand of commodity k at node j in period t
Model.H = Var(nD, bounds=(0, 0), within=NonNegativeReals)  # 0 for t-1 = 0 case.
Model.H[1] = 0
Model.H[2] = 0
Model.H[3] = 0
Model.H[4] = 0
Model.H[5] = 0
Model.H[6] = 0

# Units of resources allocated to blocked arc e in period t
Model.W = Var(nE, bounds=(0, np.inf), within=NonNegativeReals)
Model.W[11] = 0
Model.W[22] = 0
Model.W[33] = 0
Model.W[44] = 0
Model.W[55] = 0
Model.W[66] = 0

# 1 if blocked arc e is open in period t, 0, otherwise
Model.Y = Var(nE, within=Binary)
Model.Y[11] = 0
Model.Y[22] = 0
Model.Y[33] = 0
Model.Y[44] = 0
Model.Y[55] = 0
Model.Y[66] = 0

# OBJECTIVE
objective = 0
for i in Cijkt[0][0]:
    for e in nE:
        if i[0] == e:
            objective += i[1]*Model.X[e]
# Sense = 1 is minimizing
Model.obj = Objective(expr=objective, sense=1)
Model.c1 = ConstraintList()

# CONSTRAINT 1
into = 0
out = 0
for e in nS:  # for all supply nodes
    if Sikt[0][0][e] > 0:
        for i in edge_dict.keys():
            if int(str(i)[:-1]) == e:
                into += Model.X[i]
            if int(str(i)[1:2]) == e:
                out += Model.X[i]

        Model.c1.add(into - out == Sikt[0][0][e])
        into = 0
        out = 0


# CONSTRAINT 2
into = 0
out = 0
for e in nD:  # for all demand nodes
    if djkt[0][0][e] > 0:
        for i in edge_dict.keys():
            if int(str(i)[:-1]) == e:
                out += Model.X[i]
            if int(str(i)[1:2]) == e:
                into += Model.X[i]

        Model.c1.add(into - out + Model.H[e] == Model.D[e])
        into = 0
        out = 0


# CONSTRAINT 3
for e in nN:  # for all transition nodes ( neither supply nor demand )
    if Sikt[0][0][e] == 0 and djkt[0][0][e] == 0:
        for i in edge_dict.keys():
            if int(str(i)[:-1]) == e:
                out += Model.X[i]
            if int(str(i)[1:2]) == e:
                into += Model.X[i]

        Model.c1.add(into - out == 0)
        into = 0
        out = 0

# CONSTRAINT 4
for d in nD:
    Model.c1.add(Model.D[d] == Model.H[d] + djkt[0][0][d])

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