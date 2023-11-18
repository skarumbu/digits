import random
from digits_solver import solve_digits 

def create_digits(height, width):
    while True:
        matrix = []
        for i in range(height):
            row = []
            for j in range(width):
                row.append(random.randrange(1, 100))
            matrix.append(row)
        goal = random.randrange(100, 1000)
        solutions = solve_digits(matrix, goal)
        if (len(solutions) > 1):
            return matrix, goal, solutions

matrix, goal, solutions = create_digits(2,3)
print(matrix)
print(goal)
print(solutions)
