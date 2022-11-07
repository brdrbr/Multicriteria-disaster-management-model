"""Version3 on separately discounting periods and considers unsatisfied demands"""
# Here, focus on the cumulative discounting of unsatisfied demands

from dataread import *
from pyomo.opt import SolverFactory
from utils import *
import numpy as np

obj1_results = []
obj3_results = []
obj5_results = []
obj7_results = []

for l in range(0, 7, 2):  # 0 for obj1, 2 for obj3, 4 for obj gini, 6 for obj unsatisfied
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

    # All objectives for tiebreaking
    Model.objective1 = 0
    for t in nT:
        for k in nK:
            for i in Cijkt[t][k]:
                for e in nE:
                    if i[0] == e:
                        Model.objective1 += i[1] * Model.X[e, k, t]

    Model.Z = Var(bounds=(0, np.inf), within=NonNegativeReals)
    Model.unsatisfied_Z = Var(bounds=(0, np.inf), within=NonNegativeReals)
    Model.T = Var(nD, nD, nK, nT, bounds=(0, np.inf), within=NonNegativeReals)

    Model.scaling_factor = Suffix(direction=Suffix.EXPORT)
    Model.scaling_expression = Suffix(direction=Suffix.LOCAL)

    Model.c1 = ConstraintList()

    difference = 0
    count = len(nD)
    mean = 0
    alpha = 0.5
    cumsum = {}
    cumsum_dict = {}
    satisfied_cumsum_d1 = 0
    satisfied_cumsum_d2 = {}

    for t in nT:
        for k in nK:
            tmp = np.array(list(Sikt[t][k].values()))
            mean = np.sum(tmp) / count
            for d1 in nD:
                cumsum[d1] = djkt[t][k][d1]

        cumsum_fin = cumsum.copy()
        cumsum_dict[t] = cumsum_fin

    satisfied_cumsum = {}
    satisfied_cumsum_dict = {}
    for t in nT:
        for k in nK:
            for d1 in nD:
                satisfied_cumsum[d1] = Model.Q[d1, k, t]

        satisfied_cumsum_fin = satisfied_cumsum.copy()
        satisfied_cumsum_dict[t] = satisfied_cumsum_fin

    for t in nT:
        for k in nK:
            for d1 in nD:
                for d2 in nD:
                    if djkt[t][k][d1] > 0 and djkt[t][k][d2] > 0:
                        difference += Model.T[d1, d2, k, t] / (2 * count ** 2 * mean)
                        Model.c1.add(Model.Q[d1, k, t] >= 0)
                        Model.c1.add((satisfied_cumsum_dict[t][d1] / cumsum_dict[t][d1] - satisfied_cumsum_dict[t][d2] /
                                      cumsum_dict[t][d2]) * math.exp(-alpha * t) <= Model.T[d1, d2, k, t])
                        Model.c1.add((satisfied_cumsum_dict[t][d1] / cumsum_dict[t][d1] - satisfied_cumsum_dict[t][d2] /
                                      cumsum_dict[t][d2]) * math.exp(-alpha * t) >= -Model.T[d1, d2, k, t])
                        Model.c1.add(Model.T[d1, d2, k, t] >= 0)

    Model.gini = difference / (len(nK) * len(nT))

    # TODO: Make them generic!
    max1 = 701.0825298228901
    min1 = 148.0
    max3 = 0.62955857291689
    min3 = 0.1
    max5 = 0.005510527853700961
    min5 = -1.1765422144540742e-19
    max7 = 1.93762215676693
    min7 = 1.25559988958859

    Model.scaling_factor[Model.objective1] = 1 / (max1 - min1)
    Model.scaling_factor[Model.Z] = 1 / (max3 - min3)
    Model.scaling_factor[Model.gini] = 1 / (max5 - min5)
    Model.scaling_factor[Model.unsatisfied_Z] = 1 / (max7 - min7)

    if l == 0:
        # OBJECTIVE 1

        Model.obj = Objective(expr=(((Model.objective1 - min1) * Model.scaling_factor[Model.objective1]) +
                                   (-(Model.Z - min3) * 0.001 * Model.scaling_factor[Model.Z]) +
                                   ((Model.unsatisfied_Z - min7) * 0.001 * Model.scaling_factor[Model.unsatisfied_Z]) +
                                   ((Model.gini - min5) * 0.001 * Model.scaling_factor[Model.gini])), sense=1)  # min cost

    elif l == 2:
        # OBJECTIVE 3
        Model.obj = Objective(expr=(((Model.Z - min3) * Model.scaling_factor[Model.Z]) +
                                   (-(Model.gini - min5) * Model.scaling_factor[Model.gini] * 0.001) +
                                   ((-(Model.objective1 - min1) * Model.scaling_factor[Model.objective1]) * 0.001)+
                                   (-(Model.unsatisfied_Z - min7) * 0.001 * Model.scaling_factor[Model.unsatisfied_Z])),
                                    sense=-1)  # max fairness

    elif l == 4:
        # OBJECTIVE 4 (gini)
        Model.obj = Objective(expr=(((Model.gini - min5) * Model.scaling_factor[Model.gini]) +
                                   (-(Model.Z - min3) * Model.scaling_factor[Model.Z]) * 0.001 +
                                   (((Model.objective1 - min1) * Model.scaling_factor[Model.objective1]) * 0.001)+
                                   ((Model.unsatisfied_Z - min7) * 0.001 * Model.scaling_factor[Model.unsatisfied_Z])),
                                    sense=1)  # min gini

    elif l == 6:
        Model.obj = Objective(expr=(((Model.gini - min5) * Model.scaling_factor[Model.gini] * 0.001) +
                                    (-(Model.Z - min3) * Model.scaling_factor[Model.Z]) * 0.001 +
                                    (((Model.objective1 - min1) * Model.scaling_factor[Model.objective1]) * 0.001) +
                                    ((Model.unsatisfied_Z - min7) * Model.scaling_factor[Model.unsatisfied_Z])),
                              sense=1)  # min unsatisfied demand

    # CONSTRAINT 0 for objective 3 & unsatisfied demand
    alpha = 0.5
    cumsum = 0
    satisfied_cumsum = 0
    unsatisfied_cumsum = 0
    part = 0
    unsat_part = 0

    for d in nD:
        for k in nK:
            for t in nT:
                if djkt[t][k][d] > 0:
                    cumsum += djkt[t][k][d] # cumulative sum
                    satisfied_cumsum += Model.Q[d, k, t]
                    unsatisfied_cumsum = cumsum - satisfied_cumsum

                    part += ((satisfied_cumsum / cumsum)) * math.exp((-alpha * t))
                    unsat_part += ((unsatisfied_cumsum / cumsum)) * math.exp((-alpha * (np.max(nT)-t)))

                    if t == len(nT) - 1:

                        Model.c1.add(Model.Z <= part)
                        Model.c1.add(Model.unsatisfied_Z >= unsat_part)

                        cumsum = 0
                        satisfied_cumsum = 0
                        unsatisfied_cumsum = 0
                        part = 0
                        unsat_part = 0

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
                    Model.c1.add(Model.D[d, k, t] == Model.H[d, k, t - 1] + djkt[t][k][d])
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
        Model.c1.add(sum(Model.W[int(str(o) + str(d)), t] for (o, d) in zip(origin_list, destination_list)) <= bt[t])

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
    Msolution = opt.solve(Model)

    print(f'\nScaled Objective {l + 1} Solution = ', Model.obj())

    graph_drawer(nT, nK, nN, nS, Sikt, djkt, Model, l)
    excel_writer(nT, nK, nS, djkt, Model, l)

    print(" ")

    print("Scaled Solutions:")
    print("Result of objective 1 only: ", (Model.objective1() - min1) * Model.scaling_factor[Model.objective1])
    print("Result of objective 3 only: ", (Model.Z() - min3) * Model.scaling_factor[Model.Z])
    print("Result of objective gini only: ", (Model.gini() - min5) * Model.scaling_factor[Model.gini])
    print("Result of objective unsatisfied demand only: ", (Model.unsatisfied_Z() - min7) * Model.scaling_factor[Model.unsatisfied_Z])

    print(" ")

    print("Unscaled Solutions:")
    print("Result of objective 1 only: ", Model.objective1())
    print("Result of objective 3 only: ", Model.Z())
    print("Result of objective gini only: ", Model.gini())
    print("Result of objective unsatisfied demand only: ", Model.unsatisfied_Z())

    obj1_results.append(Model.objective1())
    obj3_results.append(Model.Z())
    obj5_results.append(Model.gini())
    obj7_results.append(Model.unsatisfied_Z())


    print(" ")
    print(" ************ ")
    print(" ")