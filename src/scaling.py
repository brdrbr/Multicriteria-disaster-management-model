import numpy as np


def scaling(min_cost_results, min_unsatisfied_results):

    max1 = np.max(min_cost_results)
    min1 = np.min(min_cost_results)
    max2 = np.max(min_unsatisfied_results)
    min2 = np.min(min_unsatisfied_results)

    scaling_factor_mincost = 1 / (max1 - min1)
    scaling_factor_unsatisfied = 1 / (max2 - min2)

    return min1, min2, scaling_factor_mincost, scaling_factor_unsatisfied
