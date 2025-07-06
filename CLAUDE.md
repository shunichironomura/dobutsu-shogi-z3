# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Dōbutsu Shōgi (Animal Chess) solver that uses Z3 SMT solver to find mate-in-n solutions. The project is written in Python and uses the Z3 constraint solver to model the game rules and search for forced wins.

## References

Read the [Dōbutsu Shōgi rules](dobutsu-shogi-rules.md) for detailed game mechanics, including piece movements, captures, promotions, and win conditions.

## Key Components

- **`src/dobutsu_shogi_z3/dobutsu_shogi.py`**: Main solver implementation using Z3 SMT solver
  - `DobutsuShogiZ3` class: Complete Z3 model for the game
  - `PieceType` enum: Defines piece types (Lion, Giraffe, Elephant, Chick, Hen)
  - `Player` enum: Sente (first player) and Gote (second player)
  - Game state modeling with piece positions, ownership, captures, and promotions
  - Movement constraint generation for each piece type
  - Victory condition checking (Lion capture or reaching back rank)

## Development Commands

The project uses `uv` for Python package management:

### Dependencies

- Install dependencies: `uv sync`
- Install dev dependencies: `uv sync --group dev`

### Code Quality

- Run linting: `uv run ruff check`
- Run type checking: `uv run mypy src/`
- Run pre-commit hooks: `uv run pre-commit run --all-files`

### Testing

- Run tests: `uv run pytest` (tests are commented out in pyproject.toml)

## Architecture Notes

### Z3 Model Structure
The solver creates Z3 variables for:

- Piece positions at each time step (`piece_row`, `piece_col`)
- Piece ownership and capture states
- Movement representation with constraints
- Victory conditions

### Key Constraints

- Only one piece per square (unless captured)
- Piece movement patterns based on type
- Turn alternation between players
- Promotion rules (Chick to Hen at back rank)
- Victory conditions enforcement

### Search Strategy

- Uses SMT solving to find mate-in-n sequences
- Checks all possible moves simultaneously through constraints
- Eliminates illegal moves through Z3 assertions
- Verifies victory conditions at target depth

## Dependencies

- **z3-solver**: Core SMT solver for constraint satisfaction
- **mypy**: Type checking with strict mode enabled
- **ruff**: Linting with comprehensive rule set (ALL rules enabled)
- **pre-commit**: Code quality automation

## Notes

- The codebase uses modern Python features (requires Python 3.13+)
- Type hints are strictly enforced
- The solver can handle custom positions by modifying the initial setup
- Current implementation focuses on mate-finding rather than general game analysis
