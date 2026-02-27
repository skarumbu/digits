import azure.functions as func
import json
import logging
from digits_creator import create_digits

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

NUM_PUZZLES = 3
PUZZLE_HEIGHT = 2
PUZZLE_WIDTH = 3

@app.route(route="DigitsGetter", methods=["GET"])
def DigitsGetter(req: func.HttpRequest) -> func.HttpResponse:
    try:
        goal_list = []
        solution_list = []
        matrix_list = []

        for _ in range(NUM_PUZZLES):
            matrix, goal, solutions = create_digits(PUZZLE_HEIGHT, PUZZLE_WIDTH)
            goal_list.append(goal)
            solution_list.append(solutions)
            # solve_digits mutates matrix in-place, replacing ints with Node objects;
            # extract the original integer values via .value
            for row in matrix:
                matrix_list.append([node.value for node in row])

        body = {
            "Item": {
                "goalList":     {"S": json.dumps(goal_list)},
                "solutionList": {"S": json.dumps(solution_list)},
                "matrixList":   {"S": json.dumps(matrix_list)},
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
