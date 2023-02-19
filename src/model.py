from pyomo.environ import *
import numpy as np
import math
from collections import Counter
from src.utils import logger


class Problem_Model:
    def __init__(self, nN, nE, nK, nT):

        # model itself
        self.Model = ConcreteModel()

        # model parameters
        self.Model.X = Var(nE, nK, nT, within=NonNegativeReals)
        self.Model.D = Var(nN, nK, nT, bounds=(0, np.inf), within=NonNegativeReals)
        self.Model.H = Var(nN, nK, nT, bounds=(0, np.inf), within=NonNegativeReals)
        self.Model.Q = Var(nN, nK, nT, bounds=(0, np.inf), within=NonNegativeReals)
        self.Model.W = Var(nE, nT, bounds=(0, np.inf), within=NonNegativeReals)
        self.Model.Y = Var(nE, nT, within=Binary)

    def model_initialization(self, nT, nK, nE, nD, Cijkt, edge_dict):

        for t in nT:
            for k in nK:
                for edge in list(edge_dict.keys()):
                    self.Model.X[edge, k, t] = 0

        for k in nK:
            for n in nD:
                self.Model.H[n, k, 0] = 0

        for t in nT:
            for edge in list(edge_dict.keys()):
                self.Model.W[edge, t] = 0
                self.Model.Y[edge, t] = 0

        # Minimum Cost Objective
        self.Model.obj_mincost = 0
        for t in nT:
            for k in nK:
                for i in Cijkt[t][k]:
                    for e in nE:
                        if i[0] == e:
                            self.Model.obj_mincost += i[1] * self.Model.X[e, k, t]

        # Minimum Unsatisfied Objective and its related variable to linearize
        self.Model.obj_unsatisfied = Var(bounds=(0, np.inf), within=NonNegativeReals)
        self.Model.T2 = Var(nD, nD, nK, nT, bounds=(0, np.inf), within=NonNegativeReals)

        logger.info("Model is generated")

        return self.Model


def model_constraints(Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt, alpha):

    Model.constraints = ConstraintList()

    # Needed Structures

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

    cumsum_dict_fin = {}
    for t in nT:
        if t == 0:
            z = dict(Counter(cumsum_dict[t]))
            cumsum_dict_fin[t] = z
        elif 0 < t < len(nT) - 1:
            z = dict(Counter(cumsum_dict[t-1])+Counter(cumsum_dict[t]))
            cumsum_dict_fin[t] = z
        elif t > 0 and t == len(nT) -1:
            z = dict(Counter(cumsum_dict[t - 2]) + Counter(cumsum_dict[t - 1]) + Counter(cumsum_dict[t]))
            cumsum_dict_fin[t] = z

    # UNSATISFIED DEMAND
    difference = 0
    count = len(nD)

    unsatisfied_cumsum = {}
    unsatisfied_cumsum_dict = {}
    for t in nT:
        for k in nK:
            for d1 in nD:
                unsatisfied_cumsum[d1] = Model.H[d1, k, t]

        unsatisfied_cumsum_fin = unsatisfied_cumsum.copy()
        unsatisfied_cumsum_dict[t] = unsatisfied_cumsum_fin

    for t in nT:
        for k in nK:
            for d1 in nD:
                for d2 in nD:
                    if djkt[t][k][d1] > 0 and djkt[t][k][d2] > 0:
                        difference += Model.T2[d1, d2, k, t] / (2 * count ** 2 * mean)
                        Model.constraints.add(Model.H[d1, k, t] >= 0)
                        Model.constraints.add(
                            (unsatisfied_cumsum_dict[t][d1] / cumsum_dict_fin[t][d1] - unsatisfied_cumsum_dict[t][d2] /
                             cumsum_dict_fin[t][d2]) * math.exp(alpha) <= Model.T2[d1, d2, k, t])
                        Model.constraints.add(
                            (unsatisfied_cumsum_dict[t][d1] / cumsum_dict_fin[t][d1] - unsatisfied_cumsum_dict[t][d2] /
                             cumsum_dict_fin[t][d2]) * math.exp(alpha) >= -Model.T2[d1, d2, k, t])
                        Model.constraints.add(Model.T2[d1, d2, k, t] >= 0)

    Model.constraints.add(Model.obj_unsatisfied >= difference / (len(nK) * len(nT)))

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

    logger.info("Constraints are generated")

    return Model


