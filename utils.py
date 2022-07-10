import numpy as np


def update_blocked_capacities(uijt, blocked):
    uijt_tmp = [i[2] for i in uijt[0][0]]
    blocked = [i[2] for i in blocked[0]]

    uijt_selecting = np.multiply(uijt_tmp, blocked)

    for i in range(len(np.where(uijt_selecting == 0)[0])):

        change = np.where(uijt_selecting == 0)[0][i]
        uijt[0][0][change][2] = 0

    return uijt
