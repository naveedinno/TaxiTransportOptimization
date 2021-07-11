import json
from datetime import date, datetime, time, timedelta

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

import GraphUtils as gu
from Trip import Trip
from TimeUtils import timer

class Phase2:

    def __init__(self, dataset_path, matrixd_path):
        self.dataset_path = dataset_path
        self.matrixd_path = matrixd_path
        self.dist = {}
        self.trips = []
        with open(self.matrixd_path, "r") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                a = [token for token in line.strip().split("  ") if token][1:]
                for j, token in enumerate(a):
                    self.dist[(i, i + j)] = int(token)
                    self.dist[(i + j, i)] = int(token)

        with open(self.dataset_path, "r") as f:
            lines = f.readlines()[1:]
            for line in lines:
                self.trips.append(Trip(*line.split(",")))

        self.N = len(self.trips)
        self.G = nx.DiGraph()
        self.pos = {}
        
    @timer
    def solve(self, bypass_weight=0, input_flow=None):
        if input_flow is None:
            input_flow = self.N

        self.G.add_node("A_start", demand=-input_flow)
        self.G.add_node("A_end", demand=input_flow)

        self.pos["A_start"] = np.array([0, -self.N * 50])
        self.pos["A_end"] = np.array([900, -self.N * 50])

        for i, trip in enumerate(self.trips):
            self.G.add_node(f"{i}_start", demand=1)
            self.G.add_node(f"{i}_end", demand=-1)

            self.pos[f"{i}_start"] = np.array([300, -100 * i])
            self.pos[f"{i}_end"] = np.array([600, -100 * i])

            self.G.add_edge("A_start", f"{i}_start", capacity=1, weight=self.dist[(1, trip.source)])
            self.G.add_edge(f"{i}_end", "A_end", capacity=1, weight=self.dist[(trip.destination, 1)])

        for i, trip1 in enumerate(self.trips):
            for j, trip2 in enumerate(self.trips):
                if (
                    trip1.endTime + timedelta(minutes=self.dist[(trip1.destination, trip2.source)])
                    <= trip2.endTime - timedelta(minutes=self.dist[(trip2.source, trip2.destination)])
                ):
                    self.G.add_edge(f"{i}_end", f"{j}_start", capacity=1, weight=self.dist[(trip1.destination, trip2.source)],)

        self.G.add_edge("A_start", "A_end", weight=bypass_weight)

        return nx.network_simplex(self.G)

    def plot(self, flowDict):
            gu.draw_graph(self.G.edges, self.G.nodes, self.pos, flowDict).show()


if __name__ == "__main__":
    dataset_path = "dataset/General-Dataset-1.txt"
    matrixd_path = "dataset/MarixD_dataset1_General.txt"
    solver = Phase2(dataset_path, matrixd_path)
    flowCost, flowDict = solver.solve()
    if solver.N < 20:
        solver.plot(flowDict)

    print("The result for Network model (phase 2):")
    print(f"Environmental cost : {flowCost}")
    print(f"Optimal number of cars : {solver.N-flowDict['A_start']['A_end']}")