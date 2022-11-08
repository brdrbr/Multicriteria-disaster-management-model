# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 09:39:45 2022

@author: Computer1"""

import pandas as pd
from pyomo.environ import *

df = pd.read_excel(open('big_data2.xlsx', 'rb'), sheet_name='Data', engine='openpyxl')

T = df.iloc[0, 0]
K = df.iloc[0, 1]
N = df.iloc[0, 2]

nS = RangeSet(1, N)  # supply nodes ( I included transition & demand nodes here but gave them 0 supply )
nD = RangeSet(1, N)  # demand nodes ( I included transition & supply nodes here but gave them 0 demand )
nN = RangeSet(1, N)

edge_dict = {}
for i in range(1,N+1):
    for j in range(1,N+1):
        edge_dict[int(str(i) + str(j))] = [i,j]

nE = list(edge_dict.keys())

B = []
for i in range(1, N*N+1):
    if df.iloc[i,2] == 1:
        B.append(int(str(df.iloc[i,0]) + str(df.iloc[i,1])))


nT = RangeSet(0, T-1)
nK = RangeSet(0, K-1)

Sikt = []
for i in range(T):
    Sikt.append([])
    for j in range(K):
        Sikt[i].append({})
        for k in range(N):
            Sikt[i][j][k+1] = df.iloc[ 1 + N*(k), 3 + j + i*K]

djkt = []
for i in range(T):
    djkt.append([])
    for j in range(K):
        djkt[i].append({})
        for k in range(N):
            djkt[i][j][k+1] = df.iloc[ 1 + N*(k), 3 + T*K + j + i*K]

dummy = []
for i in range(1,N+1):
    for j in range(1,N+1):
        dummy.append(int(str(i) + str(j)))
Cijkt = []
for i in range(T):
    Cijkt.append([])
    for j in range(K):
        Cijkt[i].append([])
        for k in range(N*N):
            Cijkt[i][j].append([])
            Cijkt[i][j][k].append(dummy[k])
            Cijkt[i][j][k].append(df.iloc[ 1 + k, 3 + T*K*2 + j + i*K])
            
uijt = []
for i in range(T):
    uijt.append([])
    for k in range(N*N):
        uijt[i].append([])
        uijt[i][k].append(dummy[k])
        uijt[i][k].append(df.iloc[ 1 + k, 3 + T*K*3 + i])

blocked = []
for i in range(T):
    blocked.append([])
    for k in range(N*N):
        blocked[i].append([])
        blocked[i][k].append(dummy[k])
        blocked[i][k].append(df.iloc[ 1 + k, 3 + T*K*3 + T + i])
        
bt2 = [12, 12]
# Number of resources needed to restore blocked arc (i,j)
bt = []
for i in range(T):
    bt.append(df.iloc[ 1, 3 + T*K*3 + T*2 + i])

aij = {}
for k in range(N*N):
        aij[dummy[k]] = df.iloc[ 1 + k, 3 + T*K*3 + T*3]
