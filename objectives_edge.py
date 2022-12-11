from dataread import *
from pyomo.opt import SolverFactory
from utils import *
import numpy as np

obj1_results = []
obj3_results = []
obj5_results = []
obj7_results = []

# for generic scaling of the solutions
for counter_scaling in range(0, 2):

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

        if counter_scaling != 0:
            Model.scaling_factor = Suffix(direction=Suffix.EXPORT)
            Model.scaling_expression = Suffix(direction=Suffix.LOCAL)

        Model.c1 = ConstraintList()

        difference = 0
        count = len(nD)
        mean = 0
        alpha = 0.3
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

        if counter_scaling != 0:
            max1 = np.max(obj1_results)
            min1 = np.min(obj1_results)
            max3 = np.max(obj3_results)
            min3 = np.min(obj3_results)
            max5 = np.max(obj5_results)
            min5 = np.min(obj5_results)
            max7 = np.max(obj7_results)
            min7 = np.min(obj7_results)

            Model.scaling_factor[Model.objective1] = 1 / (max1 - min1)
            Model.scaling_factor[Model.Z] = 1 / (max3 - min3)
            Model.scaling_factor[Model.gini] = 1 / (max5 - min5)
            Model.scaling_factor[Model.unsatisfied_Z] = 1 / (max7 - min7)

        if l == 0:

            # OBJECTIVE 1 min time
            if counter_scaling != 0:

                Model.obj = Objective(expr=(((Model.objective1 - min1) * Model.scaling_factor[Model.objective1]) +
                                       (-(Model.Z - min3) * 0.001 * Model.scaling_factor[Model.Z]) +
                                       ((Model.unsatisfied_Z - min7) * 0.001 * Model.scaling_factor[Model.unsatisfied_Z]) +
                                       ((Model.gini - min5) * 0.001 * Model.scaling_factor[Model.gini])), sense=1)  # min cost
            else:
                Model.obj = Objective(expr=(Model.objective1 +
                                            (-Model.Z * 0.001) +
                                            Model.unsatisfied_Z * 0.00001 +
                                            (Model.gini * 0.001)),
                                      sense=1)  # min cost

        elif l == 2:

            # OBJECTIVE 3 fairness
            if counter_scaling != 0:
                Model.obj = Objective(expr=(((Model.Z - min3) * Model.scaling_factor[Model.Z]) +
                                       (-(Model.gini - min5) * Model.scaling_factor[Model.gini] * 0.001) +
                                       ((-(Model.objective1 - min1) * Model.scaling_factor[Model.objective1]) * 0.001)+
                                       (-(Model.unsatisfied_Z - min7) * 0.0001 * Model.scaling_factor[Model.unsatisfied_Z])),
                                        sense=-1)  # max fairness
            else:
                Model.obj = Objective(expr=(-Model.objective1 * 0.000001 +
                                            Model.Z +
                                            -Model.unsatisfied_Z * 0.00001 +
                                            (-Model.gini * 0.001)),
                                      sense=-1)  # max fairness

        elif l == 4:

            # OBJECTIVE 4 (gini)
            if counter_scaling != 0:
                Model.obj = Objective(expr=(((Model.gini - min5) * Model.scaling_factor[Model.gini]) +
                                       (-(Model.Z - min3) * Model.scaling_factor[Model.Z]) * 0.001 +
                                       (((Model.objective1 - min1) * Model.scaling_factor[Model.objective1]) * 0.001)+
                                       ((Model.unsatisfied_Z - min7) * 0.0001 * Model.scaling_factor[Model.unsatisfied_Z])),
                                        sense=1)  # min gini
            else:
                Model.obj = Objective(expr=(Model.objective1 * 0.000001 +
                                            (-Model.Z * 0.001) +
                                            Model.unsatisfied_Z * 0.00001 +
                                            (Model.gini)),
                                      sense=1)  # min gini

        elif l == 6:

            # objective 7 min unsatisfied demand
            if counter_scaling != 0:
                Model.obj = Objective(expr=(((Model.gini - min5) * Model.scaling_factor[Model.gini] * 0.001) +
                                        (-(Model.Z - min3) * Model.scaling_factor[Model.Z]) * 0.001 +
                                        (((Model.objective1 - min1) * Model.scaling_factor[Model.objective1]) * 0.001))+
                                        ((Model.unsatisfied_Z - min7) * Model.scaling_factor[Model.unsatisfied_Z]),
                                  sense=1)  # min unsatisfied demand
            else:
                Model.obj = Objective(expr=(Model.objective1 * 0.000001 +
                                            (-Model.Z * 0.001) +
                                            Model.unsatisfied_Z +
                                            (Model.gini * 0.001)),
                                      sense=1)  # min unsatisfied demand

        # CONSTRAINT 0 for maximizing fairness
        alpha = 0.3
        cumsum = 0
        satisfied_cumsum = 0
        part = 0

        for d in nD:
            for k in nK:
                for t in nT:
                    if djkt[t][k][d] > 0:
                        cumsum += djkt[t][k][d]  # cumulative sum
                        satisfied_cumsum += Model.Q[d, k, t]
                        part += ((satisfied_cumsum / cumsum)) * math.exp((-alpha * t))

                        if t == len(nT) - 1:
                            Model.c1.add(Model.Z <= part)
                            cumsum = 0
                            satisfied_cumsum = 0
                            part = 0

        # CONSTRAINT 0* for minimizing unsatisfied demand
        unsatisfied_sum = 0
        demands_t = 0
        cum_unsat_part = 0
        tmp = 0
        counter = 0

        for t in nT:
            for d in nD:
                for k in nK:

                    if djkt[t][k][d] > 0:

                        demands_t += djkt[t][k][d]
                        unsatisfied_sum += Model.H[d, k, t]

                        cum_unsat_part = (unsatisfied_sum / demands_t) * math.exp(alpha)

                        counter += 1
                        if counter == len(nT):
                            tmp += cum_unsat_part

            demands_t = 0
            unsatisfied_sum = 0
            counter = 0

        print(tmp)
        Model.c1.add(Model.unsatisfied_Z >= tmp)

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

        if counter_scaling != 0:
            print(f'\nScaled Objective {l + 1} Solution = ', Model.obj())
            excel_writer(nT, nK, nS, djkt, Model, l)

            print(" ")
            print(f"Solutions Considering Objective {l+1}:")
            print("Scaled Result of objective 1 only: ", (Model.objective1() - min1) * Model.scaling_factor[Model.objective1])
            print("Scaled Result of objective 3 only: ",(Model.Z() - min3) * Model.scaling_factor[Model.Z])
            print("Scaled Result of objective 5 only: ",(Model.gini() - min5) * Model.scaling_factor[Model.gini])
            print("Scaled Result of objective 7 only: ",(Model.unsatisfied_Z() - min7) * Model.scaling_factor[Model.unsatisfied_Z])
            print(" ")
            print(" ************ ")

        else:
            excel_writer(nT, nK, nS, djkt, Model, l)
            print(f'\nUnscaled Objective {l + 1} Solution = ', Model.obj())
            print(" ")
            print(f"Solutions Considering Objective {l+1}:")
            print("Unscaled Result of objective 1 only: ", (Model.objective1()))
            print("Unscaled Result of objective 3 only: ", (Model.Z()))
            print("Unscaled Result of objective 5 only: ", (Model.gini()))
            print("Unscaled Result of objective 7 only: ", (Model.unsatisfied_Z()))
            print(" ")
            print(" ************ ")

            obj1_results.append(Model.objective1())
            obj3_results.append(Model.Z())
            obj5_results.append(Model.gini())
            obj7_results.append(Model.unsatisfied_Z())