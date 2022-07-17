# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 06:08:53 2022

@author: Computer1
"""

import numpy as np


# Updating blocked arc capacities as 0
def update_blocked_capacities(uijt, blocked, nT):

    for t in nT:
        uijt_tmp = [i[1] for i in uijt[0][t]]
        blocked2 = [i[1] for i in blocked[t]]

        uijt_selecting = np.multiply(uijt_tmp, blocked2)

        for i in range(len(np.where(uijt_selecting == 0)[0])):
            change = np.where(uijt_selecting == 0)[0][i]
            uijt[0][t][change][1] = 0

    return uijt