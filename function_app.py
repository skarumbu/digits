import azure.functions as func
import json
import logging
import os
from datetime import datetime, timezone

from azure.data.tables import TableServiceClient, UpdateMode
from azure.core.exceptions import ResourceNotFoundError

from digits_creator import create_digits

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

PUZZLE_HEIGHT = 2
PUZZLE_WIDTH = 3
TABLE_NAME = "digits"
PARTITION_KEY = "digits"

DIFFICULTY_CONFIGS = [
    {"difficulty": "easy",   "num_range": (1, 25),  "goal_range": (50, 200),   "min_solutions": 5, "max_solutions": None},
    {"difficulty": "medium", "num_range": (1, 100), "goal_range": (100, 1000), "min_solutions": 2, "max_solutions": None},
    {"difficulty": "hard",   "num_range": (1, 100), "goal_range": (500, 5000), "min_solutions": 1, "max_solutions": 5},
]


def _get_table_client():
    conn_str = os.environ["TABLE_STORAGE_CONNECTION_STRING"]
    service_client = TableServiceClient.from_connection_string(conn_str)
    service_client.create_table_if_not_exists(TABLE_NAME)
    return service_client.get_table_client(TABLE_NAME)


def _generate_puzzles() -> dict:
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
        # solve_digits mutates matrix in-place, replacing ints with Node objects
        for row in matrix:
            matrix_list.append([node.value for node in row])

    return {
        "goalList":       json.dumps(goal_list),
        "solutionList":   json.dumps(solution_list),
        "matrixList":     json.dumps(matrix_list),
        "difficultyList": json.dumps(difficulty_list),
    }


def _build_response_body(puzzles: dict) -> dict:
    return {
        "Item": {
            "goalList":       {"S": puzzles["goalList"]},
            "solutionList":   {"S": puzzles["solutionList"]},
            "matrixList":     {"S": puzzles["matrixList"]},
            "difficultyList": {"S": puzzles["difficultyList"]},
        }
    }


# Timer Trigger: runs once daily at midnight UTC
@app.timer_trigger(schedule="0 0 0 * * *", arg_name="mytimer", run_on_startup=False)
def DailyDigitsGenerator(mytimer: func.TimerRequest) -> None:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if mytimer.past_due:
        logging.warning("DailyDigitsGenerator: timer is past due. date=%s", date_str)

    logging.info("DailyDigitsGenerator: generating puzzles for %s", date_str)
    puzzles = _generate_puzzles()

    table_client = _get_table_client()
    entity = {"PartitionKey": PARTITION_KEY, "RowKey": date_str, **puzzles}
    table_client.upsert_entity(entity=entity, mode=UpdateMode.REPLACE)
    logging.info("DailyDigitsGenerator: stored puzzles for %s", date_str)


# HTTP Trigger: serves today's puzzles from Table Storage (fallback: on-demand)
@app.route(route="DigitsGetter", methods=["GET"])
def DigitsGetter(req: func.HttpRequest) -> func.HttpResponse:
    try:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        puzzles  = None

        try:
            table_client = _get_table_client()
            entity  = table_client.get_entity(partition_key=PARTITION_KEY, row_key=date_str)
            puzzles = {k: entity[k] for k in ("goalList", "solutionList", "matrixList", "difficultyList")}
            logging.info("DigitsGetter: served pre-generated puzzles for %s", date_str)
        except ResourceNotFoundError:
            logging.warning("DigitsGetter: no entry for %s, falling back to on-demand generation", date_str)

        if puzzles is None:
            puzzles = _generate_puzzles()
            try:
                table_client = _get_table_client()
                entity = {"PartitionKey": PARTITION_KEY, "RowKey": date_str, **puzzles}
                table_client.upsert_entity(entity=entity, mode=UpdateMode.REPLACE)
                logging.info("DigitsGetter: cached on-demand puzzles for %s", date_str)
            except Exception:
                logging.exception("DigitsGetter: failed to cache puzzles, continuing")

        return func.HttpResponse(
            body=json.dumps(_build_response_body(puzzles)),
            status_code=200,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
        )

    except Exception as e:
        logging.exception("DigitsGetter: error")
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
        )
