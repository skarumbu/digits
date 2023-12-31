from nodes import Nodes

# input is 3 wide and 2 high only for now, so something like:
# [3, 40, 1]
# [24, 12, 94]
def solve_digits(input, goal):
    nodes = Nodes(len(input), len(input[0]))
    for row in range(len(input)):
        for column in range(len(input[row])):
            input[row][column] = nodes.create_node_without_neighbors(input[row][column], [], row, column)

    nodes.create_neighbors()
    return nodes.solve(goal)