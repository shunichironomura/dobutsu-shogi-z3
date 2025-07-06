"""Base solver protocol and utilities."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from z3 import Solver, is_true, sat

from ..game_rules import GameRules
from ..game_state import GameState
from ..types import MoveData, PieceId, PieceType, TimeIndex

if TYPE_CHECKING:
    from ..types import Problem, Solution


class BaseSolver(ABC):
    """Base class for all solvers."""

    @abstractmethod
    def solve(self, problem: "Problem") -> "Solution | None":
        """Solve the given problem."""

    def _create_base_solver(self, max_moves: int, initial_state) -> tuple[Solver, GameState]:
        """Create a solver with basic constraints."""
        state = GameState.create(max_moves)
        solver = Solver()

        # Add basic constraints
        solver.add(state.get_basic_constraints())
        solver.add(state.set_initial_position(initial_state))
        solver.add(GameRules.basic_constraints(state))
        solver.add(GameRules.movement_constraints(state))

        return solver, state

    def _extract_moves(self, model, state: GameState, n_moves: int) -> list[MoveData]:
        """Extract move sequence from Z3 model."""
        moves = []

        for _t in range(n_moves):
            t = TimeIndex(_t)
            move = state.moves[t]

            piece_id = PieceId(model[move.piece_id].as_long())
            piece_type_val = model[state.piece_type[piece_id]].as_long()

            move_data = MoveData(
                move_number=t,
                player="Sente" if t % 2 == 0 else "Gote",
                piece_id=piece_id,
                is_drop=is_true(model[move.is_drop]),
                from_=(
                    model[move.from_row].as_long(),
                    model[move.from_col].as_long(),
                ),
                to=(
                    model[move.to_row].as_long(),
                    model[move.to_col].as_long(),
                ),
                captures=model[move.captures].as_long(),
                piece_type=PieceType(piece_type_val),
            )
            moves.append(move_data)

        return moves
