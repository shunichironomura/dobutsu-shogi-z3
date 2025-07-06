"""Lightweight GameState class for Z3 variable management."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from z3 import Bool, Int

from .types import MoveVariables, PieceId, PieceState, PieceType, TimeIndex

if TYPE_CHECKING:
    from z3.z3 import ArithRef, BoolRef


@dataclass
class GameState:
    """Pure Z3 variable container for game state."""

    max_moves: int

    # Constants
    ROWS: int = field(default=4, init=False)
    COLS: int = field(default=3, init=False)
    N_PIECES: int = field(default=8, init=False)

    # Static piece properties
    piece_type: dict[PieceId, ArithRef] = field(default_factory=dict, init=False)

    # Dynamic state variables
    piece_owner: dict[tuple[TimeIndex, PieceId], ArithRef] = field(default_factory=dict, init=False)
    piece_row: dict[tuple[TimeIndex, PieceId], ArithRef] = field(default_factory=dict, init=False)
    piece_col: dict[tuple[TimeIndex, PieceId], ArithRef] = field(default_factory=dict, init=False)
    piece_captured: dict[tuple[TimeIndex, PieceId], BoolRef] = field(default_factory=dict, init=False)
    piece_promoted: dict[tuple[TimeIndex, PieceId], BoolRef] = field(default_factory=dict, init=False)
    piece_in_hand_of: dict[tuple[TimeIndex, PieceId], ArithRef] = field(default_factory=dict, init=False)

    # Move variables
    moves: dict[TimeIndex, MoveVariables] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        """Initialize all Z3 variables."""
        self._create_variables()

    @classmethod
    def create(cls, max_moves: int) -> GameState:
        """Create and initialize all Z3 variables."""
        return cls(max_moves=max_moves)

    def _create_variables(self) -> None:
        """Create all Z3 variables with proper constraints."""
        # Static piece properties
        for _p in range(self.N_PIECES):
            p = PieceId(_p)
            self.piece_type[p] = Int(f"piece_{p}_type")

        # Dynamic state variables
        for _t in range(self.max_moves + 1):
            t = TimeIndex(_t)
            for _p in range(self.N_PIECES):
                p = PieceId(_p)
                self.piece_owner[t, p] = Int(f"piece_{p}_owner_t{t}")
                self.piece_row[t, p] = Int(f"piece_{p}_row_t{t}")
                self.piece_col[t, p] = Int(f"piece_{p}_col_t{t}")
                self.piece_captured[t, p] = Bool(f"piece_{p}_captured_t{t}")
                self.piece_promoted[t, p] = Bool(f"piece_{p}_promoted_t{t}")
                self.piece_in_hand_of[t, p] = Int(f"piece_{p}_in_hand_t{t}")

        # Move variables
        for _t in range(self.max_moves):
            t = TimeIndex(_t)
            self.moves[t] = MoveVariables(
                piece_id=Int(f"move_{t}_piece"),
                from_row=Int(f"move_{t}_from_row"),
                from_col=Int(f"move_{t}_from_col"),
                to_row=Int(f"move_{t}_to_row"),
                to_col=Int(f"move_{t}_to_col"),
                is_drop=Bool(f"move_{t}_is_drop"),
                captures=Int(f"move_{t}_captures"),
            )

    def get_basic_constraints(self) -> list[BoolRef]:
        """Get basic domain constraints for all variables."""
        constraints = []

        # Piece type constraints
        for p in range(self.N_PIECES):
            piece_id = PieceId(p)
            constraints.extend([
                self.piece_type[piece_id] >= PieceType.min_value(),
                self.piece_type[piece_id] <= PieceType.max_value(),
            ])

        # Position and state constraints
        for _t in range(self.max_moves + 1):
            t = TimeIndex(_t)
            for _p in range(self.N_PIECES):
                p = PieceId(_p)
                constraints.extend([
                    # Owner constraints
                    self.piece_owner[t, p] >= 0,
                    self.piece_owner[t, p] <= 1,

                    # Position constraints
                    self.piece_row[t, p] >= 1,
                    self.piece_row[t, p] <= self.ROWS,
                    self.piece_col[t, p] >= 1,
                    self.piece_col[t, p] <= self.COLS,

                    # Hand constraints
                    self.piece_in_hand_of[t, p] >= -1,
                    self.piece_in_hand_of[t, p] <= 1,
                ])

        # Move constraints
        for _t in range(self.max_moves):
            t = TimeIndex(_t)
            move = self.moves[t]
            constraints.extend([
                # Piece ID constraints
                move.piece_id >= 0,
                move.piece_id < self.N_PIECES,

                # Position constraints
                move.from_row >= 0,
                move.from_row <= self.ROWS,
                move.from_col >= 0,
                move.from_col <= self.COLS,
                move.to_row >= 1,
                move.to_row <= self.ROWS,
                move.to_col >= 1,
                move.to_col <= self.COLS,

                # Capture constraints
                move.captures >= -1,
                move.captures < self.N_PIECES,
            ])

        return constraints

    def set_initial_position(self, initial_state: list[PieceState]) -> list[BoolRef]:
        """Set initial board position constraints."""
        constraints = []

        for piece_state in initial_state:
            piece_id = piece_state.piece_id

            # Static properties
            constraints.append(
                self.piece_type[piece_id] == piece_state.piece_type.value,
            )

            # Initial state at t=0
            t = TimeIndex(0)
            constraints.extend([
                self.piece_owner[t, piece_id] == piece_state.piece_owner,
                self.piece_row[t, piece_id] == piece_state.row,
                self.piece_col[t, piece_id] == piece_state.col,
                self.piece_captured[t, piece_id] == False,
                self.piece_promoted[t, piece_id] == False,
                self.piece_in_hand_of[t, piece_id] == -1,  # On board
            ])

        return constraints
