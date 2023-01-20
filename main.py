from src.dataread import DataReader
from src.model import Problem_Model, model_constraints
from src.scaling import scaling
from pyomo.environ import *
from src.utils import scaled_terminal_writer, unscaled_terminal_writer
from time import sleep


# 1. Read the data
data_reader = DataReader()
T, K, N, nS, nD, nN, nT, nK, nE, B, Sikt, djkt, Cijkt, uijt, blocked, bt, aij, edge_dict = data_reader.data_read('/Users/yaseminsavas/Multicriteria-disaster-management-model/data/big_data2.xlsx', mode="Excel")


# Defining problem types and solve the UNSCALED PROBLEM
problems = ["min_cost", "max_fairness", "min_gini", "min_unsatisfied_demand"]
for i in [0, 1, 2]:
    target_problem = problems[i]  # INPUT
    problem = i
    opt = SolverFactory('glpk')
    min_cost_results, max_fairness_results, min_gini_results, min_unsatisfied_results = [], [], [], []

    if target_problem == 'min_cost':
        Target_Model = Problem_Model(nE, nK, nT, nD)
        Target_Model = Target_Model.model_initialization(nT, nK, nE, nD, Cijkt)
        Target_Model = model_constraints(Target_Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt,
                                         alpha=0.3)
        Target_Model.obj = Objective(expr=(Target_Model.obj_mincost + (Target_Model.Z_fairness * 0.001) + (Target_Model.obj_gini * 0.001)
                                           + (Target_Model.Z_unsatisfied * 0.0001)), sense=1)
        Model_solution = opt.solve(Target_Model)
        min_cost_results.append(Target_Model.obj_mincost())
        unscaled_terminal_writer(Target_Model, problem)

    elif target_problem == 'max_fairness':
        Target_Model = Problem_Model(nE, nK, nT, nD)
        Target_Model = Target_Model.model_initialization(nT, nK, nE, nD, Cijkt)
        Target_Model = model_constraints(Target_Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt,
                                         alpha=0.3)
        Target_Model.obj = Objective(expr=((Target_Model.obj_mincost * 0.000001) + Target_Model.Z_fairness + (Target_Model.obj_gini * 0.001)
                                           + (Target_Model.Z_unsatisfied * 0.0001)), sense=-1)
        Model_solution = opt.solve(Target_Model)
        max_fairness_results.append(Target_Model.Z_fairness())
        unscaled_terminal_writer(Target_Model, problem)

    elif target_problem == 'min_gini':
        Target_Model = Problem_Model(nE, nK, nT, nD)
        Target_Model = Target_Model.model_initialization(nT, nK, nE, nD, Cijkt)
        Target_Model = model_constraints(Target_Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt,
                                         alpha=0.3)
        Target_Model.obj = Objective(expr=((Target_Model.obj_mincost * 0.000001) + (Target_Model.Z_fairness * 0.001) + Target_Model.obj_gini
                                           + (Target_Model.Z_unsatisfied * 0.0001)), sense=1)
        Model_solution = opt.solve(Target_Model)
        min_gini_results.append(Target_Model.obj_gini())
        unscaled_terminal_writer(Target_Model, problem)

    elif target_problem == 'min_unsatisfied_demand':
        Target_Model = Problem_Model(nE, nK, nT, nD)
        Target_Model = Target_Model.model_initialization(nT, nK, nE, nD, Cijkt)
        Target_Model = model_constraints(Target_Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt,
                                         alpha=0.3)
        Target_Model.obj = Objective(expr=((Target_Model.obj_mincost * 0.000001) + (Target_Model.Z_fairness * 0.001) +
                                           (Target_Model.obj_gini * 0.001) + Target_Model.Z_unsatisfied), sense=1)
        Model_solution = opt.solve(Target_Model)
        min_unsatisfied_results.append(Target_Model.Z_unsatisfied())
        unscaled_terminal_writer(Target_Model, problem)

    else:
        print("Provide a valid target objective.")

"""sleep(5)
# 5. Solve the SCALED PROBLEM
for i in [0, 2, 3]:
    target_problem = problems[i]  # INPUT
    problem = i
    opt = SolverFactory('glpk')
    min1, min2, min3, min4 = 0, 0, 0, 0
    if target_problem == 'min_cost':
        Target_Model = Problem_Model(nE, nK, nT, nD)
        Target_Model = Target_Model.model_initialization(nT, nK, nE, Cijkt)
        Target_Model = model_constraints(Target_Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt,
                                         alpha=0.3)
        Target_Model, min1, min2, min3, min4 = scaling(Target_Model, min_cost_results, max_fairness_results, min_gini_results, min_unsatisfied_results, problem)
        Model_solution = opt.solve(Target_Model)
        scaled_terminal_writer(Target_Model, min1, min2, min3, min4, nT, nK, nS, djkt, problem)

    elif target_problem == 'max_fairness':
        Target_Model = Problem_Model(nE, nK, nT, nD)
        Target_Model = Target_Model.model_initialization(nT, nK, nE, Cijkt)
        Target_Model = model_constraints(Target_Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt,
                                         alpha=0.3)
        Target_Model, min1, min2, min3, min4 = scaling(Target_Model, min_cost_results, max_fairness_results, min_gini_results, min_unsatisfied_results, problem)
        Model_solution = opt.solve(Target_Model)
        scaled_terminal_writer(Target_Model, min1, min2, min3, min4, nT, nK, nS, djkt, problem)

    elif target_problem == 'min_gini':
        Target_Model = Problem_Model(nE, nK, nT, nD)
        Target_Model = Target_Model.model_initialization(nT, nK, nE, Cijkt)
        Target_Model = model_constraints(Target_Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt,
                                         alpha=0.3)
        Target_Model, min1, min2, min3, min4 = scaling(Target_Model, min_cost_results, max_fairness_results, min_gini_results, min_unsatisfied_results, problem)
        Model_solution = opt.solve(Target_Model)
        scaled_terminal_writer(Target_Model, min1, min2, min3, min4, nT, nK, nS, djkt, problem)

    elif target_problem == 'min_unsatisfied_demand':
        Target_Model = Problem_Model(nE, nK, nT, nD)
        Target_Model = Target_Model.model_initialization(nT, nK, nE, Cijkt)
        Target_Model = model_constraints(Target_Model, nD, nT, nK, nN, Sikt, djkt, nS, uijt, edge_dict, aij, bt,
                                         alpha=0.3)
        Target_Model, min1, min2, min3, min4 = scaling(Target_Model, min_cost_results, max_fairness_results, min_gini_results, min_unsatisfied_results, problem)
        Model_solution = opt.solve(Target_Model)
        scaled_terminal_writer(Target_Model, min1, min2, min3, min4, nT, nK, nS, djkt, problem)

    else:
        print("Provide a valid target objective.")"""