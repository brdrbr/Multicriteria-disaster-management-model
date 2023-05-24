from src.dataread import DataReader
from src.model import ProblemModel, model_constraints
from src.scaling import scaling
from pyomo.environ import *
from src.utils import scaled_terminal_writer, unscaled_terminal_writer


# 1. Read the data
data_reader = DataReader()
T, K, N, nS, nD, nN, nT, nK, nE, B, Sikt, djkt, Cijkt, uijt, blocked, bt, aij, edge_dict, k1_nodes, k2_nodes = data_reader.data_read('/Users/yaseminsavas/Multicriteria-disaster-management-model/data/disaster_data_avcilar.xlsx', mode="Excel")


# Defining problem types and solve the UNSCALED PROBLEM
problems = ["min_cost", "min_unsatisfied_demand"]
min_cost_results, max_fairness_results, min_gini_results, min_unsatisfied_results = [], [], [], []
for i in range(0, 2):
    target_problem = problems[i]
    problem = i + 1
    opt = SolverFactory('glpk')

    if target_problem == 'min_cost':
        Target_Model = ProblemModel(nN, nE, nK, nT, nD)
        Target_Model = Target_Model.model_initialization(nN, nT, nK, nE, nD, Cijkt, edge_dict)
        Target_Model = model_constraints(Target_Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt, k1_nodes, k2_nodes,
                                         alpha=0.3)
        Target_Model.obj = Objective(expr=(Target_Model.obj_mincost + (Target_Model.obj_unsatisfied * 0.001)), sense=1)
        Model_solution = opt.solve(Target_Model)
        min_cost_results.append(Target_Model.obj_mincost())
        min_unsatisfied_results.append(Target_Model.obj_unsatisfied())
        unscaled_terminal_writer(Target_Model, problem)

    elif target_problem == 'min_unsatisfied_demand':
        Target_Model = ProblemModel(nN, nE, nK, nT, nD)
        Target_Model = Target_Model.model_initialization(nN, nT, nK, nE, nD, Cijkt, edge_dict)
        Target_Model = model_constraints(Target_Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt, k1_nodes, k2_nodes,
                                         alpha=0.3)
        Target_Model.obj = Objective(expr=((Target_Model.obj_mincost * 0.000001) + Target_Model.obj_unsatisfied), sense=1)
        Model_solution = opt.solve(Target_Model)
        min_cost_results.append(Target_Model.obj_mincost())
        min_unsatisfied_results.append(Target_Model.obj_unsatisfied())
        unscaled_terminal_writer(Target_Model, problem)

    else:
        print("Provide a valid target objective.")

# 5. Solve the SCALED PROBLEM
min1, min4, scaling_factor_mincost, scaling_factor_unsatisfied = scaling(min_cost_results, min_unsatisfied_results)
for i in range(0, 2):
    target_problem = problems[i]  # INPUT
    problem = i
    opt = SolverFactory('glpk')
    if target_problem == 'min_cost':
        Target_Model = ProblemModel(nN, nE, nK, nT, nD)
        Target_Model = Target_Model.model_initialization(nN, nT, nK, nE, nD, Cijkt, edge_dict)
        Target_Model = model_constraints(Target_Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt, k1_nodes, k2_nodes,
                                         alpha=0.3)

        Target_Model.obj = Objective(expr=(((Target_Model.obj_mincost - min1) * scaling_factor_mincost) +
                                    ((Target_Model.obj_unsatisfied - min4) * 0.001 * scaling_factor_unsatisfied)),
                              sense=1)  # min cost

        Model_solution = opt.solve(Target_Model)
        scaled_terminal_writer(Target_Model, min1,  min4, scaling_factor_mincost, scaling_factor_unsatisfied, nT, nK, nS, djkt, problem)

    elif target_problem == 'min_unsatisfied_demand':
        Target_Model = ProblemModel(nN, nE, nK, nT, nD)
        Target_Model = Target_Model.model_initialization(nN, nT, nK, nE, nD, Cijkt, edge_dict)
        Target_Model = model_constraints(Target_Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt, k1_nodes, k2_nodes,
                                         alpha=0.3)

        Target_Model.obj = Objective(expr=(((Target_Model.obj_mincost - min1) * 0.001 * scaling_factor_mincost) +
                                    ((Target_Model.obj_unsatisfied - min4) * scaling_factor_unsatisfied)),
                              sense=1)  # min unsatisfied demand

        Model_solution = opt.solve(Target_Model)
        scaled_terminal_writer(Target_Model, min1, min4, scaling_factor_mincost, scaling_factor_unsatisfied, nT, nK, nS, djkt, problem)

    else:
        print("Provide a valid target objective.")