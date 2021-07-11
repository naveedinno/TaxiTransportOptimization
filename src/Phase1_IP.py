from datetime import date, datetime, time, timedelta

import pulp

from Trip import Trip
from TimeUtils import timer

class Phase1_IP:
    
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
    

    @timer
    def solve(self):
        self.variables = {}
        self.variables_by_nodes = {}
        self.model = pulp.LpProblem(name="Phase1", sense=pulp.LpMinimize)
        
        for i in range(self.N):
            self.variables_by_nodes[f"{i}s_out"] = []
            self.variables_by_nodes[f"{i}s_in"] = []
            self.variables_by_nodes[f"{i}e_out"] = []
            self.variables_by_nodes[f"{i}e_in"] = []

        self.variables_by_nodes["A_in"] = []
        self.variables_by_nodes["A_out"] = []


        for i, trip in enumerate(self.trips):
            var_name = f"A_{i}s"
            var = self.variables[var_name] = pulp.LpVariable(name=var_name, lowBound=0, upBound=1, cat='Integer')
            self.variables_by_nodes["A_out"].append(var)
            self.variables_by_nodes[f"{i}s_in"].append(var)

            var_name = f"{i}e_A"
            var = self.variables[var_name] = pulp.LpVariable(name=var_name, lowBound=0, upBound=1, cat='Integer')
            self.variables_by_nodes["A_in"].append(var)
            self.variables_by_nodes[f"{i}e_out"].append(var)

            var_name = f"{i}s_{i}e"
            var = self.variables[var_name] = pulp.LpVariable(name=var_name, lowBound=1, upBound=1, cat='Integer')
            self.variables_by_nodes[f"{i}s_out"].append(var)
            self.variables_by_nodes[f"{i}e_in"].append(var)

        for i, trip1 in enumerate(self.trips):
            for j, trip2 in enumerate(self.trips):
                if (
                    trip1.endTime + timedelta(minutes=self.dist[(trip1.destination, trip2.source)])
                    <= trip2.endTime - timedelta(minutes=self.dist[(trip2.source, trip2.destination)])
                ):
                    var_name = f"{i}e_{j}s"
                    var = self.variables[var_name] = pulp.LpVariable(name=var_name, lowBound=0, upBound=1, cat='Integer')
                    self.variables_by_nodes[f"{i}e_out"].append(var)
                    self.variables_by_nodes[f"{j}s_in"].append(var)

        var_name = f"A_A"
        var = self.variables[var_name] = pulp.LpVariable(name=var_name, lowBound=0, upBound=self.N, cat='Integer')
        self.variables_by_nodes["A_out"].append(var)
        self.variables_by_nodes["A_in"].append(var)

        self.model += (sum(self.variables_by_nodes["A_out"]) == self.N)

        self.model += (sum(self.variables_by_nodes["A_in"]) == self.N)

        for i in range(self.N):
            self.model += (sum(self.variables_by_nodes[f"{i}s_out"]) - sum(self.variables_by_nodes[f"{i}s_in"]) == 0, f"{i}s")
            self.model += (sum(self.variables_by_nodes[f"{i}e_out"]) - sum(self.variables_by_nodes[f"{i}e_in"]) == 0, f"{i}e")

        obj_func = -1 * self.variables['A_A']
        self.model += obj_func
        return self.model.solve()

if __name__ == "__main__":
    dataset_path = "dataset/General-Dataset-2.txt"
    matrixd_path = "dataset/MarixD_dataset1_General.txt"
    solver = Phase1_IP(dataset_path, matrixd_path)
    state = solver.solve()
    print("The result for ILP model (phase 1):")
    print("Solution found" if state == 1 else "Problem is infeasible")
    if state == 1:
        print(f"Min number of cars : {solver.N-solver.variables['A_A'].value()}")
