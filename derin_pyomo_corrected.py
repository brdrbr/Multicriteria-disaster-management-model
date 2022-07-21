from pyomo.environ import *
import numpy as np
import pandas as pd

N = 6  # INPUT
nN = RangeSet(0, N - 1)  # total of 6 nodes
E = 11  # INPUT
nE = RangeSet(0, E - 1)  # total of 11 edges
K = 2  # INPUT
nK = RangeSet(0, K - 1)  # total of 2 commodities
T = 2  # INPUT
nT = RangeSet(0, T - 1)  # total of 2 time periods
D = 2  # INPUT
nD = RangeSet(0, D - 1)  # total of 2 demand nodes
S = 2  # INPUT
nS = RangeSet(0, S - 1)  # total of 2 supply nodes
I = N - D - S
nI = RangeSet(0, I - 1)  # total of 2 intermediate nodes

Ik = [1, 1, 0, 0, 0, 0,
      1, 1, 0, 0, 0, 0]  # supply matrix INPUT
Jk = [0, 0, 0, 0, 1, 1,
      0, 0, 0, 0, 1, 1]  # demand matrix INPUT

B = [1, 2,
     3, 5,
     3, 6,
     6, 5]  # Set of blocked arcs[source, destionation] INPUT

Sikt = [3, 5,
        2, 5,
        1, 5,
        3, 4]
# Newly arrived supply of commodity k at supply node i in period t example units: 5 = 500 litres of water INPUT

djkt = [3, 6,
        3, 5,
        2, 5,
        3, 5]
# Newly arising demand of commodity k at node j in period t INPUT

Cijkt = [1, 2, 1, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 4, 1, 3, 5, 2, 3, 6, 4, 4, 5, 3, 4, 6, 4, 5, 6, 1, 6, 5, 2,
         # period 1 commodity 1
         1, 2, 1, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 4, 1, 3, 5, 2, 3, 6, 4, 4, 5, 3, 4, 6, 4, 5, 6, 1, 6, 5, 2,
         # period 1 commodity 2
         1, 2, 1, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 4, 1, 3, 5, 2, 3, 6, 4, 4, 5, 3, 4, 6, 4, 5, 6, 1, 6, 5, 2,
         # period 2 commodity 1
         1, 2, 1, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 4, 1, 3, 5, 2, 3, 6, 4, 4, 5, 3, 4, 6, 4, 5, 6, 1, 6, 5,
         2]  # period 2 commodity 2 [origin, destination, cost(travel time)] INPUT
# Unit travel time on arc (i,j) for commodity k in period t

uijt = [1, 2, 0, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 4, 1, 3, 5, 0, 3, 6, 0, 4, 5, 3, 4, 6, 4, 5, 6, 1, 6, 5, 0,  # period 1
        1, 2, 0, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 4, 1, 3, 5, 0, 3, 6, 0, 4, 5, 3, 4, 6, 4, 5, 6, 1, 6, 5,
        0]  # period 2  INPUT
# Capacity of arc (i,j) in period t (zero, if arc (i,j) is blocked at time t)

bt = [10, 11]  # Units of road restoration resources in period t  INPUT

aij = [8, 8, 8, 8]  # Number of resources needed to restore blocked arc (i,j)  INPUT

# all of the above are inputs

# -------------------------Main model-------------------------#

Model = ConcreteModel()
Model.X = Var(nE, nK, nT, within=NonNegativeReals)
Model.D = Var(nD, nK, nT, within=NonNegativeReals)
Model.H = Var(nD, nK, nT, within=NonNegativeReals)
Model.W = Var(nE, nT, within=NonNegativeReals)
Model.Y = Var(nE, nT, within=Binary)

alpha = 2  # penalty factor for unsatisfied demand

Model.obj = Objective(
    expr=sum(Cijkt[2 + e * 3 + k * 3 * E + t * 3 * E * T] * Model.X[e, k, t] for e in nE for k in nK for t in nT))


Model.c1 = ConstraintList()
for t in nT:
    for k in nK:
        sum1 = 0
        sum2 = 0
        for s in nS:
            for e in nE:
                print(Cijkt[(0 + e * 3 + k * 3 * E + t * 3 * E * T)-1])

                if s == Cijkt[(0 + e * 3 + k * 3 * E + t * 3 * E * T)-1]:
                    sum1 = sum1 + Model.X[e, k, t]
                if s == Cijkt[1 + e * 3 + k * 3 * E + t * 3 * E * T]:
                    sum2 = sum2 + Model.X[e, k, t]

        Model.c1.add(sum1 - sum2 == Sikt[s + k * S + t * S * K])

for t in nT:
    for k in nK:
        for d in nD:
            sum1 = 0
            sum2 = 0
            for e in nE:

                if d + N - D == Cijkt[0 + e * 3 + k * 3 * E + t * 3 * E * T]:
                    sum1 = sum1 + Model.X[e, k, t]
                if d + N - D == Cijkt[1 + e * 3 + k * 3 * E + t * 3 * E * T]:
                    sum2 = sum2 + Model.X[e, k, t]
        Model.c1.add(sum2 - sum1 + Model.H[d, k, t] == Model.D[d, k, t])


for t in nT:
    for k in nK:
        sum1 = 0
        sum2 = 0
        for i in nI:

            for e in nE:
                if i + D == Cijkt[0 + e * 3 + k * 3 * E + t * 3 * E * T]:
                    sum1 += Model.X[e, k, t]
                if i + D == Cijkt[1 + e * 3 + k * 3 * E + t * 3 * E * T]:
                    sum2 += Model.X[e, k, t]

        Model.c1.add(sum1 - sum2 == 0)


for k in nK:
    for d in nD:
        Model.c1.add(Model.H[d, k, 0] == 0)

for t in nT:
    for k in nK:
        for d in nD:
            Model.c1.add(Model.D[d, k, t] == 0 + djkt[d + k * D + t * D * K])  # Model.H[d,k,t-1]

for t in nT:
    for e in nE:
        for k in nK:
            if uijt[2 + e * 3 + t * 3 * E] != 0:
                Model.c1.add(Model.X[e, k, t] <= uijt[2 + e * 3 + t * 3 * E])

for t in nT:
    for e in nE:
        for k in nK:
            if uijt[2 + e * 3 + t * 3 * E] == 0:
                Model.c1.add(Model.X[e, k, t] <= uijt[2 + e * 3 + t * 3 * E] * Model.Y[e, t])

for t in nT:
    sum1 = 0
    for e in nE:
        if uijt[2 + e * 3 + t * 3 * E] == 0:
            sum1 = sum1 + Model.W[e, t]
    Model.c1.add(sum1 <= bt[t])

for t in nT:
    curlist = []
    counter = -1
    for i in range(0, t + 1):
        curlist.append(i)

    for e in nE:
        if uijt[2 + e * 3 + t * 3 * E] == 0:
            counter = counter + 1
            for c in curlist:
                Model.c1.add(Model.W[e, c] >= aij[counter] * Model.Y[e, t])

Model.obj.pprint()
Model.c1.pprint()

opt = SolverFactory('glpk')
Msolution = opt.solve(Model)

# Display solution
print(Msolution)
print('\nMinimum total travel time = ', Model.obj())
print(Model.X.display())