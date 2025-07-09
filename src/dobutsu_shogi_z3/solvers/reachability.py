"""Reachability solver implementation."""

from __future__ import annotations

from dataclasses import dataclass

from z3 import And, Or, sat

from dobutsu_shogi_z3.core import MoveData, PieceId, PieceState, Player, Position, TimeIndex

from .utils import create_base_solver, extract_moves


@dataclass(frozen=True)
class ReachabilityProblem:
    """Problem specification for proving piece reachability."""

    initial_state: list[PieceState]
    piece_id: PieceId
    target: Position
    player: Player
    max_moves: int


@dataclass(frozen=True)
class ReachabilitySolution:
    """Solution for reachability problem."""

    moves: list[MoveData]
    piece_id: PieceId
    reached: Position


class ReachabilitySolver:
    """Proves piece can reach target position."""

    def solve(self, problem: ReachabilityProblem) -> ReachabilitySolution | None:
        """Solve reachability problem."""
        if problem.max_moves <= 0:
            return None

        solver, state = create_base_solver(problem.max_moves, problem.initial_state)

        # Add reachability constraint - piece must reach target at some point
        reachability_conditions = []

        for _t in range(problem.max_moves + 1):
            t = TimeIndex(_t)
            piece_at_target = And(
                state.piece_row[t, problem.piece_id] == problem.target.row,
                state.piece_col[t, problem.piece_id] == problem.target.col,
                state.piece_owner[t, problem.piece_id] == problem.player.value,
                state.piece_captured[t, problem.piece_id] == False,
            )
            reachability_conditions.append(piece_at_target)

        solver.add(Or(reachability_conditions))

        if solver.check() == sat:
            model = solver.model()

            # Find the earliest time when target is reached
            reached_time = None
            for _t in range(problem.max_moves + 1):
                t = TimeIndex(_t)
                if (
                    model[state.piece_row[t, problem.piece_id]].as_long() == problem.target.row
                    and model[state.piece_col[t, problem.piece_id]].as_long() == problem.target.col
                    and model[state.piece_owner[t, problem.piece_id]].as_long() == problem.player.value
                    and not model[state.piece_captured[t, problem.piece_id]]
                ):
                    reached_time = _t
                    break

            if reached_time is not None:
                moves = extract_moves(model, state, reached_time)

                return ReachabilitySolution(
                    moves=moves,
                    piece_id=problem.piece_id,
                    reached=problem.target,
                )

        return None

    def find_shortest_path(self, problem: ReachabilityProblem) -> ReachabilitySolution | None:
        """Find shortest path to target."""
        for n in range(1, problem.max_moves + 1):
            reachability_problem = ReachabilityProblem(
                initial_state=problem.initial_state,
                piece_id=problem.piece_id,
                target=problem.target,
                player=problem.player,
                max_moves=n,
            )

            solution = self.solve(reachability_problem)
            if solution:
                return solution

        return None
