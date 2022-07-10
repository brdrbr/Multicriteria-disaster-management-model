from variables import *
from pyomo.opt import SolverFactory


Model = ConcreteModel()

# We need time periods too. I kept it as 1 for simplicity.
# I also kept commodity number as 1 for simplicity.

# Amount of commodity k sent on arc (i,j) in period t
Model.X = Var(nS, nD, within=NonNegativeReals)
# I assumed nodes cannot feed themselves, we can remove these...
Model.X[1, 1] = 0
Model.X[2, 2] = 0
Model.X[3, 3] = 0
Model.X[4, 4] = 0
Model.X[5, 5] = 0
Model.X[6, 6] = 0

# Demand of commodity k at node j in period t
Model.D = Var(nD, bounds=(0, np.inf), within=NonNegativeReals)
Model.D[1] = djkt[0][0][1]
Model.D[2] = djkt[0][0][2]
Model.D[3] = djkt[0][0][3]
Model.D[4] = djkt[0][0][4]
Model.D[5] = djkt[0][0][5]
Model.D[6] = djkt[0][0][6]


# Unsatisfied demand of commodity k at node j in period t
Model.H = Var(nD, bounds=(0, 0), within=NonNegativeReals) # 0 for t-1 = 0 case.
Model.H[1] = 0
Model.H[2] = 0
Model.H[3] = 0
Model.H[4] = 0
Model.H[5] = 0
Model.H[6] = 0

# Units of resources allocated to blocked arc (i,j) in period t
Model.W = Var(nS, nD, bounds=(0, np.inf), within=NonNegativeReals)
Model.W[1, 1] = 0
Model.W[2, 2] = 0
Model.W[3, 3] = 0
Model.W[4, 4] = 0
Model.W[5, 5] = 0
Model.W[6, 6] = 0

# 1 if blocked arc (i,j) is open in period t, 0, otherwise
Model.Y = Var(nS, nD, within=Binary)
Model.Y[1, 1] = 0
Model.Y[2, 2] = 0
Model.Y[3, 3] = 0
Model.Y[4, 4] = 0
Model.Y[5, 5] = 0
Model.Y[6, 6] = 0

# OBJECTIVE
objective = 0
for i in Cijkt[0][0]:
    for e in nS:
        for k in nD:
            if i[0] == e and i[1] == k:
                objective += i[2]*Model.X[e, k]
# Sense = 1 is minimizing
Model.obj = Objective(expr=objective, sense=1)
Model.c1 = ConstraintList()


# CONSTRAINT 1
for e in Ik[0]:  # for all supply nodes
    if e in [1, 2]:
        Model.c1.add(sum(Model.X[e, k] - Model.X[k, e] for k in nD) == Sikt[0][0][e])


# CONSTRAINT 2
for e in Jk[0]:  # for all demand nodes
    if e in [3, 4]:
        Model.c1.add((sum(Model.X[k, e] - Model.X[e, k] for k in nS) + Model.H[e] == Model.D[e]))


# CONSTRAINT 3
for e in Tk[0]:  # for all transition nodes ( neither supply nor demand )
    if e in [5, 6]:
        Model.c1.add(sum(Model.X[k, e] for k in nS) - sum(Model.X[e, k] for k in nS) == 0)


# CONSTRAINT 4 - I removed this for now, since we only consider 1 time period.
for d in nD:
    # assume for now t-1 = 0
    Model.c1.add(Model.D[d] == Model.H[d] + djkt[0][0][d])


# REMOVING BLOCKED ARCS FOR CONSTRAINTS 5 AND 6
capacities = []
for i in uijt[0][0]:
    for e in nS:
        for k in nD:
            if i[0] == e and i[1] == k:
                capacities.append(i[2])

# CONSTRAINT 5
for index, i in enumerate(uijt[0][0]):
    if i[2] != 0:  # its not blocked
        Model.c1.add(Model.X[i[0], i[1]] <= capacities[index])


# CONSTRAINT 6
for index, i in enumerate(uijt[0][0]):
    if i[2] == 0:  # its blocked
        Model.c1.add(Model.X[i[0], i[1]] <= capacities[index] * Model.Y[i[0], i[1]])


# CONSTRAINT 7
origin_list = []
destination_list = []
for index, i in enumerate(uijt[0][0]):
    if i[2] == 0:  # its blocked
        origin_list.append(i[0])
        destination_list.append(i[1])
Model.c1.add(sum(Model.W[o, d] for (o, d) in zip(origin_list, destination_list)) <= sum([bt[0][a][2] for a in range(len(bt[0]))]))


# CONSTRAINT 8
origin_list = []
destination_list = []
blocked_indexes = []
counter = 0
for index, i in enumerate(uijt[0][0]):
    if i[2] == 0:  # its blocked
        origin_list.append(i[0])
        destination_list.append(i[1])
        blocked_indexes.append(counter)
        Model.c1.add(Model.W[i[0], i[1]] >= aij[0][0][counter][2] * Model.Y[i[0], i[1]])
        counter += 1


# CONSTRAINT 9
for index, i in enumerate(uijt[0][0]):
    if i[2] == 0:
        Model.c1.add(Model.X[i[0], i[1]] >= 0)
        Model.c1.add(Model.D[i[1]] >= 0)
        Model.c1.add(Model.H[i[1]] >= 0)

counter = 0
for index, i in enumerate(uijt[0][0]):
    if i[2] != 0:
        if counter == 2:
            break
        Model.c1.add(Model.X[i[0], i[1]] >= 0)
        Model.c1.add(Model.D[i[1]] >= 0)
        Model.c1.add(Model.H[i[1]] >= 0)
        counter += 1

Model.obj.pprint()
Model.c1.pprint()

opt = SolverFactory('glpk')
Msolution = opt.solve(Model)

# Display solution
print(Msolution)
print('\nMinimum total travel time = ', Model.obj())
print(Model.X.display())