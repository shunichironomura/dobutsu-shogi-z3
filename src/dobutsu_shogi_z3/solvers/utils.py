"""Base solver protocol and utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from z3 import Solver, is_true

from dobutsu_shogi_z3.core import (
    ColIndex,
    MoveData,
    PieceId,
    PieceState,
    PieceType,
    Position,
    RowIndex,
    TimeIndex,
)
from dobutsu_shogi_z3.z3_constraints import GameRules
from dobutsu_shogi_z3.z3_models import GameState

if TYPE_CHECKING:
    from z3.z3 import ModelRef


def create_base_solver(max_moves: int, initial_state: list[PieceState]) -> tuple[Solver, GameState]:
    """Create a solver with basic constraints."""
    state = GameState(max_moves)
    solver = Solver()

    # Add basic constraints
    solver.add(state.get_basic_constraints())
    solver.add(state.set_initial_position(initial_state))
    solver.add(GameRules.basic_constraints(state))
    solver.add(GameRules.movement_constraints(state))

    return solver, state


def extract_moves(model: ModelRef, state: GameState, n_moves: int) -> list[MoveData]:
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
            from_=Position(
                row=RowIndex(model[move.from_row].as_long()),
                col=ColIndex(model[move.from_col].as_long()),
            ),
            to=Position(
                row=RowIndex(model[move.to_row].as_long()),
                col=ColIndex(model[move.to_col].as_long()),
            ),
            captures=model[move.captures].as_long(),
            piece_type=PieceType(piece_type_val),
        )
        moves.append(move_data)

    return moves
