# Dōbutsu Shōgi Z3 Examples Implementation Plan

## Overview

This document outlines the plan for re-implementing `examples.py` using the new modular API. The examples will progress from simple property verification to sophisticated tsume shogi problems.

## Design Principles

1. **Simplicity First**: Start with the most basic examples to demonstrate core concepts
2. **Progressive Complexity**: Build up from simple to complex scenarios
3. **Clear Documentation**: Each example should clearly explain what it demonstrates
4. **Practical Use Cases**: Show real-world applications of the solver

## Example Structure

### Part 1: Basic Property Verification (Simple Examples)

#### Example 1: Basic Reachability
- **Purpose**: Demonstrate the simplest use case - can a piece reach a specific square?
- **Scenario**: Check if a chick can reach the promotion zone
- **Key Concepts**: ReachabilityProblem, ReachabilitySolver
- **Code Complexity**: Minimal - direct solver usage

#### Example 2: Movement Validation
- **Purpose**: Verify that pieces move according to rules
- **Scenario**: Check if specific piece movements are possible
- **Key Concepts**: Position validation, piece movement rules
- **Code Complexity**: Simple - basic position checks

#### Example 3: Simple Victory Condition
- **Purpose**: Check if a player can achieve victory in N moves
- **Scenario**: Can Sente's lion reach Gote's back rank?
- **Key Concepts**: Victory conditions, game ending states
- **Code Complexity**: Simple - single objective

### Part 2: Intermediate Examples

#### Example 4: Basic Checkmate Finding
- **Purpose**: Find forced checkmate sequences
- **Scenario**: Standard opening position, find mate if it exists
- **Key Concepts**: CheckmateProblem, CheckmateSolver
- **Code Complexity**: Moderate - using checkmate solver

#### Example 5: Custom Position Analysis
- **Purpose**: Analyze non-standard positions
- **Scenario**: Set up a position with few pieces, find best move sequence
- **Key Concepts**: PieceState setup, custom initial positions
- **Code Complexity**: Moderate - custom setup + analysis

### Part 3: Sophisticated Examples (Tsume Shogi)

#### Example 6: Classic Tsume Problem
- **Purpose**: Solve a traditional tsume shogi puzzle
- **Scenario**: Sente must checkmate in exactly N moves, Gote plays optimally to delay
- **Key Concepts**: TsumeProblem with specific constraints
- **Code Complexity**: High - multiple constraints

#### Example 7: Tsume with Piece Restrictions
- **Purpose**: Solve tsume with additional constraints
- **Scenario**: Must checkmate using specific pieces or without capturing certain pieces
- **Key Concepts**: Custom Z3 constraints, TsumeSolver
- **Code Complexity**: High - custom constraint formulation

#### Example 8: Multi-Objective Tsume
- **Purpose**: Find solution satisfying multiple objectives
- **Scenario**: Checkmate while achieving secondary goals (e.g., promote a piece)
- **Key Concepts**: Complex constraint combinations
- **Code Complexity**: Highest - multiple interacting constraints

### Part 4: Optimization Examples

#### Example 9: Shortest Path Finding
- **Purpose**: Find optimal move sequences
- **Scenario**: Find the shortest path for a piece to reach a target
- **Key Concepts**: Optimization, path finding
- **Code Complexity**: Moderate - using shortest path methods

#### Example 10: Efficiency Comparison
- **Purpose**: Compare different solving approaches
- **Scenario**: Same problem solved with different solvers/constraints
- **Key Concepts**: Performance analysis, solver comparison
- **Code Complexity**: Moderate - multiple solver usage

## Implementation Details

### Import Structure
```python
from dobutsu_shogi_z3 import (
    # Core types
    Player, PieceType, PieceId, Position,
    # State representation
    PieceState, MoveData,
    # Problems
    CheckmateProblem, ReachabilityProblem, TsumeProblem,
    # Solvers
    CheckmateSolver, ReachabilitySolver, TsumeSolver,
    # Constants
    DEFAULT_INITIAL_SETUP,
)
from dobutsu_shogi_z3.core import RowIndex, ColIndex
```

### Helper Functions
- `print_board(pieces: List[PieceState])` - Visual board representation
- `describe_move(move: MoveData)` - Human-readable move description
- `setup_position(description: str) -> List[PieceState]` - Create positions from notation

### Error Handling
- All examples will handle None returns gracefully
- Clear messages when no solution is found
- Explanation of why solutions might not exist

## Testing Strategy

1. Each example should be runnable independently
2. Expected outputs should be documented
3. Edge cases should be demonstrated
4. Performance characteristics noted where relevant

## Documentation

Each example will include:
- Brief description of the problem
- Expected outcome
- Key learning points
- Variations to try

## Next Steps

1. Implement helper functions
2. Create simple examples (1-3)
3. Build intermediate examples (4-5)
4. Develop sophisticated tsume examples (6-8)
5. Add optimization examples (9-10)
6. Test all examples thoroughly
7. Add inline documentation