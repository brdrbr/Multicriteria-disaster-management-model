from pyomo.environ import *
import numpy as np


#OLD VERSION

nS = RangeSet(1, 6)  # supply nodes ( I included transition & demand nodes here but gave them 0 supply )
nD = RangeSet(1, 6)  # demand nodes ( I included transition & supply nodes here but gave them 0 demand )
nN = RangeSet(1, 6)  # all nodes
# Mapping edges with their origin-destination node pairs
# keys represent edge number e, values represent the [origin,destination] routes.
edge_dict = {11: [1, 1], 12: [1, 2],
             13: [1, 3], 14: [1, 4],
             15: [1, 5], 16: [1, 6],
             21: [2, 1], 22: [2, 2],
             23: [2, 3], 24: [2, 4],
             25: [2, 5], 26: [2, 6],
             31: [3, 1], 32: [3, 2],
             33: [3, 3], 34: [3, 4],
             35: [3, 5], 36: [3, 6],
             41: [4, 1], 42: [4, 2],
             43: [4, 3], 44: [4, 4],
             45: [4, 5], 46: [4, 6],
             51: [5, 1], 52: [5, 2],
             53: [5, 3], 54: [5, 4],
             55: [5, 5], 56: [5, 6],
             61: [6, 1], 62: [6, 2],
             63: [6, 3], 64: [6, 4],
             65: [6, 5], 66: [6, 6]}
nE = list(edge_dict.keys())  # list of edges
# Set of blocked roads
# arc a
B = [14, 23]
# Time periods - only 2
nT = RangeSet(0, 1)
# Commodities - only 2
nK = RangeSet(0, 1)
# Newly arrived supply of commodity k at supply node i in period t example units: 5 = 500 litres of water
# (supply node, supply amount) - will be extended for all commodities and all time periods
Sikt = [[{1: 8, 2: 15, 3: 0, 4: 0, 5: 0, 6: 0}, #comm 1 tp 1
        {1: 8, 2: 15, 3: 0, 4: 0, 5: 0, 6: 0}], #comm 2 tp 1
        [{1: 8, 2: 15, 3: 0, 4: 0, 5: 0, 6: 0}, #comm 1 tp 2
        {1: 8, 2: 15, 3: 0, 4: 0, 5: 0, 6: 0}]] #comm 2 tp 2
# Newly arising demand of commodity k at node j in period t - will be extended for all commodities and all time periods
# (demand node, demand amount)
djkt = [[{1: 0, 2: 0, 3: 15, 4: 8, 5: 0, 6: 0}, #comm 1 tp 1
         {1: 0, 2: 0, 3: 15, 4: 8, 5: 0, 6: 0}],#comm 2 tp 1
        [{1: 0, 2: 0, 3: 15, 4: 8, 5: 0, 6: 0}, #comm 1 tp 2
        {1: 0, 2: 0, 3: 15, 4: 8, 5: 0, 6: 0}]] #comm 2 tp 2
# (origin, destination, cost of travel time) - will be extended for all commodities and all time periods
Cijkt = [[[[11, 0], [12, 10], [13, 8], [14, 2], [15, 2], [16, 2],
           [21, 1], [22, 0], [23, 3], [24, 9], [25, 2], [26, 2],
           [31, 1], [32, 2], [33, 0], [34, 3], [35, 2], [36, 2],
           [41, 3], [42, 1], [43, 1], [44, 0], [45, 2], [46, 2],
           [51, 3], [52, 3], [53, 1], [54, 1], [55, 0], [56, 2],
           [61, 3], [62, 1], [63, 1], [64, 2], [65, 2], [66, 0]],

           [[11, 0], [12, 10], [13, 8], [14, 2], [15, 2], [16, 2],
           [21, 1], [22, 0], [23, 3], [24, 9], [25, 2], [26, 2],
           [31, 1], [32, 2], [33, 0], [34, 3], [35, 2], [36, 2],
           [41, 3], [42, 1], [43, 1], [44, 0], [45, 2], [46, 2],
           [51, 3], [52, 3], [53, 1], [54, 1], [55, 0], [56, 2],
           [61, 3], [62, 1], [63, 1], [64, 2], [65, 2], [66, 0]
          ]],  # comm1 tp 1 & comm2 tp 1
         [[[11, 0], [12, 10], [13, 8], [14, 2], [15, 2], [16, 2],
           [21, 1], [22, 0], [23, 3], [24, 9], [25, 2], [26, 2],
           [31, 1], [32, 2], [33, 0], [34, 3], [35, 2], [36, 2],
           [41, 3], [42, 1], [43, 1], [44, 0], [45, 2], [46, 2],
           [51, 3], [52, 3], [53, 1], [54, 1], [55, 0], [56, 2],
           [61, 3], [62, 1], [63, 1], [64, 2], [65, 2], [66, 0]],

          [[11, 0], [12, 10], [13, 8], [14, 2], [15, 2], [16, 2],
           [21, 1], [22, 0], [23, 3], [24, 9], [25, 2], [26, 2],
           [31, 1], [32, 2], [33, 0], [34, 3], [35, 2], [36, 2],
           [41, 3], [42, 1], [43, 1], [44, 0], [45, 2], [46, 2],
           [51, 3], [52, 3], [53, 1], [54, 1], [55, 0], [56, 2],
           [61, 3], [62, 1], [63, 1], [64, 2], [65, 2], [66, 0]
           ]]]  # comm2 tp 1 & comm2 tp 2
# Unit travel time on arc [i,j] for commodity k in period t
# Capacity of arc [i,j] in period t [zero, if arc [i,j] is blocked at time t]
# no need to extend this for the commodities right???
uijt = [
           [
               [11, 0], [12, 5], [13, 10], [14, 0], [15, 10], [16, 4],
          [21, 5], [22, 0], [23, 0], [24, 20], [25, 10], [26, 4],
          [31, 3], [32, 6], [33, 0], [34, 10], [35, 10], [36, 4],
          [41, 10], [42, 5], [43, 8], [44, 0], [45, 10], [46, 4],
          [51, 10], [52, 5], [53, 8], [54, 2], [55, 0], [56, 4],
          [61, 10], [62, 5], [63, 8], [64, 2], [65, 10], [66, 0]
           ],
           # comm1 tp1 & comm2 tp 1

         [
             [11, 0], [12, 5], [13, 10], [14, 0], [15, 10], [16, 4],
          [21, 5], [22, 0], [23, 0], [24, 20], [25, 10], [26, 4],
          [31, 3], [32, 6], [33, 0], [34, 10], [35, 10], [36, 4],
          [41, 10], [42, 5], [43, 8], [44, 0], [45, 10], [46, 4],
          [51, 10], [52, 5], [53, 8], [54, 2], [55, 0], [56, 4],
          [61, 10], [62, 5], [63, 8], [64, 2], [65, 10], [66, 0]
         ]
       ]  # comm2 tp 1 & comm2 tp 2
# Blocked arc or not
# [from, to, blocked/not blocked] Blocked = 0 for a time period t
blocked = [[[11, 1], [12, 1], [13, 1], [14, 0], [15, 1], [16, 1],
            [21, 1], [22, 1], [23, 0], [24, 1], [25, 1], [26, 1],
            [31, 1], [32, 1], [33, 1], [34, 1], [35, 1], [36, 1],
            [41, 1], [42, 1], [43, 1], [44, 1], [45, 1], [46, 1],
            [51, 1], [52, 1], [53, 1], [54, 1], [55, 1], [56, 1],
            [61, 1], [62, 1], [63, 1], [64, 1], [65, 1], [66, 1]],  # comm1 tp 1 & comm2 tp 2

           [[11, 1], [12, 1], [13, 1], [14, 0], [15, 1], [16, 1],
            [21, 1], [22, 1], [23, 0], [24, 1], [25, 1], [26, 1],
            [31, 1], [32, 1], [33, 1], [34, 1], [35, 1], [36, 1],
            [41, 1], [42, 1], [43, 1], [44, 1], [45, 1], [46, 1],
            [51, 1], [52, 1], [53, 1], [54, 1], [55, 1], [56, 1],
            [61, 1], [62, 1], [63, 1], [64, 1], [65, 1], [66, 1]]]  # comm2 tp 1 & comm2 tp 2
#uijt = update_blocked_capacities(uijt, blocked, nT)
# [blocked road origin, blocked road destination, units of road restoration resources in period t]
bt = [12, 12]
# Number of resources needed to restore blocked arc (i,j)
aij = {11: 8, 12: 8, 13: 8, 14: 8, 15: 8, 16: 8,
        21: 8, 22: 8, 23: 8, 24: 8, 25: 8, 26: 8,
        31: 8, 32: 8, 33: 8, 34: 8, 35: 8, 36: 8,
        41: 8, 42: 8, 43: 8, 44: 8, 45: 8, 46: 8,
        51: 8, 52: 8, 53: 8, 54: 8, 55: 8, 56: 8,
        61: 8, 62: 8, 63: 8, 64: 8, 65: 8, 66: 8}  #I deleted the extra brackets here since in the model this does not
#depend on time or commodity right ???
#Yes, it is ok. I think it is not time-dependent. If it is, we can add brackets like the previous ones.


#NEW VERSION
"""
from pyomo.environ import *
from utils_edge import *
nS = RangeSet(1, 6)  # supply nodes ( I included transition & demand nodes here but gave them 0 supply )
nD = RangeSet(1, 6)  # demand nodes ( I included transition & supply nodes here but gave them 0 demand )
nN = RangeSet(1, 6)  # all nodes
# Mapping edges with their origin-destination node pairs
# keys represent edge number e, values represent the [origin,destination] routes.
edge_dict = {11: [1, 1], 12: [1, 2],
             13: [1, 3], 14: [1, 4],
             15: [1, 5], 16: [1, 6],
             21: [2, 1], 22: [2, 2],
             23: [2, 3], 24: [2, 4],
             25: [2, 5], 26: [2, 6],
             31: [3, 1], 32: [3, 2],
             33: [3, 3], 34: [3, 4],
             35: [3, 5], 36: [3, 6],
             41: [4, 1], 42: [4, 2],
             43: [4, 3], 44: [4, 4],
             45: [4, 5], 46: [4, 6],
             51: [5, 1], 52: [5, 2],
             53: [5, 3], 54: [5, 4],
             55: [5, 5], 56: [5, 6],
             61: [6, 1], 62: [6, 2],
             63: [6, 3], 64: [6, 4],
             65: [6, 5], 66: [6, 6]}
nE = list(edge_dict.keys())  # list of edges
# Set of blocked roads
# arc a
B = [14, 23]
# Time periods - only 2
nT = [0]
# Commodities - only 2
nK = [0]
# Newly arrived supply of commodity k at supply node i in period t example units: 5 = 500 litres of water
# (supply node, supply amount) - will be extended for all commodities and all time periods
Sikt = [[{1: 8, 2: 15, 3: 0, 4: 0, 5: 0, 6: 0}]] #comm 2 tp 2
# Newly arising demand of commodity k at node j in period t - will be extended for all commodities and all time periods
# (demand node, demand amount)
djkt = [[{1: 0, 2: 0, 3: 15, 4: 8, 5: 0, 6: 0}]] #comm 2 tp 2
# (origin, destination, cost of travel time) - will be extended for all commodities and all time periods
Cijkt = [[[[11, 0], [12, 10], [13, 8], [14, 2], [15, 2], [16, 2],
           [21, 1], [22, 0], [23, 3], [24, 9], [25, 2], [26, 2],
           [31, 1], [32, 2], [33, 0], [34, 3], [35, 2], [36, 2],
           [41, 3], [42, 1], [43, 1], [44, 0], [45, 2], [46, 2],
           [51, 3], [52, 3], [53, 1], [54, 1], [55, 0], [56, 2],
           [61, 3], [62, 1], [63, 1], [64, 2], [65, 2], [66, 0]]]]
# Unit travel time on arc [i,j] for commodity k in period t
# Capacity of arc [i,j] in period t [zero, if arc [i,j] is blocked at time t]
# no need to extend this for the commodities right???
uijt = [[[11, 0], [12, 5], [13, 10], [14, 4], [15, 10], [16, 4],
          [21, 5], [22, 0], [23, 1], [24, 20], [25, 10], [26, 4],
          [31, 3], [32, 6], [33, 0], [34, 10], [35, 10], [36, 4],
          [41, 10], [42, 5], [43, 8], [44, 0], [45, 10], [46, 4],
          [51, 10], [52, 5], [53, 8], [54, 2], [55, 0], [56, 4],
          [61, 10], [62, 5], [63, 8], [64, 2], [65, 10], [66, 0]]]
# Blocked arc or not
# [from, to, blocked/not blocked] Blocked = 0 for a time period t
blocked = [[[11, 1], [12, 1], [13, 1], [14, 0], [15, 1], [16, 1],
            [21, 1], [22, 1], [23, 0], [24, 1], [25, 1], [26, 1],
            [31, 1], [32, 1], [33, 1], [34, 1], [35, 1], [36, 1],
            [41, 1], [42, 1], [43, 1], [44, 1], [45, 1], [46, 1],
            [51, 1], [52, 1], [53, 1], [54, 1], [55, 1], [56, 1],
            [61, 1], [62, 1], [63, 1], [64, 1], [65, 1], [66, 1]]]
#uijt = update_blocked_capacities(uijt, blocked, nT)  #how to change this based on time ??? we need to insert the right uijt[][]
#changed this as well
# [blocked road origin, blocked road destination, units of road restoration resources in period t]
bt = [12]
#uijt = update_blocked_capacities(uijt, blocked, nT)  #how to change this based on time ??? we need to insert the right uijt[][]
# Number of resources needed to restore blocked arc (i,j)
aij = {11: 8, 12: 8, 13: 8, 14: 8, 15: 8, 16: 8,
        21: 8, 22: 8, 23: 8, 24: 8, 25: 8, 26: 8,
        31: 8, 32: 8, 33: 8, 34: 8, 35: 8, 36: 8,
        41: 8, 42: 8, 43: 8, 44: 8, 45: 8, 46: 8,
        51: 8, 52: 8, 53: 8, 54: 8, 55: 8, 56: 8,
        61: 8, 62: 8, 63: 8, 64: 8, 65: 8, 66: 8}  #I deleted the extra brackets here since in the model this does not
#depend on time or commodity right ???"""
