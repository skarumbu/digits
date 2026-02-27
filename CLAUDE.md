# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repo implements a variant of the NYT Digits puzzle game — a math puzzle where players combine adjacent numbers on a grid using arithmetic to reach a target goal. It exposes puzzle generation via an Azure Functions HTTP API.

## Running Locally

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the Azure Function locally (requires [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)):
```bash
func start
```

The `DigitsGetter` endpoint is available at `GET http://localhost:7071/api/DigitsGetter`.

To test puzzle generation or solving directly in Python:
```bash
python -c "from digits_creator import create_digits; print(create_digits(2, 3))"
python -c "from digits_solver import solve_digits; print(solve_digits([[3,40,1],[24,12,94]], 500))"
```

## Architecture

**Core logic** (`nodes.py`, `digits_solver.py`, `digits_creator.py`):
- `nodes.py` — `Node` represents a grid cell with a value and visited flag. `Nodes` manages the grid, builds adjacency (4-directional neighbors), and implements the recursive DFS solver (`solve_from_node` / `traverse_with_all_operations`). Solutions are paths of the form `"3+40*12"` (operations between adjacent nodes).
- `digits_solver.py` — thin wrapper: initializes `Nodes`, populates it from a 2D list, and calls `nodes.solve(goal)`. **Note:** `solve_digits` mutates the input matrix in-place, replacing integer values with `Node` objects.
- `digits_creator.py` — generates random 2D grids and goals, calls `solve_digits`, and retries until the solution count satisfies the configured bounds. Accepts `num_range`, `goal_range`, `min_solutions`, `max_solutions`, and `max_attempts` (default 500) parameters; raises `RuntimeError` if no valid puzzle is found within `max_attempts`.

**API layer** (`function_app.py`):
- Azure Functions v2 app with a single anonymous `GET /api/DigitsGetter` route.
- Generates 3 puzzles per request (one per difficulty) of size `PUZZLE_HEIGHT x PUZZLE_WIDTH` (2×3), driven by `DIFFICULTY_CONFIGS`.
- Returns JSON with `goalList`, `solutionList`, `matrixList` (flattened integer values extracted post-mutation), and `difficultyList`.

**Difficulty system** (`DIFFICULTY_CONFIGS` in `function_app.py`):

| Difficulty | num_range | goal_range  | min_solutions | max_solutions |
|------------|-----------|-------------|---------------|---------------|
| easy       | (1, 25)   | (50, 200)   | 5             | None          |
| medium     | (1, 100)  | (100, 1000) | 2             | None          |
| hard       | (1, 100)  | (500, 5000) | 1             | 5             |

Difficulty is tuned by: smaller numbers + lower goals + more required solutions = easier; higher goals + solution cap = harder (forces multiplication chains, fewer valid paths).

**Legacy** (`handler.py`):
- Original AWS Lambda handler — writes a single puzzle to a DynamoDB table. Superseded by the Azure Functions approach; kept for reference.

## Key Constraints

- The solver only prunes paths where `current_value <= 0` (stops traversal for non-positive intermediates) and only allows integer division (no remainder).
- `create_digits` retries until the solution count is within `[min_solutions, max_solutions]`; it raises `RuntimeError` after `max_attempts` (default 500) if no valid puzzle is found.
- The puzzle grid defaults to 2 rows × 3 columns; changing `PUZZLE_HEIGHT`/`PUZZLE_WIDTH` in `function_app.py` changes the puzzle size for all generated puzzles.
