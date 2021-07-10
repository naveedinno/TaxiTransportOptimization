from Phase2 import Phase2
from Phase1 import Phase1

inf = 1000000000000
dataset_path = "dataset/General-Dataset-3.txt"
matrixd_path = "dataset/MarixD_dataset1_General.txt"


# Version 1
solver = Phase2(dataset_path, matrixd_path)
print("The result for Phase3 (V.1):")
flowCost, flowDict = solver.solve(bypass_weight=-1)
print(f"Environmental cost : {flowCost}")
print(f"Optimal number of cars : {solver.N-flowDict['A_start']['A_end']}")
# solver.plot(flowDict)


# Version 2
solver1 = Phase1(dataset_path, matrixd_path)
solver2 = Phase2(dataset_path, matrixd_path)
min_cost, min_flow = solver2.solve()
flowCost, flowDict = solver1.solve()
min_cars = solver1.N-flowDict['A_start']['A_end']
optimal_cars = min_cars
optimal_cost, optiaml_flow = solver2.solve(bypass_weight=inf, input_flow=min_cars)

for car_number in range(min_cars + 1, int(1.1*min_cars)):
    if optimal_cost == min_cost:
        break

    flowCost, flowDict = solver2.solve(bypass_weight=inf, input_flow=car_number)
    bypass_flow = flowDict["A_start"]["A_end"]
    if flowCost < optimal_cost:
        optimal_cost = flowCost
        optiaml_flow = flowDict
        optimal_cars = car_number - bypass_flow
    print(car_number, flowCost, optimal_cost, bypass_flow)

print("======================================")
print("The result for Phase3 (V.2):")
print(f"Environmental cost: {optimal_cost}")
print(f"Optimal number of cars (with respect to 10% loss in profit of the taxi numbers for benefit of environment): {optimal_cars}")
print(f"Minimum possible number of cars: {min_cars}")
print(f"Minimum possible value for environmental cost: {min_cost}")
# solver2.plot(optiaml_flow)
