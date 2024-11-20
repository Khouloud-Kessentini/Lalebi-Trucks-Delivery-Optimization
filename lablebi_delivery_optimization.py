from docplex.mp.model import Model
import math
import os

class Coordinate:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

class CVRPData:
    def __init__(self, name, dimension, capacity, nodes, costMatrix, depot):
        self.name = name
        self.dimension = dimension
        self.capacity = capacity
        self.nodes = nodes
        self.costMatrix = costMatrix
        self.depot = depot

def euclidean_distance(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    dist = math.sqrt(dx * dx + dy * dy)
    return int(round(dist))

def parse_data(filename):
    data = CVRPData("", 0, 0, [], [], 0)
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("NAME"):
                data.name = line.split(":")[1].strip()
            elif line.startswith("DIMENSION"):
                data.dimension = int(line.split(":")[1].strip())
                data.nodes = [None] * data.dimension
            elif line.startswith("CAPACITY"):
                data.capacity = float(line.split(":")[1].strip())
            elif line.startswith("NODE_COORD_SECTION"):
                for i in range(data.dimension):
                    id, x, y = map(float, file.readline().split())
                    data.nodes[int(id) - 1] = Coordinate(int(id), x, y)
                data.costMatrix = [[euclidean_distance(data.nodes[i], data.nodes[j]) for j in range(data.dimension)] for i in range(data.dimension)]
            elif line.startswith("DEMAND_SECTION"):
                for i in range(data.dimension):
                    id, demand = map(int, file.readline().split())
                    data.nodes[id - 1].demand = demand
            elif line.startswith("DEPOT_SECTION"):
                data.depot = int(file.readline().strip()) - 1
            elif line.startswith("EOF"):
                break
    return data

from matplotlib import pyplot as plt

def solve_cvrp(data, K, file_name):
    n = data.dimension - 1  # Number of customer nodes ( -1 for depot)
    Q = data.capacity

    mdl = Model()

    # Create variables
    x = mdl.binary_var_cube(K, n + 1, n + 1, name="x")  # Vehicle flow binary variables
    y = mdl.continuous_var_list(n + 1, name="y")  # Load variables

    # Objective function: minimize total travel distance
    mdl.minimize(mdl.sum(data.costMatrix[i][j] * x[k, i, j] for k in range(K) for i in range(n + 1) for j in range(n + 1)))

    # Flow conservation constraints
    mdl.add_constraints(mdl.sum(x[k, i, h] for i in range(n + 1)) == mdl.sum(x[k, h, j] for j in range(n + 1))
                        for k in range(K) for h in range(1, n + 1))

    # Each node must be visited exactly once by one vehicle
    mdl.add_constraints(mdl.sum(x[k, i, j] for k in range(K) for j in range(n + 1)) == 1
                        for i in range(1, n + 1))
    
    # No travel from a node to itself
    mdl.add_constraints(mdl.sum(x[k, i, j] for k in range(K) for j in range(n + 1) if i == j) == 0
                        for i in range(n + 1))

    # Each vehicle must leave the depot once
    mdl.add_constraints(mdl.sum(x[k, data.depot, j] for j in range(1, n + 1)) == 1 for k in range(K))

    # Capacity constraints
    mdl.add_constraints(mdl.sum(data.nodes[j].demand * x[k, i, j] for i in range(n + 1) for j in range(1, n + 1)) <= Q
                        for k in range(K))

    # Subtour elimination constraints
    mdl.add_constraints(y[j] - y[i] >= data.nodes[j].demand - Q * (1 - x[k, i, j])
                        for k in range(K) for i in range(n + 1) for j in range(1, n + 1) if i != j)

    # Bounds on the y variables
    mdl.add_constraints(y[i] >= data.nodes[i].demand for i in range(1, n + 1))
    mdl.add_constraints(y[i] <= Q for i in range(1, n + 1))

    # Solve the model
    mdl.parameters.timelimit = 3600
    mdl.context.solver.log_output = True
    solution = mdl.solve()

    # Print the solution
    if solution:
        print("Solution status:", solution.solve_status)
        print("Objective value (total distance):", solution.objective_value)

        # Reconstruct routes in the correct order
        routes = [[data.depot] for _ in range(K)]
        for k in range(K):
            current_node = data.depot
            while True:
                for j in range(n + 1):
                    if x[k, current_node, j].solution_value > 0.5:
                        routes[k].append(j)
                        current_node = j
                        break
                if current_node == data.depot:
                    break
        print(routes)
        # Visualization
        plt.figure(figsize=(10, 6))
        for k, route in enumerate(routes):
            x_coords = [data.nodes[i].x for i in route]
            y_coords = [data.nodes[i].y for i in route]
            plt.plot(x_coords, y_coords, marker='o', label=f"Vehicle {k + 1}")
        
        depot = data.nodes[data.depot]
        plt.scatter(depot.x, depot.y, c='red', s=100, label="Depot")
        plt.title("Optimal routes for Lablebi delivery trucks")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.legend()
        plt.grid(True)
        plt.show()
    else:
        print("No solution found.")

if __name__ == "__main__":
    for instance in ["E-n23-k3.vrp"]:
        for v in [3]:
            data = parse_data(f"input/{instance}")
            solve_cvrp(data, v, f"{instance}-k{v}")
