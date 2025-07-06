"""Checkmate solver implementation."""

from __future__ import annotations

from dataclasses import dataclass

from z3 import Not, sat

from dobutsu_shogi_z3.core import MoveData, PieceState, Player, TimeIndex
from dobutsu_shogi_z3.z3_constraints import GameRules

from .utils import create_base_solver, extract_moves


# Problem Types
@dataclass(frozen=True)
class CheckmateProblem:
    """Problem specification for finding checkmate."""

    initial_state: list[PieceState]
    winning_player: Player
    max_moves: int


# Solution Types
@dataclass(frozen=True)
class CheckmateSolution:
    """Solution for checkmate problem."""

    moves: list[MoveData]
    winning_player: Player
    mate_in: int


class CheckmateSolver:
    """Finds forced checkmate sequences."""

    def solve(self, problem: CheckmateProblem) -> CheckmateSolution | None:
        """Solve checkmate problem."""
        if problem.max_moves <= 0:
            return None

        # Check move parity - winning player must make the last move
        last_player = (problem.max_moves - 1) % 2
        if last_player != problem.winning_player.value:
            return None

        solver, state = create_base_solver(problem.max_moves, problem.initial_state)

        # Add victory condition at the end for winning player
        victory_condition = GameRules.victory_conditions(
            state,
            TimeIndex(problem.max_moves),
            problem.winning_player,
        )
        solver.add(victory_condition)

        # No victory before final move
        for _t in range(problem.max_moves):
            t = TimeIndex(_t)
            solver.add(Not(GameRules.victory_conditions(state, t, problem.winning_player)))

        if solver.check() == sat:
            model = solver.model()
            moves = extract_moves(model, state, problem.max_moves)

            return CheckmateSolution(
                moves=moves,
                winning_player=problem.winning_player,
                mate_in=problem.max_moves,
            )

        return None

    def find_shortest_mate(self, problem: CheckmateProblem) -> CheckmateSolution | None:
        """Find shortest possible mate for the winning player."""
        max_search = min(problem.max_moves, 15)  # Reasonable upper bound

        # Try odd moves for Sente, even moves for Gote
        start = 1 if problem.winning_player == Player.SENTE else 2

        for n in range(start, max_search + 1, 2):
            mate_problem = CheckmateProblem(
                initial_state=problem.initial_state,
                winning_player=problem.winning_player,
                max_moves=n,
            )

            solution = self.solve(mate_problem)
            if solution:
                return solution

        return None
