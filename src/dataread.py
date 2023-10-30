import pandas as pd
import numpy as np


class DataReader:

    def data_read(self, directory):

        dataframe = pd.read_excel(open(directory, 'rb'),
                                  sheet_name='Sheet1',
                                  engine='openpyxl')[:121]  # for eliminating unnecessary parts

        T = 7  # 1 week
        K = 1  # 1 commodity
        N = len(np.unique(list(dataframe.inside)))  # total number of nodes

        periods = ["t1", "t2", "t3", "t4", "t5", "t6", "t7"]
        supplies = dataframe[(f"supply_{i-1}" for i in periods)].sum(axis=1)
        demands = dataframe[(f"demand_{i-1}" for i in periods)].sum(axis=1)

        total_values = pd.concat([dataframe.inside, supplies, demands], axis=1)
        total_values.columns = ["inside", "total_supply", "total_demand"]

        nS = np.unique(list(total_values[(total_values.total_supply > 0)].inside.astype(int)))  # supply node set
        nD = np.unique(list(total_values[(total_values.total_demand > 0)].inside.astype(int)))  #demand node set
        nN = np.unique(list(total_values.inside.astype(int)))  # total node set

        nT = [1, 2, 3, 4, 5, 6, 7]
        nK = [0]

        edge_dict = {}
        for row in dataframe.iterrows():
            edge_dict[int(float(str(int(float(str(row[1].inside)))) + str(int(float(str(row[1].out))))))] = [
                int(float(row[1].inside)), int(float(row[1].out))]

        nE = list(edge_dict.keys())
        B = list(dataframe.B)

        Sikt = []
        for i in range(T):
            Sikt.append([])
            for j in range(K):
                Sikt[i].append({})

        for t in range(T):
            for k in range(K):
                for n in nN:
                    Sikt[t][k][n] = int(sum(np.unique(dataframe.loc[dataframe.inside == n, f"supply_t{t + 1}"])))

        djkt = []
        for i in range(T):
            djkt.append([])
            for j in range(K):
                djkt[i].append({})

        for t in range(T):
            for k in range(K):
                for n in nN:
                    djkt[t][k][n] = int(sum(np.unique(dataframe.loc[dataframe.inside == n, f"demand_t{t + 1}"])))

        Cijkt = []
        for i in range(T):
            Cijkt.append([])
            for j in range(K):
                Cijkt[i].append({})

        for t in range(T):
            for k in range(K):
                for n in nN:
                    Cijkt[t][k][n] = int(sum(np.unique(dataframe.loc[dataframe.inside == n, "cost"])))

        uijt = []
        for t in range(T):
            uijt.append({})

        dataframe.capacity.fillna(0, inplace=True)

        for t in range(T):
            for n in nD:
                n_cap = int(np.sum(list(dataframe.loc[dataframe.inside == n, "capacity"])))
                print(dataframe.loc[dataframe.inside == n, "capacity"])

                for edge in list(edge_dict.keys()):
                    if str(edge).find(str(n)[:-2]) == 0:
                        uijt[t][edge] = n_cap

        print(uijt)

        blocked = []
        for i in range(T):
            blocked.append({})

        for t in range(T):
            for n in nD:
                blocked[t][n] = int(sum(np.unique(dataframe.loc[dataframe.inside == n, "blocked"])))

        # Number of resources needed to restore blocked arc (i,j)
        bt = []
        for t in range(T):
            bt.append([])

        # This will depend on the previous used supply
        for t in range(T):
            bt[t] = int(np.unique(dataframe["road_restoration_supply"].fillna(0).sum()))

        aij = []
        for i in range(T):
            aij.append([])
            for j in range(K):
                aij[i].append({})

        for t in range(T):
            for k in range(K):
                for n in nN:
                    aij[t][k][n] = int(sum((dataframe[f"rest_demand_t{t + 1}"])))

        print("Data is ready")
        return T, K, N, nS, nD, nN, nT, nK, nE, B, Sikt, djkt, Cijkt, uijt, blocked, bt, aij, edge_dict