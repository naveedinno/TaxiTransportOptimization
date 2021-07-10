import pulp


class Trip:
    def __init__(self, startTime, endTime, source, destination):
        self.startTime = int(startTime.strip())
        self.endTime = int(endTime.strip())
        self.source = int(source.strip())
        self.destination = int(destination.strip())

    def __str__(self):
        return f"{self.startTime}:{self.endTime}:{self.source}:{self.destination}"


dataset_path = "dataset/General-Dataset-2.txt"
matrixd_path = "dataset/MarixD_dataset1_General.txt"

dist = {}
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

model = pulp.LpProblem(name="Phase2", sense=pulp.LpMinimize)
variables = {}
variables_by_nodes = {}
objective_list = []

for i in range(N):
    variables_by_nodes[f"{i}s_out"] = []
    variables_by_nodes[f"{i}s_in"] = []
    variables_by_nodes[f"{i}e_out"] = []
    variables_by_nodes[f"{i}e_in"] = []

variables_by_nodes["A_in"] = []
variables_by_nodes["A_out"] = []


for i, trip in enumerate(trips):
    var_name = f"A_{i}s"
    var = variables[var_name] = pulp.LpVariable(name=var_name, lowBound=0, upBound=1, cat='Integer')
    variables_by_nodes["A_out"].append(var)
    variables_by_nodes[f"{i}s_in"].append(var)
    objective_list.append(dist[(1, trip.source)] * var)

    var_name = f"{i}e_A"
    var = variables[var_name] = pulp.LpVariable(name=var_name, lowBound=0, upBound=1, cat='Integer')
    variables_by_nodes["A_in"].append(var)
    variables_by_nodes[f"{i}e_out"].append(var)
    objective_list.append(dist[(trip.destination, 1)] * var)

    var_name = f"{i}s_{i}e"
    var = variables[var_name] = pulp.LpVariable(name=var_name, lowBound=1, upBound=1, cat='Integer')
    variables_by_nodes[f"{i}s_out"].append(var)
    variables_by_nodes[f"{i}e_in"].append(var)

for i, trip1 in enumerate(trips):
    for j, trip2 in enumerate(trips):
        if (
            trip1.endTime + dist[(trip1.destination, trip2.source)]
            <= trip2.endTime - dist[(trip2.source, trip2.destination)]
        ):
            var_name = f"{i}e_{j}s"
            var = variables[var_name] = pulp.LpVariable(name=var_name, lowBound=0, upBound=1, cat='Integer')
            variables_by_nodes[f"{i}e_out"].append(var)
            variables_by_nodes[f"{j}s_in"].append(var)
            objective_list.append(dist[trip1.destination, trip2.source] * var)

var_name = f"A_A"
var = variables[var_name] = pulp.LpVariable(name=var_name, lowBound=0, upBound=N, cat='Integer')
variables_by_nodes["A_out"].append(var)
variables_by_nodes["A_in"].append(var)
objective_list.append(0 * var)

model += (sum(variables_by_nodes["A_out"]) == N)

model += (sum(variables_by_nodes["A_in"]) == N)

for i in range(N):
    model += (sum(variables_by_nodes[f"{i}s_out"]) - sum(variables_by_nodes[f"{i}s_in"]) == 0, f"{i}s")
    model += (sum(variables_by_nodes[f"{i}e_out"]) - sum(variables_by_nodes[f"{i}e_in"]) == 0, f"{i}e")

obj_func = sum(objective_list)
model += obj_func

print("----------------------------")
print("Solution is found" if model.solve() == 1 else "Problem is infeasible")

# if model.status != -1:
#     for var in model.variables():
#         print(f"{var.name}: {var.value()}")

print(f"flowCost : {model.objective.value()}")
print(f"min number of cars : {N-variables['A_A'].value()}")