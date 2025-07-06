# Dōbutsu Shōgi Solver Refactoring Plan

## Overview

This document outlines the comprehensive refactoring plan for the Dōbutsu Shōgi solver to transform it from a monolithic design into a modular, extensible system that supports multiple use cases while leveraging algebraic typing and minimizing code complexity.

## Current State Analysis

### Issues with Current Implementation

1. **Monolithic Design**: All functionality packed into single 850-line `DobutsuShogiZ3` class
2. **Tight Coupling**: Z3 model creation, constraints, and solving logic are intertwined
3. **Limited Extensibility**: Adding new problem types requires modifying core code
4. **Verbose Constraints**: Repetitive loops and manual constraint building
5. **Single Purpose**: Only designed for mate-in-n problems
6. **Code Duplication**: Similar patterns repeated throughout

## Proposed Architecture

### Core Design Principles

- **Separation of Concerns**: Distinct modules for state, rules, and solving
- **Algebraic Data Types**: Strong typing for problems and solutions
- **Functional Programming**: Constraint combinators and immutable data
- **Protocol-Based Extension**: Easy addition of new solver types
- **Zero Runtime Overhead**: Type safety without performance cost

### Module Structure

```
src/dobutsu_shogi_z3/
├── types.py          # Core algebraic types and protocols
├── game_state.py     # Z3 variable management
├── game_rules.py     # Constraint generation logic
├── solvers/
│   ├── base.py       # Solver protocol
│   ├── checkmate.py  # Checkmate solver
│   ├── reachability.py # Reachability solver
│   └── tsume.py      # General Tsume solver
└── dobutsu_shogi.py  # Public API
```

## Detailed Design

### 1. Algebraic Type System

```python
from typing import Protocol, Union, NewType
from dataclasses import dataclass

# Position type
Position = tuple[RowIndex, ColIndex]

# Problem specifications
@dataclass(frozen=True)
class CheckmateProblem:
    initial_state: list[PieceState]
    winning_player: Player
    max_moves: int

@dataclass(frozen=True)
class ReachabilityProblem:
    initial_state: list[PieceState]
    piece_id: PieceId
    target: Position
    player: Player
    max_moves: int

@dataclass(frozen=True)
class TsumeProblem:
    initial_state: list[PieceState]
    constraints: list[Constraint]
    objective: Objective
    max_moves: int

# Union type for all problems
Problem = Union[CheckmateProblem, ReachabilityProblem, TsumeProblem]

# Solution types
@dataclass(frozen=True)
class CheckmateSolution:
    moves: list[MoveData]
    winning_player: Player
    mate_in: int

@dataclass(frozen=True)
class ReachabilitySolution:
    moves: list[MoveData]
    piece_id: PieceId
    reached: Position

@dataclass(frozen=True)
class TsumeSolution:
    moves: list[MoveData]
    satisfied_constraints: list[Constraint]

# Union type for all solutions
Solution = Union[CheckmateSolution, ReachabilitySolution, TsumeSolution]
```

### 2. GameState Class

Lightweight container for Z3 variables:

```python
@dataclass
class GameState:
    """Pure Z3 variable container for game state."""
    max_moves: int

    # Static piece properties
    piece_type: dict[PieceId, ArithRef]

    # Dynamic state variables
    piece_owner: dict[tuple[TimeIndex, PieceId], ArithRef]
    piece_row: dict[tuple[TimeIndex, PieceId], ArithRef]
    piece_col: dict[tuple[TimeIndex, PieceId], ArithRef]
    piece_captured: dict[tuple[TimeIndex, PieceId], BoolRef]
    piece_promoted: dict[tuple[TimeIndex, PieceId], BoolRef]
    piece_in_hand_of: dict[tuple[TimeIndex, PieceId], ArithRef]

    # Move variables
    moves: dict[TimeIndex, MoveVariables]

    @classmethod
    def create(cls, max_moves: int) -> 'GameState':
        """Factory method to create and initialize all Z3 variables."""
        # Variable creation logic here
```

### 3. GameRules Module

Functional constraint generation:

```python
class GameRules:
    """Static methods for generating game constraints."""

    @staticmethod
    def basic_constraints(state: GameState) -> list[BoolRef]:
        """Generate basic game invariants."""
        return [
            constraint
            for t, p in product(range(state.max_moves), range(N_PIECES))
            for constraint in [
                # No two pieces on same square
                no_overlap_constraint(state, t, p),
                # Captured pieces in hand
                capture_hand_constraint(state, t, p),
                # Only chicks can promote
                promotion_constraint(state, t, p),
            ]
        ]

    @staticmethod
    def movement_constraints(state: GameState) -> list[BoolRef]:
        """Generate movement rules for each piece type."""
        return [
            movement_constraint(state, t, move)
            for t, move in state.moves.items()
        ]

    @staticmethod
    def victory_conditions(state: GameState, t: TimeIndex, player: Player) -> BoolRef:
        """Check victory conditions at time t."""
        return Or([
            lion_captured(state, t, player),
            lion_reached_back_rank(state, t, player)
        ])
```

### 4. Solver Protocol and Implementations

```python
class Solver(Protocol):
    """Protocol for all solver types."""
    def solve(self, problem: Problem) -> Solution | None:
        """Solve the given problem."""
        ...

class CheckmateSolver:
    """Finds forced checkmate sequences."""

    def solve(self, problem: CheckmateProblem) -> CheckmateSolution | None:
        state = GameState.create(problem.max_moves)
        solver = Solver()

        # Add initial position
        solver.add(initial_position_constraints(state, problem.initial_state))

        # Add game rules
        solver.add(GameRules.basic_constraints(state))
        solver.add(GameRules.movement_constraints(state))

        # Add checkmate constraints
        solver.add(checkmate_constraints(state, problem))

        if solver.check() == sat:
            return extract_checkmate_solution(solver.model(), state, problem)
        return None

class ReachabilitySolver:
    """Proves piece can reach target position."""

    def solve(self, problem: ReachabilityProblem) -> ReachabilitySolution | None:
        # Similar structure with reachability-specific constraints
        pass

class TsumeSolver:
    """General constraint-based problem solver."""

    def solve(self, problem: TsumeProblem) -> TsumeSolution | None:
        # Flexible constraint solving
        pass
```

### 5. Constraint Combinators

Functional helpers to reduce code duplication:

```python
# Higher-order constraint functions
def for_all_pieces(constraint_fn: Callable) -> Callable:
    """Apply constraint to all pieces."""
    return lambda state, t: And([
        constraint_fn(state, t, p)
        for p in range(N_PIECES)
    ])

def for_all_times(constraint_fn: Callable) -> Callable:
    """Apply constraint to all time steps."""
    return lambda state: And([
        constraint_fn(state, t)
        for t in range(state.max_moves)
    ])

def implies_for_piece(piece_id: ArithRef, constraint_fn: Callable) -> Callable:
    """Apply constraint only when piece_id matches."""
    return lambda state, t, p: Implies(
        piece_id == p,
        constraint_fn(state, t, p)
    )

# Usage example
no_overlap = for_all_pieces(
    lambda state, t, p1: for_all_pieces(
        lambda state, t, p2: Implies(
            And(p1 < p2, Not(captured(state, t, p1)), Not(captured(state, t, p2))),
            different_positions(state, t, p1, p2)
        )
    )(state, t)
)
```

### 6. Public API

Simple, intuitive interface:

```python
# dobutsu_shogi.py
from .solvers import CheckmateSolver, ReachabilitySolver, TsumeSolver
from .types import CheckmateProblem, ReachabilityProblem, TsumeProblem

__all__ = [
    # Solvers
    'CheckmateSolver',
    'ReachabilitySolver',
    'TsumeSolver',

    # Problem types
    'CheckmateProblem',
    'ReachabilityProblem',
    'TsumeProblem',

    # Core types
    'Player',
    'PieceType',
    'PieceState',
    'DEFAULT_INITIAL_SETUP',
]

# Convenience functions
def find_checkmate(initial_state: list[PieceState], player: Player, max_moves: int) -> CheckmateSolution | None:
    """Find checkmate for given player within max_moves."""
    problem = CheckmateProblem(initial_state, player, max_moves)
    solver = CheckmateSolver()
    return solver.solve(problem)

def can_reach(initial_state: list[PieceState], piece_id: PieceId, target: Position, max_moves: int) -> ReachabilitySolution | None:
    """Check if piece can reach target position."""
    # Determine player from piece ownership
    player = next(p.piece_owner for p in initial_state if p.piece_id == piece_id)
    problem = ReachabilityProblem(initial_state, piece_id, target, player, max_moves)
    solver = ReachabilitySolver()
    return solver.solve(problem)
```

## Implementation Strategy

### Phase 1: Core Types and GameState (2 hours)

- [ ] Create `types.py` with all algebraic types
- [ ] Implement `GameState` class with Z3 variable creation
- [ ] Add type aliases and NewType definitions

### Phase 2: Game Rules Extraction (2 hours)

- [ ] Create `game_rules.py` with static constraint methods
- [ ] Implement constraint combinators
- [ ] Convert existing constraints to functional style

### Phase 3: Solver Implementation (3 hours)

- [ ] Create solver protocol in `base.py`
- [ ] Implement `CheckmateSolver`
- [ ] Implement `ReachabilitySolver`
- [ ] Implement `TsumeSolver`

### Phase 4: Integration and Testing (2 hours)

- [ ] Create public API in `dobutsu_shogi.py`
- [ ] Migrate existing tests
- [ ] Add new tests for each solver type
- [ ] Write usage examples

### Phase 5: Optimization (1 hour)

- [ ] Profile and optimize constraint generation
- [ ] Remove redundant code
- [ ] Add caching where beneficial

## Expected Outcomes

### Code Metrics

- **Line Count**: ~500 lines (40% reduction)
- **Module Count**: 7 focused modules (vs 1 monolithic)
- **Type Safety**: 100% type coverage
- **Test Coverage**: >95%

### Functionality

- ✅ Checkmate detection
- ✅ Reachability analysis
- ✅ Custom Tsume problems
- ✅ Easy extension for new problem types

### Code Quality

- **Separation of Concerns**: Clear module boundaries
- **DRY Principle**: No repeated constraint logic
- **Type Safety**: Compile-time error detection
- **Testability**: Each module independently testable

## Usage Examples

### Example 1: Find Checkmate

```python
from dobutsu_shogi_z3 import CheckmateSolver, CheckmateProblem, Player, DEFAULT_INITIAL_SETUP

solver = CheckmateSolver()
problem = CheckmateProblem(
    initial_state=DEFAULT_INITIAL_SETUP,
    winning_player=Player.SENTE,
    max_moves=7
)

solution = solver.solve(problem)
if solution:
    print(f"Found mate in {solution.mate_in} moves!")
    for move in solution.moves:
        print(f"{move.player}: {move.piece_type} {move.from_} -> {move.to}")
```

### Example 2: Prove Reachability

```python
from dobutsu_shogi_z3 import ReachabilitySolver, ReachabilityProblem

solver = ReachabilitySolver()
problem = ReachabilityProblem(
    initial_state=DEFAULT_INITIAL_SETUP,
    piece_id=PieceId(3),  # Sente's chick
    target=(4, 2),        # Can it reach the back rank?
    player=Player.SENTE,
    max_moves=5
)

solution = solver.solve(problem)
if solution:
    print(f"Piece can reach {solution.reached} in {len(solution.moves)} moves")
```

### Example 3: Custom Tsume Problem

```python
from dobutsu_shogi_z3 import TsumeSolver, TsumeProblem, Constraint

# Define custom constraints
constraints = [
    # Sente must capture Gote's giraffe
    CaptureConstraint(piece_type=PieceType.GIRAFFE, by_player=Player.SENTE),
    # Sente's lion must survive
    SurvivalConstraint(piece_type=PieceType.LION, player=Player.SENTE),
]

solver = TsumeSolver()
problem = TsumeProblem(
    initial_state=custom_position,
    constraints=constraints,
    objective=Objective.SATISFY_ALL,
    max_moves=10
)

solution = solver.solve(problem)
```

## Conclusion

This refactoring transforms the Dōbutsu Shōgi solver from a monolithic, single-purpose implementation into a modular, extensible system that supports multiple use cases. By leveraging algebraic typing, functional programming, and clear separation of concerns, we achieve:

1. **40% code reduction** through better abstractions
2. **Multiple use cases** with specialized solvers
3. **Type safety** catching errors at compile time
4. **Easy extensibility** for new problem types
5. **Clear, intuitive API** for end users

The new architecture maintains all existing functionality while providing a foundation for future enhancements and problem types.
