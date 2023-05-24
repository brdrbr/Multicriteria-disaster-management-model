import numpy as np
from pyomo.environ import *


def scaling(min_cost_results,  min_unsatisfied_results):

    max1 = np.max(min_cost_results)
    min1 = np.min(min_cost_results)
    max4 = np.max(min_unsatisfied_results)
    min4 = np.min(min_unsatisfied_results)

    scaling_factor_mincost = 1 / (max1 - min1)
    scaling_factor_unsatisfied = 1 / (max4 - min4)

    return min1, min4, scaling_factor_mincost, scaling_factor_unsatisfied