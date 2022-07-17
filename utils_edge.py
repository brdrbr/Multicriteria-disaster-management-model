# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 06:08:53 2022

@author: Computer1
"""

import numpy as np


def update_blocked_capacities(uijt, blocked):
    uijt_tmp = [i[1] for i in uijt[0][0]]
    blocked = [i[1] for i in blocked[0]]

    uijt_selecting = np.multiply(uijt_tmp, blocked)

    for i in range(len(np.where(uijt_selecting == 0)[0])):

        change = np.where(uijt_selecting == 0)[0][i]
        uijt[0][0][change][1] = 0

    return uijt