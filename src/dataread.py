import pandas as pd
import numpy as np


class DataReader:

    def data_read(self, directory, mode="Excel"):

        if mode == 'Excel':

            df = pd.read_excel(open(directory, 'rb'), sheet_name='Sheet1', engine='openpyxl')

            T = 1
            K = 2
            N = len(np.unique(list(df.inside)))

            nS = np.unique(list(df[(df.health_supply > 0) | (df.shelter_supply > 0)].inside))
            nD = np.unique(list(df[(df.health_need > 0) | (df.shelter_need > 0)].inside))
            nN = np.unique(list(df.inside))

            nT = [0]
            nK = [0, 1]

            edge_dict = {}
            for row in df.iterrows():
                edge_dict[int(float(str(int(float(str(row[1].inside)))) + str(int(float(str(row[1].out))))))] = [int(float(row[1].inside)), int(float(row[1].out))]

            nE = list(edge_dict.keys())
            B = list(df.B)

            Sikt = []
            for i in range(T):
                Sikt.append([])
                for j in range(K):
                    Sikt[i].append({})

            for t in range(T):
                for k in range(K):
                    if k == 0:
                        supply = "health_supply"
                    if k == 1:
                        supply = "shelter_supply"
                    for n in nN:
                        Sikt[t][k][n] = int(np.unique(df.loc[df.inside == n, supply]))

            djkt = []
            for i in range(T):
                djkt.append([])
                for j in range(K):
                    djkt[i].append({})

            for t in range(T):
                for k in range(K):
                    if k == 0:
                        need = "health_need"
                    if k == 1:
                        need = "shelter_need"
                    for n in nN:
                        djkt[t][k][n] = int(np.unique(df.loc[df.inside == n, need]))

            Cijkt = []
            for i in range(T):
                Cijkt.append([])
                for j in range(K):
                    Cijkt[i].append({})

            for t in range(T):
                for k in range(K):
                    if k == 0:
                        cost = "cost_health"
                    if k == 1:
                        cost = "cost_shelter"
                    for n in nN:
                        Cijkt[t][k][n] = int(np.unique(df.loc[df.inside == n, cost]))

            uijt = []
            for t in range(T):
                uijt.append({})

            df.capacity.fillna(0, inplace=True)
            for t in range(T):
                for n in nD:
                    n_cap = int(np.sum(list(df.loc[df.inside == n, "capacity"])))
                    for edge in list(edge_dict.keys()):
                        if str(edge).find(str(n)) == 0:
                            uijt[t][edge] = n_cap

            blocked = []
            for i in range(T):
                blocked.append({})

            for t in range(T):
                for n in nD:
                    blocked[t][n] = int(np.unique(df.loc[df.inside == n, "blocked"]))

            # Number of resources needed to restore blocked arc (i,j)
            bt = []
            for t in range(T):
                bt.append([])

            for t in range(T):
                bt[t] = int(np.unique(list(df["road_restoration_supply"])))

            aij = []
            for i in range(T):
                aij.append([])
                for j in range(K):
                    aij[i].append({})

            for t in range(T):
                for k in range(K):
                    for n in nN:
                        aij[t][k][n] = int(np.unique(list(df["road_restoration_demand"])))

            k1_nodes = np.unique(list(df[(df.health_need > 0)].inside))
            k2_nodes = np.unique(list(df[(df.shelter_need > 0)].inside))

            print("Data is ready")

            return T, K, N, nS, nD, nN, nT, nK, nE, B, Sikt, djkt, Cijkt, uijt, blocked, bt, aij, edge_dict, k1_nodes, k2_nodes