"""Functional constraint generation for Dōbutsu Shōgi game rules."""

from __future__ import annotations

from itertools import product
from typing import TYPE_CHECKING

from z3 import Abs, And, BoolRef, If, Implies, Not, Or

from .types import MoveVariables, PieceId, PieceType, Player, TimeIndex

if TYPE_CHECKING:
    from collections.abc import Callable

    from z3.z3 import ArithRef

    from .game_state import GameState


class GameRules:
    """Static methods for generating game constraints."""

    @staticmethod
    def basic_constraints(state: GameState) -> list[BoolRef]:
        """Generate basic game invariants."""
        constraints = []

        # No two pieces on same square constraint
        constraints.extend(GameRules._no_overlap_constraints(state))

        # Captured pieces are in someone's hand
        constraints.extend(GameRules._capture_hand_constraints(state))

        # Only Chicks can be promoted
        constraints.extend(GameRules._promotion_constraints(state))

        return constraints

    @staticmethod
    def movement_constraints(state: GameState) -> list[BoolRef]:
        """Generate movement rules for each piece type."""
        constraints = []

        for _t in range(state.max_moves):
            t = TimeIndex(_t)
            current_player = _t % 2  # 0 for Sente, 1 for Gote

            # Moving piece must belong to current player
            constraints.extend(GameRules._player_ownership_constraints(state, t, current_player))

            # Handle regular moves vs drops
            constraints.extend(GameRules._move_type_constraints(state, t, current_player))

            # Apply move effects
            constraints.extend(GameRules._move_effects_constraints(state, t))

        return constraints

    @staticmethod
    def victory_conditions(state: GameState, t: TimeIndex, player: Player) -> BoolRef:
        """Check victory conditions at time t."""
        victory_conditions = []

        for _p in range(state.N_PIECES):
            p = PieceId(_p)

            # Victory by capturing opponent's Lion
            is_opponent_lion = And(
                state.piece_type[p] == PieceType.LION.value,
                state.piece_owner[t, p] != player.value,
            )
            victory_conditions.append(
                And(is_opponent_lion, state.piece_captured[t, p]),
            )

            # Victory by reaching opponent's back rank
            is_own_lion = And(
                state.piece_type[p] == PieceType.LION.value,
                state.piece_owner[t, p] == player.value,
            )
            reaches_back_rank = If(
                player.value == Player.SENTE.value,
                state.piece_row[t, p] == state.ROWS,
                state.piece_row[t, p] == 1,
            )
            victory_conditions.append(
                And(is_own_lion, Not(state.piece_captured[t, p]), reaches_back_rank),
            )

        return Or(victory_conditions)

    # Private helper methods
    @staticmethod
    def _no_overlap_constraints(state: GameState) -> list[BoolRef]:
        """Generate constraints ensuring no two pieces occupy same square."""
        constraints = []

        for _t in range(state.max_moves + 1):
            t = TimeIndex(_t)
            for _p1 in range(state.N_PIECES):
                p1 = PieceId(_p1)
                for _p2 in range(_p1 + 1, state.N_PIECES):
                    p2 = PieceId(_p2)
                    constraints.append(
                        Implies(
                            And(
                                Not(state.piece_captured[t, p1]),
                                Not(state.piece_captured[t, p2]),
                            ),
                            Or(
                                state.piece_row[t, p1] != state.piece_row[t, p2],
                                state.piece_col[t, p1] != state.piece_col[t, p2],
                            ),
                        ),
                    )

        return constraints

    @staticmethod
    def _capture_hand_constraints(state: GameState) -> list[BoolRef]:
        """Generate constraints for captured pieces in hand."""
        constraints = []

        for t, p in product(range(state.max_moves + 1), range(state.N_PIECES)):
            t_idx = TimeIndex(t)
            p_id = PieceId(p)
            constraints.append(
                state.piece_captured[t_idx, p_id] == (state.piece_in_hand_of[t_idx, p_id] >= 0),
            )

        return constraints

    @staticmethod
    def _promotion_constraints(state: GameState) -> list[BoolRef]:
        """Only Chicks can be promoted."""
        constraints = []

        for t, p in product(range(state.max_moves + 1), range(state.N_PIECES)):
            t_idx = TimeIndex(t)
            p_id = PieceId(p)
            constraints.append(
                Implies(
                    state.piece_promoted[t_idx, p_id],
                    state.piece_type[p_id] == PieceType.CHICK.value,
                ),
            )

        return constraints

    @staticmethod
    def _player_ownership_constraints(state: GameState, t: TimeIndex, current_player: int) -> list[BoolRef]:
        """Generate constraints for player piece ownership."""
        constraints = []
        move = state.moves[t]

        for _p in range(state.N_PIECES):
            p = PieceId(_p)
            constraints.append(
                Implies(
                    move.piece_id == p,
                    state.piece_owner[t, p] == current_player,
                ),
            )

        return constraints

    @staticmethod
    def _move_type_constraints(state: GameState, t: TimeIndex, current_player: int) -> list[BoolRef]:
        """Handle regular moves vs drops."""
        constraints = []
        move = state.moves[t]

        for _p in range(state.N_PIECES):
            p = PieceId(_p)
            constraints.append(
                Implies(
                    move.piece_id == p,
                    If(
                        move.is_drop,
                        # Drop constraints
                        And(
                            state.piece_captured[t, p],
                            state.piece_in_hand_of[t, p] == current_player,
                            move.from_row == 0,
                            move.from_col == 0,
                            move.captures == -1,
                            GameRules._square_empty_or_opponent(state, t, move.to_row, move.to_col, current_player),
                        ),
                        # Regular move constraints
                        And(
                            Not(state.piece_captured[t, p]),
                            move.from_row == state.piece_row[t, p],
                            move.from_col == state.piece_col[t, p],
                            GameRules._valid_move_pattern(state, t, move, p),
                            GameRules._square_empty_or_opponent(state, t, move.to_row, move.to_col, current_player),
                        ),
                    ),
                ),
            )

        return constraints

    @staticmethod
    def _square_empty_or_opponent(
        state: GameState,
        t: TimeIndex,
        row: ArithRef,
        col: ArithRef,
        current_player: int,
    ) -> BoolRef:
        """Check if square is empty or contains opponent's piece."""
        square_conditions = []

        for _p in range(state.N_PIECES):
            p = PieceId(_p)
            occupied_by_p = And(
                Not(state.piece_captured[t, p]),
                state.piece_row[t, p] == row,
                state.piece_col[t, p] == col,
            )
            square_conditions.append(
                Implies(occupied_by_p, state.piece_owner[t, p] != current_player),
            )

        return And(square_conditions)

    @staticmethod
    def _valid_move_pattern(state: GameState, t: TimeIndex, move: MoveVariables, piece_id: PieceId) -> BoolRef:
        """Check if move follows piece movement rules."""
        from_row = move.from_row
        from_col = move.from_col
        to_row = move.to_row
        to_col = move.to_col

        # Calculate movement delta
        d_row = to_row - from_row
        d_col = to_col - from_col

        # Get effective piece type (considering promotion)
        effective_type = If(
            state.piece_promoted[t, piece_id],
            PieceType.HEN.value,
            state.piece_type[piece_id],
        )

        # Define movement patterns
        patterns = [
            # Lion - moves 1 square in any direction
            Implies(
                effective_type == PieceType.LION.value,
                And(
                    Abs(d_row) <= 1,
                    Abs(d_col) <= 1,
                    Or(d_row != 0, d_col != 0),
                ),
            ),
            # Giraffe - moves 1 square orthogonally
            Implies(
                effective_type == PieceType.GIRAFFE.value,
                Or(
                    And(d_row == 0, Or(d_col == 1, d_col == -1)),
                    And(d_col == 0, Or(d_row == 1, d_row == -1)),
                ),
            ),
            # Elephant - moves 1 square diagonally
            Implies(
                effective_type == PieceType.ELEPHANT.value,
                And(Abs(d_row) == 1, Abs(d_col) == 1),
            ),
            # Chick - moves 1 square forward
            Implies(
                effective_type == PieceType.CHICK.value,
                And(
                    If(
                        state.piece_owner[t, piece_id] == Player.SENTE.value,
                        d_row == 1,
                        d_row == -1,
                    ),
                    d_col == 0,
                ),
            ),
            # Hen - moves like Gold
            Implies(
                effective_type == PieceType.HEN.value,
                Or(
                    # Orthogonal moves
                    And(d_row == 0, Or(d_col == 1, d_col == -1)),
                    And(d_col == 0, Or(d_row == 1, d_row == -1)),
                    # Forward diagonal moves
                    And(
                        If(
                            state.piece_owner[t, piece_id] == Player.SENTE.value,
                            d_row == 1,
                            d_row == -1,
                        ),
                        Or(d_col == 1, d_col == -1),
                    ),
                ),
            ),
        ]

        return And(patterns)

    @staticmethod
    def _move_effects_constraints(state: GameState, t: TimeIndex) -> list[BoolRef]:
        """Apply effects of a move to get next board state."""
        constraints = []
        move = state.moves[t]
        next_t = TimeIndex(t + 1)
        current_player = t % 2

        for _p in range(state.N_PIECES):
            p = PieceId(_p)

            # Check if this piece is moving
            is_moving = move.piece_id == p

            # Check if this piece is captured
            is_captured = And(move.captures == p, Not(move.is_drop))

            # Default states
            same_position = And(
                state.piece_row[next_t, p] == state.piece_row[t, p],
                state.piece_col[next_t, p] == state.piece_col[t, p],
            )
            same_captured = state.piece_captured[next_t, p] == state.piece_captured[t, p]
            same_promoted = state.piece_promoted[next_t, p] == state.piece_promoted[t, p]
            same_hand = state.piece_in_hand_of[next_t, p] == state.piece_in_hand_of[t, p]
            same_owner = state.piece_owner[next_t, p] == state.piece_owner[t, p]

            # Apply effects based on piece role
            constraints.append(
                If(
                    is_moving,
                    # This piece is moving
                    And(
                        state.piece_row[next_t, p] == move.to_row,
                        state.piece_col[next_t, p] == move.to_col,
                        state.piece_captured[next_t, p] == False,
                        state.piece_in_hand_of[next_t, p] == -1,
                        same_owner,
                        # Check promotion
                        If(
                            And(
                                state.piece_type[p] == PieceType.CHICK.value,
                                Or(
                                    And(state.piece_owner[t, p] == Player.SENTE.value, move.to_row == state.ROWS),
                                    And(state.piece_owner[t, p] == Player.GOTE.value, move.to_row == 1),
                                ),
                            ),
                            state.piece_promoted[next_t, p] == True,
                            same_promoted,
                        ),
                    ),
                    If(
                        is_captured,
                        # This piece is captured
                        And(
                            state.piece_captured[next_t, p] == True,
                            state.piece_in_hand_of[next_t, p] == current_player,
                            state.piece_promoted[next_t, p] == False,
                            state.piece_owner[next_t, p] == current_player,
                            same_position,
                        ),
                        # This piece is unaffected
                        And(same_position, same_captured, same_promoted, same_hand, same_owner),
                    ),
                ),
            )

        # Capture logic
        constraints.extend(GameRules._capture_logic_constraints(state, t))

        return constraints

    @staticmethod
    def _capture_logic_constraints(state: GameState, t: TimeIndex) -> list[BoolRef]:
        """Handle capture logic."""
        constraints = []
        move = state.moves[t]
        current_player = t % 2

        # Determine what piece is captured
        for _p in range(state.N_PIECES):
            p = PieceId(_p)
            constraints.append(
                Implies(
                    And(
                        Not(state.piece_captured[t, p]),
                        p != move.piece_id,
                        state.piece_row[t, p] == move.to_row,
                        state.piece_col[t, p] == move.to_col,
                        state.piece_owner[t, p] != current_player,
                    ),
                    move.captures == p,
                ),
            )

        # If no valid capture, set captures to -1
        no_valid_capture = And(
            [
                Or(
                    state.piece_captured[t, PieceId(p)],
                    p == move.piece_id,
                    state.piece_row[t, PieceId(p)] != move.to_row,
                    state.piece_col[t, PieceId(p)] != move.to_col,
                    state.piece_owner[t, PieceId(p)] == current_player,
                )
                for p in range(state.N_PIECES)
            ],
        )
        constraints.append(Implies(no_valid_capture, move.captures == -1))

        return constraints


# Constraint combinators for functional programming
def for_all_pieces(constraint_fn: Callable) -> Callable:
    """Apply constraint to all pieces."""
    return lambda state, t: And([constraint_fn(state, t, PieceId(p)) for p in range(state.N_PIECES)])


def for_all_times(constraint_fn: Callable) -> Callable:
    """Apply constraint to all time steps."""
    return lambda state: And([constraint_fn(state, TimeIndex(t)) for t in range(state.max_moves)])


def implies_for_piece(piece_id: int, constraint_fn: Callable) -> Callable:
    """Apply constraint only when piece_id matches."""
    return lambda state, t, p: Implies(
        p == piece_id,
        constraint_fn(state, t, p),
    )
