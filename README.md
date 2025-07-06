# Tsume Shogi Solver

A DMbutsu ShMgi (Animal Chess) solver that uses the Z3 SMT solver to find mate-in-n solutions.

## Overview

This project implements a complete solver for DMbutsu ShMgi problems, capable of:

- Finding checkmate sequences
- Analyzing piece reachability
- Solving general tsume (mate) problems
- Finding shortest solutions

## Architecture

The codebase is organized into focused modules with clear responsibilities:

### Core Game Logic

- **`core.py`** - Fundamental game types
  - Type aliases (`PieceId`, `TimeIndex`, `Position`, etc.)
  - Game enums (`PieceType`, `Player`)
  - Data structures (`PieceState`, `MoveData`)

- **`constants.py`** - Game constants
  - Default board setup (`DEFAULT_INITIAL_SETUP`)
  - Other game-specific constants

### Problem Definitions

- **`problems.py`** - Problem and solution types
  - Problem types: `CheckmateProblem`, `ReachabilityProblem`, `TsumeProblem`
  - Solution types: `CheckmateSolution`, `ReachabilitySolution`, `TsumeSolution`
  - `Solver` protocol defining the interface

### Z3 Implementation

- **`z3_models.py`** - Z3-specific models
  - `MoveVariables`: Z3 variables representing a move
  - `GameState`: Complete Z3 variable container for game state
  - Variable initialization and basic domain constraints

- **`z3_constraints.py`** - Game rule encoding
  - `GameRules`: Static methods for generating Z3 constraints
  - Movement patterns for each piece type
  - Turn alternation and victory conditions
  - Capture and promotion mechanics

### Solvers

The `solvers/` package contains specialized solver implementations:

- **`base.py`** - Base solver class with common functionality
- **`checkmate.py`** - Checkmate-specific solver
- **`reachability.py`** - Piece reachability analysis
- **`tsume.py`** - General tsume problem solver

### Public API

- **`api.py`** - User-facing convenience functions
  - `find_checkmate()` - Find checkmate sequences
  - `find_shortest_mate()` - Find optimal solutions
  - `can_reach()` - Check piece reachability
  - `find_shortest_path()` - Find optimal paths

## Usage

```python
from dobutsu_shogi_z3 import find_checkmate, find_shortest_mate

# Find any checkmate
solution = find_checkmate(max_moves=10)
if solution:
    print(f"Found mate in {solution.mate_in} moves!")
    for move in solution.moves:
        print(f"  {move}")

# Find shortest checkmate
shortest = find_shortest_mate(max_search_depth=10)
if shortest:
    print(f"Shortest mate: {shortest.mate_in} moves")
```

## Installation

```bash
# Clone the repository
git clone https://github.com/shunichironomura/dobutsu-shogi-z3.git
cd dobutsu-shogi-z3

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

## Development

The project uses modern Python tooling:

- **uv** - Fast Python package manager
- **mypy** - Static type checking with strict mode
- **ruff** - Fast linting with comprehensive rules
- **pytest** - Testing framework
- **pre-commit** - Git hooks for code quality

### Commands

```bash
# Run linting
uv run ruff check

# Run type checking
uv run mypy src/

# Run tests
uv run pytest

# Run examples
uv run python examples.py
```

## Requirements

- Python 3.13+
- z3-solver

## License

[License information here]

## Contributing

[Contributing guidelines here]
