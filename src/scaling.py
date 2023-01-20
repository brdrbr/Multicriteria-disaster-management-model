import numpy as np
from pyomo.environ import *


def scaling(Model, min_cost_results, max_fairness_results, min_gini_results, min_unsatisfied_results, problem=None):

    max1 = np.max(min_cost_results)
    min1 = np.min(min_cost_results)
    max2 = np.max(max_fairness_results)
    min2 = np.min(max_fairness_results)
    max3 = np.max(min_gini_results)
    min3 = np.min(min_gini_results)
    max4 = np.max(min_unsatisfied_results)
    min4 = np.min(min_unsatisfied_results)

    Model.scaling_factor[Model.obj_mincost] = 1 / (max1 - min1)
    Model.scaling_factor[Model.Z_fairness] = 1 / (max2 - min2)
    Model.scaling_factor[Model.obj_gini] = 1 / (max3 - min3)
    Model.scaling_factor[Model.Z_unsatisfied] = 1 / (max4 - min4)

    if problem == 1:
        Model.obj = Objective(expr=(((Model.obj_mincost - min1) * Model.scaling_factor[Model.obj_mincost]) +
                                    ((Model.Z_fairness - min2) * 0.001 * Model.scaling_factor[Model.Z_fairness]) +
                                    ((Model.obj_gini - min3) * 0.001 * Model.scaling_factor[Model.obj_gini]) +
                                    ((Model.Z_unsatisfied - min4) * 0.001 * Model.scaling_factor[Model.Z_unsatisfied])),
                              sense=1)  # min cost
    elif problem == 2:
        Model.obj = Objective(expr=(((Model.obj_mincost - min1) * 0.001 * Model.scaling_factor[Model.obj_mincost]) +
                                    ((Model.Z_fairness - min2) * Model.scaling_factor[Model.Z_fairness]) +
                                    ((Model.obj_gini - min3) * 0.001 * Model.scaling_factor[Model.obj_gini]) +
                                    ((Model.Z_unsatisfied - min4) * 0.001 * Model.scaling_factor[Model.Z_unsatisfied])),
                              sense=1)  # min cost
    elif problem == 3:
        Model.obj = Objective(expr=(((Model.obj_mincost - min1) * 0.001 * Model.scaling_factor[Model.obj_mincost]) +
                                    ((Model.Z_fairness - min2) * 0.001 * Model.scaling_factor[Model.Z_fairness]) +
                                    ((Model.obj_gini - min3) * Model.scaling_factor[Model.obj_gini]) +
                                    ((Model.Z_unsatisfied - min4) * 0.001 * Model.scaling_factor[Model.Z_unsatisfied])),
                              sense=1)  # min cost
    elif problem == 4:
        Model.obj = Objective(expr=(((Model.obj_mincost - min1) * 0.001 * Model.scaling_factor[Model.obj_mincost]) +
                                    ((Model.Z_fairness - min2) * 0.001 * Model.scaling_factor[Model.Z_fairness]) +
                                    ((Model.obj_gini - min3) * 0.001 * Model.scaling_factor[Model.obj_gini]) +
                                    ((Model.Z_unsatisfied - min4) * Model.scaling_factor[Model.Z_unsatisfied])),
                              sense=1)  # min cost

    return Model, min1, min2, min3, min4
