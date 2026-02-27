import azure.functions as func
import json
import logging
from digits_creator import create_digits

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

PUZZLE_HEIGHT = 2
PUZZLE_WIDTH = 3

DIFFICULTY_CONFIGS = [
    {"difficulty": "easy",   "num_range": (1, 25),  "goal_range": (50, 200),   "min_solutions": 5, "max_solutions": None},
    {"difficulty": "medium", "num_range": (1, 100), "goal_range": (100, 1000), "min_solutions": 2, "max_solutions": None},
    {"difficulty": "hard",   "num_range": (1, 100), "goal_range": (500, 5000), "min_solutions": 1, "max_solutions": 5},
]

@app.route(route="DigitsGetter", methods=["GET"])
def DigitsGetter(req: func.HttpRequest) -> func.HttpResponse:
    try:
        goal_list       = []
        solution_list   = []
        matrix_list     = []
        difficulty_list = []

        for config in DIFFICULTY_CONFIGS:
            matrix, goal, solutions = create_digits(
                PUZZLE_HEIGHT,
                PUZZLE_WIDTH,
                num_range=config["num_range"],
                goal_range=config["goal_range"],
                min_solutions=config["min_solutions"],
                max_solutions=config["max_solutions"],
            )
            goal_list.append(goal)
            solution_list.append(solutions)
            difficulty_list.append(config["difficulty"])
            # solve_digits mutates matrix in-place, replacing ints with Node objects;
            # extract the original integer values via .value
            for row in matrix:
                matrix_list.append([node.value for node in row])

        body = {
            "Item": {
                "goalList":       {"S": json.dumps(goal_list)},
                "solutionList":   {"S": json.dumps(solution_list)},
                "matrixList":     {"S": json.dumps(matrix_list)},
                "difficultyList": {"S": json.dumps(difficulty_list)},
            }
        }

        return func.HttpResponse(
            body=json.dumps(body),
            status_code=200,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
        )

    except Exception as e:
        logging.exception("Error generating digits puzzles")
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
        )
