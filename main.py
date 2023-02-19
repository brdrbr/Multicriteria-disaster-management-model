from src.dataread import DataReader
from src.model import Problem_Model, model_constraints
from src.scaling import scaling
from pyomo.environ import *
from src.utils import scaled_terminal_writer, unscaled_terminal_writer, logger

# 1. Read the data
data_reader = DataReader()
T, K, N, nS, nD, nN, nT, nK, nE, B, Sikt, djkt, Cijkt, uijt, blocked, bt, aij, \
edge_dict = data_reader.data_read('/Users/yaseminsavas/Multicriteria-disaster-management-model/data/big_data2.xlsx',
                                  mode="Excel")

# Defining problem types and solve the UNSCALED PROBLEM
problems = ["min_cost", "min_unsatisfied_demand"]
min_cost_results, min_unsatisfied_results = [], []

for i in range(0, 2):
    target_problem = problems[i]
    problem = i + 1
    opt = SolverFactory('glpk')

    if target_problem == 'min_cost':
        Target_Model = Problem_Model(nN, nE, nK, nT)
        Target_Model = Target_Model.model_initialization(nT, nK, nE, nD, Cijkt, edge_dict)
        Target_Model = model_constraints(Target_Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt,
                                         alpha=0.3)
        Target_Model.obj = Objective(expr=(Target_Model.obj_mincost +
                                           (Target_Model.obj_unsatisfied * 0.001)),
                                     sense=1)
        Model_solution = opt.solve(Target_Model)

        min_cost_results.append(Target_Model.obj_mincost())
        min_unsatisfied_results.append(Target_Model.obj_unsatisfied())

        unscaled_terminal_writer(Target_Model, problem)

    elif target_problem == 'min_unsatisfied_demand':
        Target_Model = Problem_Model(nN, nE, nK, nT)
        Target_Model = Target_Model.model_initialization(nT, nK, nE, nD, Cijkt, edge_dict)
        Target_Model = model_constraints(Target_Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt,
                                         alpha=0.3)
        Target_Model.obj = Objective(expr=((Target_Model.obj_mincost * 0.000001) +
                                           Target_Model.obj_unsatisfied),
                                     sense=1)
        Model_solution = opt.solve(Target_Model)

        min_cost_results.append(Target_Model.obj_mincost())
        min_unsatisfied_results.append(Target_Model.obj_unsatisfied())

        unscaled_terminal_writer(Target_Model, problem)

    else:
        logger.warning("Provide a valid target objective.")

# 5. Solve the SCALED PROBLEM
min1, min2, scaling_factor_mincost, scaling_factor_unsatisfied = scaling(min_cost_results, min_unsatisfied_results)
for i in range(0, 2):
    target_problem = problems[i]  # INPUT
    problem = i
    opt = SolverFactory('glpk')  # TODO: try cplex and others too for speed.
    if target_problem == 'min_cost':
        Target_Model = Problem_Model(nN, nE, nK, nT)
        Target_Model = Target_Model.model_initialization(nT, nK, nE, nD, Cijkt, edge_dict)
        Target_Model = model_constraints(Target_Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt,
                                         alpha=0.3)

        Target_Model.obj = Objective(expr=(((Target_Model.obj_mincost - min1) * scaling_factor_mincost) +
                                           ((Target_Model.obj_unsatisfied - min2) * 0.001 * scaling_factor_unsatisfied)),
                                     sense=1)  # min cost

        Model_solution = opt.solve(Target_Model)
        scaled_terminal_writer(Target_Model, min1, min2, scaling_factor_mincost,
                               scaling_factor_unsatisfied, nT, nK, nS, djkt, problem)

    elif target_problem == 'min_unsatisfied_demand':
        Target_Model = Problem_Model(nN, nE, nK, nT)
        Target_Model = Target_Model.model_initialization(nT, nK, nE, nD, Cijkt, edge_dict)
        Target_Model = model_constraints(Target_Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt,
                                         alpha=0.3)

        Target_Model.obj = Objective(expr=(((Target_Model.obj_mincost - min1) * 0.001 * scaling_factor_mincost) +
                                           ((Target_Model.obj_unsatisfied - min2) * scaling_factor_unsatisfied)),
                                     sense=1)  # min unsatisfied demand

        Model_solution = opt.solve(Target_Model)
        scaled_terminal_writer(Target_Model, min1, min2, scaling_factor_mincost,
                               scaling_factor_unsatisfied, nT, nK, nS, djkt, problem)

    else:
        logger.warning("Provide a valid target objective.")