import pulp


class Trip:
    def __init__(self, startTime, endTime, source, destination):
        self.startTime = int(startTime.strip())
        self.endTime = int(endTime.strip())
        self.source = int(source.strip())
        self.destination = int(destination.strip())

    def __str__(self):
        return f"{self.startTime}:{self.endTime}:{self.source}:{self.destination}"


dataset_path = "dataset/General-Dataset-1.txt"
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

model = pulp.LpProblem(name="Phase1", sense=pulp.LpMinimize)
variables = {}

for i, trip in enumerate(trips):
    var_name = f"A_{i}s"
    variables[var_name] = pulp.LpVariable(name=var_name, lowBound=0, upBound=1, cat='Integer')
    var_name = f"{i}e_A"
    variables[var_name] = pulp.LpVariable(name=var_name, lowBound=0, upBound=1, cat='Integer')
    # var_name = f"{i}s_{i}e"
    # variables[var_name] = pulp.LpVariable(name=var_name, lowBound=1, upBound=1, cat='Integer')

for i, trip1 in enumerate(trips):
    for j, trip2 in enumerate(trips):
        if (
            trip1.endTime + dist[(trip1.destination, trip2.source)]
            <= trip2.endTime - dist[(trip2.source, trip2.destination)]
        ):
            var_name = f"{i}e_{j}s"
            variables[var_name] = pulp.LpVariable(name=var_name, lowBound=0, upBound=1, cat='Integer')

var_name = f"A_A"
variables[var_name] = pulp.LpVariable(name=var_name, lowBound=0, upBound=N, cat='Integer')

lst = [var for var_name, var in variables.items() if 'A_' in var_name]
model += (sum(lst) == N)

lst = [var for var_name, var in variables.items() if '_A' in var_name]
model += (sum(lst) == N)

for i in range(N):
    out_list = [var for var_name, var in variables.items() if f"{i}s_" in var_name]
    in_list = [var for var_name, var in variables.items() if f"_{i}s" in var_name]
    model += (sum(in_list) - sum(out_list) == 1)

    out_list = [var for var_name, var in variables.items() if f"{i}e_" in var_name]
    in_list = [var for var_name, var in variables.items() if f"_{i}e" in var_name]
    model += (sum(in_list) - sum(out_list) == -1)

obj_func = -1 * variables['A_A']
model += obj_func

print("----------------------------")
print(model.solve(solver=pulp.GLPK(msg=False)))
print(model.objective.value())

if model.status != -1:
    for var in model.variables():
        print(f"{var.name}: {var.value()}")

print(f"min number of cars : {N-variables['A_A'].value()}")