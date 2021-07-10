import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import GraphUtils as gu
from datetime import datetime, timedelta, date, time

class Trip:
    def __init__(self, startTime, endTime, source, destination):
        startTime = startTime.strip()
        self.startTime = datetime.combine(date.today(), time(hour=int(startTime[:-2]), minute=int(startTime[-2:])))
        endTime = endTime.strip()
        self.endTime = datetime.combine(date.today(), time(hour=int(endTime[:-2]), minute=int(endTime[-2:])))
        self.source = int(source.strip())
        self.destination = int(destination.strip())

    def __str__(self):
        return f"{self.startTime}:{self.endTime}:{self.source}:{self.destination}"


dataset_path = "dataset/General-Dataset-3.txt"
matrixd_path = "dataset/MarixD_dataset1_General.txt"

dist = {}
pos = {}
trips = []

with open(matrixd_path, "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        a = [token for token in line.strip().split("  ") if token][1:]
        for j, token in enumerate(a):
            dist[(i, i + j)] = int(token)
            dist[(i + j, i)] = int(token)

with open(dataset_path, "r") as f:
    lines = f.readlines()[1:]
    for line in lines:
        trips.append(Trip(*line.split(",")))
N = len(trips)

G = nx.DiGraph()

G.add_node("A_start", demand=-N)
G.add_node("A_end", demand=N)

pos["A_start"] = np.array([0, -N * 50])
pos["A_end"] = np.array([900, -N * 50])

for i, trip in enumerate(trips):
    G.add_node(f"{i}_start", demand=1)
    G.add_node(f"{i}_end", demand=-1)

    pos[f"{i}_start"] = np.array([300, -100 * i])
    pos[f"{i}_end"] = np.array([600, -100 * i])

    G.add_edge("A_start", f"{i}_start", capacity=1)
    G.add_edge(f"{i}_end", "A_end", capacity=1)

for i, trip1 in enumerate(trips):
    for j, trip2 in enumerate(trips):
        if (
            trip1.endTime + timedelta(minutes=dist[(trip1.destination, trip2.source)])
            <= trip2.endTime - timedelta(minutes=dist[(trip2.source, trip2.destination)])
        ):
            G.add_edge(f"{i}_end", f"{j}_start", capacity=1)

G.add_edge("A_start", "A_end", weight=-1)

# for e in G.edges:
#     print(e)

flowCost, flowDict = nx.network_simplex(G)

# print(f"flowCost : {flowCost}")
print(f"min number of cars : {N-flowDict['A_start']['A_end']}")

# print(json.dumps(flowDict, indent=4, sort_keys=True))

# if N < 20:
#     nx.draw_networkx(G, with_labels=True, pos=pos, node_color="#47a0ff")
#     plt.show()

if N < 20:
    gu.draw_graph(G.edges, G.nodes, pos, flowDict).show()