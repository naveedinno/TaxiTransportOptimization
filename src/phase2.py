import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import os

class Trip:
    def __init__(self, startTime, endTime, source, destination):
        self.startTime = int(startTime.strip())
        self.endTime = int(endTime.strip())
        self.source = int(source.strip())
        self.destination = int(destination.strip())

    def __str__(self):
        return f"{self.startTime}:{self.endTime}:{self.source}:{self.destination}"


fileDir = os.path.dirname(os.path.realpath("__file__"))
dataset_path = os.path.join(fileDir, "dataset/General-Dataset-1.txt")
matrixd_path = os.path.join(fileDir, "dataset/MarixD_dataset1_General.txt")

dist = {}
pos = {}
trips = []

with open(matrixd_path, "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        a = [token for token in line.strip().split("  ") if token][1:]
        for j, token in enumerate(a):
            dist[(i, i + j)] = int(token)
            dist[(i + j, i)] =  int(token)


with open(dataset_path, "r") as f:
    lines = f.readlines()[1:]
    for line in lines:
        trips.append(Trip(*line.split(",")))

G = nx.DiGraph()

N = len(trips)

G.add_node("as", demand=-N)
G.add_node("ae", demand=N)

pos["as"] = np.array([0, -(N-1) * 50])
pos["ae"] = np.array([900, -(N-1) * 50])

for i, trip in enumerate(trips):
    G.add_node(f"{i}s", demand=1)
    G.add_node(f"{i}e", demand=-1)

    pos[f"{i}s"] = np.array([300, -100 * i])
    pos[f"{i}e"] = np.array([600, -100 * i])

    G.add_edge("as", f"{i}s", capacity=1, cost=dist[(1, trip.source)])
    G.add_edge(f"{i}e", "ae", capacity=1, cost=dist[(trip.destination, 1)])

for i, trip1 in enumerate(trips):
    for j, trip2 in enumerate(trips):
        if trip1.endTime + dist[(trip1.destination, trip2.source)] <= trip2.endTime - dist[(trip2.source, trip2.destination)]:
            G.add_edge(f"{i}e", f"{j}s", capacity=1, cost=dist[(trip1.destination, trip2.source)])

G.add_edge("as", "ae", cost=0)

flowCost, flowDict = nx.network_simplex(G, weight="cost")

print(f"flowCost : {flowCost}")
print(f"min number of cars : {N-flowDict['as']['ae']}")

# print(json.dumps(flowDict, indent=4, sort_keys=True))

if N < 20:
    nx.draw_networkx(G, with_labels=True, pos=pos, node_color="#47a0ff")
    plt.show()
