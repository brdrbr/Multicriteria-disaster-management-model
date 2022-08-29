import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from dataread import uijt


def update_blocked_capacities(uijt, blocked):
    uijt_tmp = [i[2] for i in uijt[0][0]]
    blocked = [i[2] for i in blocked[0]]

    uijt_selecting = np.multiply(uijt_tmp, blocked)

    for i in range(len(np.where(uijt_selecting == 0)[0])):

        change = np.where(uijt_selecting == 0)[0][i]
        uijt[0][0][change][2] = 0

    return uijt


def graph_drawer(nT, nK, nN, nS, Sikt, djkt, Model, l):
    counter = 1
    periodcounter = 1
    commoditycounter = 1

    for i in nT:
        for j in nK:
            supplynodes = []
            demandnodes = []
            transhipmentnodes = []
            for key, value in Sikt[i][j].items():
                if value != 0:
                    supplynodes.append(key)
            for key, value in djkt[i][j].items():
                if value != 0:
                    demandnodes.append(key)
            for w in nN:
                if w not in supplynodes and w not in demandnodes:
                    transhipmentnodes.append(w)

            G = nx.DiGraph()

            for k in nS:
                for key, value in Model.X.get_values().items():
                    if str(key[0])[0] == str(k) and str(key[1]) == str(j) and str(key[2]) == str(i):
                        if value != 0.0:
                            G.add_edge(int(str(k)), int(str(key[0])[1]), edge_label=str(value))
            color_map = []
            for node in G:
                if node in supplynodes:
                    color_map.append('orange')
                elif node in demandnodes:
                    color_map.append('green')
                else:
                    color_map.append('blue')

            # colorizing edges
            edge_list = G.edges(data=True)
            edge_list_updated = {}

            for edge in edge_list:
                edg = int(str(edge[0]) + str(edge[1]))
                val = float(edge[2]["edge_label"])
                edge_list_updated[edg] = val

            green = []
            red = []
            for edge in uijt[i]:
                if edge[0] in edge_list_updated.keys():
                    if edge_list_updated[edge[0]] == edge[1]:
                        green.append(edge[0])
                    elif edge_list_updated[edge[0]] < edge[1]:
                        red.append(edge[0])

            green_updated = []
            red_updated = []
            for g in green:
                f1 = str(g)[0]
                s1 = str(g)[1]
                green_updated.append((int(f1), int(s1)))

            for r in red:
                f2 = str(r)[0]
                s2 = str(r)[1]
                red_updated.append((int(f2), int(s2)))

            plt.figure(counter)
            plt.title("Period: " + str(periodcounter) + " Commodity: " + str(commoditycounter))
            pos = nx.spring_layout(G)
            nx.draw(G, pos, node_color=color_map, with_labels=True)

            nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=green_updated,
                width=1.0,
                alpha=0.5,
                edge_color="tab:green",
            )
            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=red_updated,
                width=1.0,
                alpha=0.5,
                edge_color="tab:red",
            )

            nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'edge_label'))

            plt.savefig(f'Obj_{l+1}_{"Period_" + str(periodcounter) + "_Commodity_" + str(commoditycounter)}.png')
            plt.close()

            commoditycounter = commoditycounter + 1
            periodcounter = periodcounter + 1
            counter = counter + 1

        commoditycounter = 1


def excel_writer(nT, nK, djkt, Model, l):
    data = {}
    demandnodes = []
    for i in nT:
        for j in nK:
            for key, value in djkt[i][j].items():
                if value != 0:
                    if key not in demandnodes:
                        demandnodes.append(key)
    df = pd.DataFrame(data)
    df[""] = demandnodes

    for i in nT:
        for j in nK:
            djktlist = []
            Dlist = []
            percentage = []
            Hlist = []
            NetList = []
            for key, value in djkt[i][j].items():
                if key in demandnodes:
                    djktlist.append(value)
            for (key, value), (key2, value2) in zip(Model.D.get_values().items(), Model.H.get_values().items()):
                if key[0] in demandnodes and key[0] == key2[0] and j == key[1] and i == key[2]:
                    Dlist.append(int(value))  # total demand - unsatisfied demand
                    Hlist.append(int(value2))
                    NetList.append(int(value) - int(value2))

            df["djkt(C" + str(j + 1) + "T" + str(i + 1) + ")"] = djktlist
            df["Djkt(C" + str(j + 1) + "T" + str(i + 1) + ")"] = Dlist
            df["Hjkt(C" + str(j + 1) + "T" + str(i + 1) + ")"] = Hlist
            df["Satisfied demand" + "(C" + str(j + 1) + "T" + str(i + 1) + ")"] = [a - b for a, b in zip(Dlist, Hlist)]

            for m in range(len(djktlist)):
                percentage.append(str(str(round((NetList[m] / Dlist[m] * 100), 2)) + "%"))

            df["Percentage Satisfied" + "(C" + str(j + 1) + "T" + str(i + 1) + ")"] = percentage

    df.set_index('', drop=True, inplace=True)

    writer = pd.ExcelWriter(f'output_obj_{l+1}.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name=f"Demand Data Obj {l+1}")
    writer.save()




