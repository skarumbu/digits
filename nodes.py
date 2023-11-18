class Nodes:
    def __init__(self, height, width):
        self.nodes = [[0]*width for i in range(height)]
        self.solutions = []
        self.debug = True

    def create_node_without_neighbors(self, value, neighbors, row, column):
        self.nodes[row][column] = Node(value, neighbors)
        return self.nodes[row][column]

    def create_neighbors(self):
        for row in range(len(self.nodes)):
            for column in range(len(self.nodes[row])): 
                self.nodes[row][column].clear_neighbors()
                if row + 1 < len(self.nodes):
                    self.nodes[row][column].add_neighbor(self.nodes[row + 1][column])
                if row - 1 >= 0:
                    self.nodes[row][column].add_neighbor(self.nodes[row - 1][column])
                if column + 1 < len(self.nodes[row]):
                    self.nodes[row][column].add_neighbor(self.nodes[row][column + 1])
                if column - 1 >= 0:
                    self.nodes[row][column].add_neighbor(self.nodes[row][column - 1])

    def solve(self, goal):
        for row in range(len(self.nodes)):
            for column in range(len(self.nodes[row])): 
                # Try to solve from every starting point
                self.solve_from_node(goal, row, column, self.nodes[row][column].value, "")
                self.mark_nodes_unvisited()
        return self.solutions
                
    # this function is very messy and hard to read
    # prioritizing implementation first
    # current_value already has the value of the current node it's on, just because otherwise it wouldn't know what operation
    def solve_from_node(self, goal, row, column, current_value, path):
        if self.debug:
            print("Row Column: " + str(row) + ", " + str(column) + ". path: " + path + str(self.nodes[row][column].value) + ". value: " + str(current_value))             
        if current_value == goal:
            self.solutions.append(path + str(self.nodes[row][column].value))
        elif current_value > 0:
            self.nodes[row][column].visited = True
            if row + 1 < len(self.nodes) and self.nodes[row + 1][column].visited == False:
                self.traverse_with_all_operations(goal, row + 1, column, current_value, path + str(self.nodes[row][column].value))
            if row - 1 >= 0 and self.nodes[row - 1][column].visited == False:
                self.traverse_with_all_operations(goal, row - 1, column, current_value, path + str(self.nodes[row][column].value))
            if column + 1 < len(self.nodes[row]) and self.nodes[row][column + 1].visited == False:
                self.traverse_with_all_operations(goal, row, column + 1, current_value, path + str(self.nodes[row][column].value))
            if column - 1 >= 0 and self.nodes[row][column - 1].visited == False:
                self.traverse_with_all_operations(goal, row, column - 1, current_value, path + str(self.nodes[row][column].value))
        self.nodes[row][column].visited = False
        
    def traverse_with_all_operations(self, goal, row, column, current_value, path):
            self.solve_from_node(goal, row, column, current_value + self.nodes[row][column].value, path + "+")
            self.solve_from_node(goal, row, column, current_value - self.nodes[row][column].value, path + "-")
            self.solve_from_node(goal, row, column, current_value * self.nodes[row][column].value, path + "*")
            if current_value % self.nodes[row][column].value == 0:
                self.solve_from_node(goal, row, column, current_value / self.nodes[row][column].value, path + "/")

    def mark_nodes_unvisited(self):
        for row in self.nodes:
            for node in row:
                node.visited = False

class Node:
    def __init__(self, value, neighbors):
        self.neighbors = neighbors
        self.value = value
        self.visited = False

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def clear_neighbors(self):
        self.neighbors.clear()

    def __repr__(self):
        return ("Value: " + str(self.value) + ", number of neighbors: " + str(len(self.neighbors)))
