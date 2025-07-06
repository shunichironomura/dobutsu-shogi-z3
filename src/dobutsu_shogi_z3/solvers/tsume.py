"""General Tsume solver implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from z3 import And, sat

from .utils import create_base_solver, extract_moves

if TYPE_CHECKING:
    from z3.z3 import BoolRef

    from dobutsu_shogi_z3.core import MoveData, PieceState


@dataclass(frozen=True)
class TsumeProblem:
    """Problem specification for general Tsume solving."""

    initial_state: list[PieceState]
    constraints: list[BoolRef]
    max_moves: int


@dataclass(frozen=True)
class TsumeSolution:
    """Solution for general Tsume problem."""

    moves: list[MoveData]
    satisfied_constraints: list[BoolRef]


class TsumeSolver:
    """General constraint-based problem solver."""

    def solve(self, problem: TsumeProblem) -> TsumeSolution | None:
        """Solve general Tsume problem."""
        if problem.max_moves <= 0:
            return None

        solver, state = create_base_solver(problem.max_moves, problem.initial_state)

        # Add custom constraints
        if problem.constraints:
            solver.add(And(problem.constraints))

        if solver.check() == sat:
            model = solver.model()
            moves = extract_moves(model, state, problem.max_moves)

            return TsumeSolution(
                moves=moves,
                satisfied_constraints=problem.constraints,
            )

        return None

    def solve_with_objective(self, problem: TsumeProblem, objective_constraint: BoolRef) -> TsumeSolution | None:
        """Solve with additional objective constraint."""
        if problem.max_moves <= 0:
            return None

        solver, state = create_base_solver(problem.max_moves, problem.initial_state)

        # Add custom constraints
        if problem.constraints:
            solver.add(And(problem.constraints))

        # Add objective constraint
        solver.add(objective_constraint)

        if solver.check() == sat:
            model = solver.model()
            moves = extract_moves(model, state, problem.max_moves)

            return TsumeSolution(
                moves=moves,
                satisfied_constraints=[*problem.constraints, objective_constraint],
            )

        return None
