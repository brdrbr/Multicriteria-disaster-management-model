import numpy as np
from pyomo.environ import *


def scaling(min_cost_results, max_fairness_results, min_gini_results, min_unsatisfied_results):

    max1 = np.max(min_cost_results)
    min1 = np.min(min_cost_results)
    max2 = np.max(max_fairness_results)
    min2 = np.min(max_fairness_results)
    max3 = np.max(min_gini_results)
    min3 = np.min(min_gini_results)
    max4 = np.max(min_unsatisfied_results)
    min4 = np.min(min_unsatisfied_results)

    scaling_factor_mincost = 1 / (max1 - min1)
    scaling_factor_fairness = 1 / (max2 - min2)
    scaling_factor_mingini = 1 / (max3 - min3)
    scaling_factor_unsatisfied = 1 / (max4 - min4)

    return min1, min2, min3, min4, scaling_factor_mincost, scaling_factor_fairness, scaling_factor_mingini, scaling_factor_unsatisfied
