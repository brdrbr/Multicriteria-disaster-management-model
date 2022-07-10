from pyomo.environ import *
from utils_node import *


# Supply nodes for commodity k
Ik = [[1, 2]]

# Demand nodes for commodity k
Jk = [[3, 4]]

# Transition Nodes for commodity k
Tk = [[5, 6]]

nS = RangeSet(1, 6)  # supply nodes ( I included transition & demand nodes here but gave them 0 supply )
nD = RangeSet(1, 6)  # demand nodes ( I included transition & supply nodes here but gave them 0 demand )
nT = RangeSet(5, 6)  # transition nodes

# Set of blocked roads
# (source, destination)
B = [[1, 4],
     [2, 3]]

# Time periods - only 1 for simplicity
t = [0]

# Commodities - only 1 for simplicity
K = [1]

# Newly arrived supply of commodity k at supply node i in period t example units: 5 = 500 litres of water
# (supply node, supply amount) - will be extended for all commodities and all time periods
Sikt = [[{1: 8, 2: 15, 3: 0, 4: 0, 5: 0, 6: 0}]]

# Newly arising demand of commodity k at node j in period t - will be extended for all commodities and all time periods
# (demand node, demand amount)
djkt = [[{1: 0, 2: 0, 3: 15, 4: 8, 5: 0, 6: 0}]]

# (origin, destination, cost of travel time) - will be extended for all commodities and all time periods
Cijkt = [[[[1, 1, 0], [1, 2, 10], [1, 3, 8], [1, 4, 2], [1, 5, 2], [1, 6, 2],
           [2, 1, 1], [2, 2, 0], [2, 3, 3], [2, 4, 9], [2, 5, 2], [2, 6, 2],
           [3, 1, 1], [3, 2, 2], [3, 3, 0], [3, 4, 3], [3, 5, 2], [3, 6, 2],
           [4, 1, 3], [4, 2, 1], [4, 3, 1], [4, 4, 0], [4, 5, 2], [4, 6, 2],
           [5, 1, 3], [5, 2, 3], [5, 3, 1], [5, 4, 1], [5, 5, 0], [5, 6, 2],
           [6, 1, 3], [6, 2, 1], [6, 3, 1], [6, 4, 2], [6, 5, 2], [6, 6, 0]]]]
# Unit travel time on arc [i,j] for commodity k in period t

# Capacity of arc [i,j] in period t [zero, if arc [i,j] is blocked at time t] - will be extended for all commodities and all time periods
uijt = [[[[1, 1, 0], [1, 2, 5], [1, 3, 10], [1, 4, 4], [1, 5, 10], [1, 6, 4],
          [2, 1, 5], [2, 2, 0], [2, 3, 1], [2, 4, 20], [2, 5, 10], [2, 6, 4],
          [3, 1, 3], [3, 2, 6], [3, 3, 0], [3, 4, 10], [3, 5, 10], [3, 6, 4],
          [4, 1, 10], [4, 2, 5], [4, 3, 8], [4, 4, 0], [4, 5, 10], [4, 6, 4],
          [5, 1, 10], [5, 2, 5], [5, 3, 8], [5, 4, 2], [5, 5, 0], [5, 6, 4],
          [6, 1, 10], [6, 2, 5], [6, 3, 8], [6, 4, 2], [6, 5, 10], [6, 6, 0]]]]

# Blocked arc or not
# [from, to, blocked/not blocked] Blocked = 0 for a time period t
blocked = [[[1, 1, 1], [1, 2, 1], [1, 3, 1], [1, 4, 0], [1, 5, 1], [1, 6, 1],
            [2, 1, 1], [2, 2, 1], [2, 3, 0], [2, 4, 1], [2, 5, 1], [2, 6, 1],
            [3, 1, 1], [3, 2, 1], [3, 3, 1], [3, 4, 1], [3, 5, 1], [3, 6, 1],
            [4, 1, 1], [4, 2, 1], [4, 3, 1], [4, 4, 1], [4, 5, 1], [4, 6, 1],
            [5, 1, 1], [5, 2, 1], [5, 3, 1], [5, 4, 1], [5, 5, 1], [5, 6, 1],
            [6, 1, 1], [6, 2, 1], [6, 3, 1], [6, 4, 1], [6, 5, 1], [6, 6, 1]]]

uijt = update_blocked_capacities(uijt, blocked)

# [blocked road origin, blocked road destination, units of road restoration resources in period t]
bt = [[[1, 1, 0], [1, 2, 0], [1, 3, 0], [1, 4, 12], [1, 5, 1], [1, 6, 2],
       [2, 1, 0], [2, 2, 0], [2, 3, 12], [2, 4, 0], [2, 5, 1], [2, 6, 2],
       [3, 1, 0], [3, 2, 0], [3, 3, 0], [3, 4, 0], [3, 5, 1], [3, 6, 2],
       [4, 1, 0], [4, 2, 0], [4, 3, 0], [4, 4, 0], [4, 5, 1], [4, 6, 2],
       [5, 1, 0], [5, 2, 0], [5, 3, 0], [5, 4, 0], [5, 5, 0], [5, 6, 2],
       [6, 1, 0], [6, 2, 0], [6, 3, 0], [6, 4, 0], [6, 5, 1], [6, 6, 0]]]

# Number of resources needed to restore blocked arc (i,j)
aij = [[[[1, 1, 8], [1, 2, 8], [1, 3, 8], [1, 4, 8], [1, 5, 8], [1, 6, 8],
        [2, 1, 8], [2, 2, 8], [2, 3, 8], [2, 4, 8], [2, 5, 8], [2, 6, 8],
        [3, 1, 8], [3, 2, 8], [3, 3, 8], [3, 4, 8], [3, 5, 8], [3, 6, 8],
        [4, 1, 8], [4, 2, 8], [4, 3, 8], [4, 4, 8], [4, 5, 8], [4, 6, 8],
        [5, 1, 8], [5, 2, 8], [5, 3, 8], [5, 4, 8], [5, 5, 8], [5, 6, 8],
        [6, 1, 8], [6, 2, 8], [6, 3, 8], [6, 4, 8], [6, 5, 8], [6, 6, 8]]]]