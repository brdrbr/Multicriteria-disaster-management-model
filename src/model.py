from pyomo.environ import *
import numpy as np
import math
from time import sleep
import warnings
warnings.filterwarnings("ignore")


class ProblemModel:
    def __init__(self, nN, nE, nK, nT, nD):

        # model itself
        self.Model = ConcreteModel()

        # model parameters
        self.Model.X = Var(nE, nK, nT, within=NonNegativeReals)
        self.Model.D = Var(nN, nK, nT, bounds=(0, np.inf), within=NonNegativeReals)
        self.Model.H = Var(nN, nK, nT, bounds=(0, np.inf), within=NonNegativeReals)
        self.Model.Q = Var(nN, nK, nT, bounds=(0, np.inf), within=NonNegativeReals)
        self.Model.W = Var(nE, nT, bounds=(0, np.inf), within=NonNegativeReals)
        self.Model.Y = Var(nE, nT, within=Binary)

    def model_initialization(self, nN, nT, nK, nE, nD, Cijkt, edge_dict):

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

        # All objectives for tie-breaking
        self.Model.obj_mincost = 0
        for t in nT:
            for k in nK:
                for i in Cijkt[t][k]:
                    for e in nE:
                        if str(i) in str(e):
                            self.Model.obj_mincost += self.Model.X[e, k, t] * Cijkt[t][k][i]

        self.Model.obj_unsatisfied = 0
        self.Model.Z_fairness = Var(bounds=(0, np.inf), within=NonNegativeReals)
        self.Model.T = Var(nD, nD, nK, nT, bounds=(0, np.inf), within=NonNegativeReals)

        print("Model is generated")

        return self.Model


def model_constraints(Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt, k1_nodes, k2_nodes, alpha):

    Model.constraints = ConstraintList()

    difference = 0
    count = {}
    for k in nK:
        if k == 0:
            count[k] = len(k1_nodes)
        elif k == 1:
            count[k] = len(k2_nodes)

    mean = 0
    cumsum = {}
    cumsum_dict = {}

    for t in nT:
        for k in nK:
            tmp = np.array(list(Sikt[t][k].values()))
            mean = np.sum(tmp) / count[k]
            for d1 in nD:
                if djkt[t][k][d1] > 0:
                    cumsum[d1] = djkt[t][k][d1]

        cumsum_fin = cumsum.copy()
        cumsum_dict[t] = cumsum_fin

    satisfied_cumsum = {}
    satisfied_cumsum_dict = {}
    for t in nT:
        for k in nK:
            for d1 in nD:
                if djkt[t][k][d1] > 0:
                    satisfied_cumsum[d1] = Model.Q[d1, k, t]

        satisfied_cumsum_fin = satisfied_cumsum.copy()
        satisfied_cumsum_dict[t] = satisfied_cumsum_fin

    for t in nT:
        for k in nK:
            for d1 in nD:
                for d2 in nD:
                    if djkt[t][k][d1] > 0 and djkt[t][k][d2] > 0:

                        difference += Model.T[d1, d2, k, t] / (2 * count[k] ** 2 * mean)
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
    part_fairness = 0

    # Handling fairness
    for d in nD:
        for k in nK:
            for t in nT:
                if djkt[t][k][d] > 0:
                    cumsum += djkt[t][k][d]  # cumulative sum
                    satisfied_cumsum += Model.Q[d, k, t]
                    part_fairness += (satisfied_cumsum / cumsum) * math.exp(-alpha * t)

                    if t == len(nT) - 1:
                        Model.constraints.add(Model.Z_fairness <= part_fairness)
                        cumsum = 0
                        satisfied_cumsum = 0
                        part_fairness = 0

    # TODO: HANDLE UNSATISFIED DEMAND IN A BETTER WAY (THE RESULT SHOULD BE LIKE GINI)
    unsatisfied_percentage = 0
    cumsum_dict_v2 = {}

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
                unsatisfied_percentage += (Model.H[key, k, t] / cumsum_dict_v2[key])

            unsatisfied_percentage = (unsatisfied_percentage * math.exp(alpha))
            Model.obj_unsatisfied += unsatisfied_percentage
            unsatisfied_percentage = 0

    # CONSTRAINTS

    # CONSTRAINT 1
    into = 0
    out = 0
    for t in nT:
        for k in nK:
            for e in nS:  # for all supply nodes
                if Sikt[t][k][e] > 0:
                    for i in edge_dict.keys():
                        if str(i).find(str(e)) == 0:
                            into += Model.X[i, k, t]
                        elif str(i).find(str(e)) > 0:
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
                        if str(i).find(str(e)) == 0:
                            into += Model.X[i, k, t]
                        elif str(i).find(str(e)) > 0:
                            out += Model.X[i, k, t]

                    Model.constraints.add(into - out + Model.H[e, k, t] == Model.D[e, k, t])
                    into = 0
                    out = 0

    # CONSTRAINT 3
    into = 0
    out = 0
    for t in nT:
        for k in nK:
            for e in nN:  # for all transition nodes ( neither supply nor demand )
                if Sikt[t][k][e] == 0 and djkt[t][k][e] == 0:
                    for i in edge_dict.keys():
                        if str(i).find(str(e)) == 0:
                            into += Model.X[i, k, t]
                        elif str(i).find(str(e)) > 0:
                            out += Model.X[i, k, t]

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

    # CONSTRAINT 5
    for t in nT:
        for index, i in enumerate(uijt[t]):
            if uijt[t][i] != 0:  # its not blocked
                Model.constraints.add(sum(Model.X[i, k, t] for k in nK) <= uijt[t][i])  # capacities

    # CONSTRAINT 6
    for t in nT:
        for index, i in enumerate(uijt[t]):
            if uijt[t][i] == 0:   # its blocked
                Model.constraints.add(sum(Model.X[i, k, t] for k in nK) <= uijt[t][i] * Model.Y[i, t])

    # CONSTRAINT 7
    time_list = []
    edge_list = []
    for t in nT:
        for index, i in enumerate(uijt[t]):
            if uijt[t][i] == 0:  # its blocked
                edge_list.append(i)
                time_list.append(t)

    for t in nT:
        try:
            Model.constraints.add(
                sum(Model.W[edge, t] for edge in edge_list) <= bt[t])
        except:
            continue

    # CONSTRAINT 8
    for t in nT:
        nT2 = RangeSet(0, t)
        for index, i in enumerate(uijt[t]):
            if uijt[t][i] == 0:  # its blocked
                Model.constraints.add(sum(Model.W[i, t2] for t2 in nT2) >= 10 * Model.Y[i, t])

    # CONSTRAINT 9
    for t in nT:
        for k in nK:
            for index, i in enumerate(uijt[t]):
                if uijt[t][i] == 0:
                    Model.constraints.add(Model.X[i, k, t] >= 0)
                    for n in nN:
                        if str(i).find(str(n)) == 0:
                            Model.constraints.add(Model.D[n, k, t] >= 0)
                            Model.constraints.add(Model.H[n, k, t] >= 0)

    counter = 0
    for t in nT:
        for k in nK:
            for index, i in enumerate(uijt[t]):
                if uijt[t][i] > 0:
                    if counter == 2:
                        break
                    for n in nN:
                        if str(i).find(str(n)) == 0:
                            Model.constraints.add(Model.D[n, k, t] >= 0)
                    Model.constraints.add(Model.X[i, k, t] >= 0)
                    counter += 1

    print("Constraints are done")

    return Model

