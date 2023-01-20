from pyomo.environ import *
import numpy as np
import math


class Problem_Model:
    def __init__(self, nE, nK, nT, nD):

        # model itself
        self.Model = ConcreteModel()

        # model parameters
        self.Model.X = Var(nE, nK, nT, within=NonNegativeReals)
        self.Model.D = Var(nD, nK, nT, bounds=(0, np.inf), within=NonNegativeReals)
        self.Model.H = Var(nD, nK, nT, bounds=(0, np.inf), within=NonNegativeReals)
        self.Model.Q = Var(nD, nK, nT, bounds=(0, np.inf), within=NonNegativeReals)
        self.Model.W = Var(nE, nT, bounds=(0, np.inf), within=NonNegativeReals)
        self.Model.Y = Var(nE, nT, within=Binary)

    def model_initialization(self, nT, nK, nE, nD, Cijkt):

        for t in nT:
            for k in nK:
                self.Model.X[11, k, t] = 0
                self.Model.X[22, k, t] = 0
                self.Model.X[33, k, t] = 0
                self.Model.X[44, k, t] = 0
                self.Model.X[55, k, t] = 0
                self.Model.X[66, k, t] = 0

        for k in nK:
            self.Model.H[1, k, 0] = 0
            self.Model.H[2, k, 0] = 0
            self.Model.H[3, k, 0] = 0
            self.Model.H[4, k, 0] = 0
            self.Model.H[5, k, 0] = 0
            self.Model.H[6, k, 0] = 0

        for t in nT:
            self.Model.W[11, t] = 0
            self.Model.W[22, t] = 0
            self.Model.W[33, t] = 0
            self.Model.W[44, t] = 0
            self.Model.W[55, t] = 0
            self.Model.W[66, t] = 0

        for t in nT:
            self.Model.Y[11, t] = 0
            self.Model.Y[22, t] = 0
            self.Model.Y[33, t] = 0
            self.Model.Y[44, t] = 0
            self.Model.Y[55, t] = 0
            self.Model.Y[66, t] = 0

        # All objectives for tiebreaking
        Model.obj_mincost = 0
        for t in nT:
            for k in nK:
                for i in Cijkt[t][k]:
                    for e in nE:
                        if i[0] == e:
                            self.Model.obj_mincost += i[1] * self.Model.X[e, k, t]

        # For fairness and min unsatisfied demand objectives
        self.Model.Z_fairness = Var(bounds=(0, np.inf), within=NonNegativeReals)
        self.Model.Z_unsatisfied = Var(bounds=(0, np.inf), within=NonNegativeReals)
        # For gini non-linearity handling
        self.Model.T = Var(nD, nD, nK, nT, bounds=(0, np.inf), within=NonNegativeReals)

        return self.Model


def model_constraints(Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt, alpha):

    Model.constraints = ConstraintList()

    difference = 0
    count = len(nD)
    mean = 0
    cumsum = {}
    cumsum_dict = {}

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
                        Model.constraints.add(Model.Q[d1, k, t] >= 0)
                        Model.constraints.add(
                            (satisfied_cumsum_dict[t][d1] / cumsum_dict[t][d1] - satisfied_cumsum_dict[t][d2] /
                             cumsum_dict[t][d2]) * math.exp(-alpha * t) <= Model.T[d1, d2, k, t])
                        Model.constraints.add(
                            (satisfied_cumsum_dict[t][d1] / cumsum_dict[t][d1] - satisfied_cumsum_dict[t][d2] /
                             cumsum_dict[t][d2]) * math.exp(-alpha * t) >= -Model.T[d1, d2, k, t])
                        Model.constraints.add(Model.T[d1, d2, k, t] >= 0)

    Model.obj_gini = difference / (len(nK) * len(nT))

    # CONSTRAINT 0 for maximizing fairness
    cumsum = 0
    satisfied_cumsum = 0
    part = 0
    part2 = 0

    # Handling fairness
    for d in nD:
        for k in nK:
            for t in nT:
                if djkt[t][k][d] > 0:
                    cumsum += djkt[t][k][d]  # cumulative sum
                    satisfied_cumsum += Model.Q[d, k, t]
                    part += (((cumsum - satisfied_cumsum) / cumsum)) * math.exp((alpha))
                    part2 += (((satisfied_cumsum) / cumsum)) * math.exp((-alpha * (t+1)))

                    if t == len(nT) - 1:
                        #Model.constraints.add(Model.Z_unsatisfied >= part)
                        Model.constraints.add(Model.Z_fairness <= part2)
                        cumsum = 0
                        satisfied_cumsum = 0
                        part2 = 0

    # TODO: HANDLE UNSATISFIED DEMAND IN A BETTER WAY (SHOULD BE EQUAL TO THE GINI)
    unsatisfied_percentage = 0
    cumsum_dict_v2 = {}
    constraint = []
    for t in nT:
        for k in nK:
            for d in nD:
                if djkt[t][k][d] > 0:

                    counter = 0
                    if d in cumsum_dict_v2.keys():
                        cumsum_dict_v2[d] += cumsum_dict[t][d]
                        counter += 1
                    else:
                        cumsum_dict_v2[d] = cumsum_dict[t][d]
                        counter += 1

            for key in cumsum_dict_v2.keys():
                unsatisfied_percentage += Model.H[key, k, t] / cumsum_dict_v2[key]

            unsatisfied_percentage = (unsatisfied_percentage * math.exp(alpha))
            constraint.append(unsatisfied_percentage)
            unsatisfied_percentage = 0

    constraint_fin = 0
    for i in constraint:
        constraint_fin += i
        Model.constraints.add(Model.Z_unsatisfied >= i)

    # CONSTRAINTS

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
                    Model.constraints.add(into - out == Sikt[t][k][e])
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

                    Model.constraints.add(into - out + Model.H[e, k, t] == Model.D[e, k, t])
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

                    Model.constraints.add(into - out == 0)
                    into = 0
                    out = 0

    # CONSTRAINT 4
    for t in nT:
        for k in nK:
            for d in nD:
                if t == 0:
                    Model.constraints.add(Model.D[d, k, t] == djkt[t][k][d])
                    Model.constraints.add(Model.H[d, k, t] <= Model.D[d, k, t])
                    Model.constraints.add(Model.Q[d, k, t] == Model.D[d, k, t] - Model.H[d, k, t])
                else:
                    Model.constraints.add(Model.D[d, k, t] == Model.H[d, k, t - 1] + djkt[t][k][d])
                    Model.constraints.add(Model.H[d, k, t] <= Model.D[d, k, t])
                    Model.constraints.add(Model.Q[d, k, t] == Model.D[d, k, t] - Model.H[d, k, t])

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
                Model.constraints.add(sum(Model.X[i[0], k, t] for k in nK) <= capacities[index])

    # CONSTRAINT 6
    for t in nT:
        for index, i in enumerate(uijt[t]):
            if i[1] == 0:  # its blocked
                Model.constraints.add(sum(Model.X[i[0], k, t] for k in nK) <= capacities[i[1]] * Model.Y[i[0], t])

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
        Model.constraints.add(
            sum(Model.W[int(str(o) + str(d)), t] for (o, d) in zip(origin_list, destination_list)) <= bt[t])

    # CONSTRAINT 8
    for t in nT:
        nT2 = RangeSet(0, t)
        for index, i in enumerate(uijt[t]):
            if i[1] == 0:  # its blocked
                Model.constraints.add(sum(Model.W[i[0], t2] for t2 in nT2) >= aij[i[0]] * Model.Y[i[0], t])

    # CONSTRAINT 9
    for t in nT:
        for k in nK:
            for index, i in enumerate(uijt[t]):
                if i[1] == 0:
                    Model.constraints.add(Model.X[int(str(i[0])), k, t] >= 0)
                    Model.constraints.add(Model.D[int(str(i[0])[1:2]), k, t] >= 0)
                    Model.constraints.add(Model.H[int(str(i[0])[1:2]), k, t] >= 0)

    counter = 0
    for t in nT:
        for k in nK:
            for index, i in enumerate(uijt[t]):
                if i[1] != 0:
                    if counter == 2:
                        break
                    Model.constraints.add(Model.X[int(str(i[0])), k, t] >= 0)
                    Model.constraints.add(Model.D[int(str(i[0])[1:2]), k, t] >= 0)
                    counter += 1
    return Model


