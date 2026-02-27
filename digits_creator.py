import random
from digits_solver import solve_digits


def create_digits(
    height,
    width,
    num_range=(1, 100),
    goal_range=(100, 1000),
    min_solutions=2,
    max_solutions=None,
    max_attempts=500,
):
    for _ in range(max_attempts):
        matrix = []
        for i in range(height):
            row = []
            for j in range(width):
                row.append(random.randrange(num_range[0], num_range[1]))
            matrix.append(row)
        goal = random.randrange(goal_range[0], goal_range[1])
        solutions = solve_digits(matrix, goal)
        count = len(solutions)
        if count >= min_solutions and (max_solutions is None or count <= max_solutions):
            return matrix, goal, solutions
    raise RuntimeError(
        f"Could not generate a valid puzzle after {max_attempts} attempts "
        f"(num_range={num_range}, goal_range={goal_range}, "
        f"min_solutions={min_solutions}, max_solutions={max_solutions})"
    )
