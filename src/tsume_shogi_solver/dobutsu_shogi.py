"""Dōbutsu Shōgi (Animal Chess) - Complete Z3 Model."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Literal, NewType, TypedDict

from z3 import Abs, And, Bool, BoolRef, If, Implies, Int, Not, Or, Solver, is_true, sat

if TYPE_CHECKING:
    from z3.z3 import ArithRef

PieceId = NewType("PieceId", int)
PieceTypeId = NewType("PieceTypeId", int)
PlayerId = NewType("PlayerId", int)
TimeIndex = NewType("TimeIndex", int)
ColIndex = NewType("ColIndex", int)
RowIndex = NewType("RowIndex", int)


class PieceType(Enum):
    """Piece types in Dōbutsu Shōgi."""

    LION = PieceTypeId(0)  # Lion (王) - moves 1 square in any direction
    GIRAFFE = PieceTypeId(1)  # Giraffe (飛) - moves 1 square orthogonally
    ELEPHANT = PieceTypeId(2)  # Elephant (角) - moves 1 square diagonally
    CHICK = PieceTypeId(3)  # Chick (歩) - moves 1 square forward
    HEN = PieceTypeId(4)  # Hen (と金) - promoted chick, moves like gold

    @classmethod
    def min_value(cls) -> PieceTypeId:
        """Get the minimum value of the enum."""
        return min(member.value for member in cls)

    @classmethod
    def max_value(cls) -> PieceTypeId:
        """Get the maximum value of the enum."""
        return max(member.value for member in cls)


class Player(Enum):
    """Players - using Shogi terminology."""

    SENTE = PlayerId(0)  # First player (starts at bottom)
    GOTE = PlayerId(1)  # Second player (starts at top)


class Move(TypedDict):
    """Representation of a move in Dōbutsu Shōgi."""

    piece_id: ArithRef  # Piece being moved (0-7)
    from_row: ArithRef  # Starting row (0 for drop)
    from_col: ArithRef  # Starting column (0 for drop)
    to_row: ArithRef  # Target row (1-4)
    to_col: ArithRef  # Target column (1-3)
    is_drop: BoolRef  # True if this is a drop move
    captures: ArithRef  # -1 if no capture, else piece id being captured


@dataclass(frozen=True, slots=True)
class MoveData:
    """Data structure for a move in Dōbutsu Shōgi."""

    move_number: TimeIndex  # Move number (0-indexed)
    player: Literal["Sente", "Gote"]
    piece_id: PieceId  # Piece ID (0-7)
    is_drop: bool  # True if this is a drop move
    from_: tuple[RowIndex, ColIndex]  # (row, col) of the piece before the move
    to: tuple[RowIndex, ColIndex]  # (row, col) of the piece after the move
    captures: int  # -1 if no capture, else piece id being captured
    piece_type: PieceType


@dataclass
class MoveVariables:
    """Variables for a move in Dōbutsu Shōgi."""

    piece_id: ArithRef  # Piece being moved (0-7)
    from_row: ArithRef  # Starting row (0 for drop)
    from_col: ArithRef  # Starting column (0 for drop)
    to_row: ArithRef  # Target row (1-4)
    to_col: ArithRef  # Target column (1-3)
    is_drop: BoolRef  # True if this is a drop move
    captures: ArithRef  # -1 if no capture, else piece id being captured


@dataclass(frozen=True, slots=True)
class PieceState:
    """State of a piece in Dōbutsu Shōgi."""

    piece_id: PieceId
    piece_type: PieceType
    piece_owner: PlayerId
    row: RowIndex
    col: ColIndex


# Default initial board setup for Dōbutsu Shōgi
DEFAULT_INITIAL_SETUP: list[PieceState] = [
    # Sente (bottom player) - Row 1
    PieceState(
        piece_id=PieceId(0),
        piece_type=PieceType.ELEPHANT,
        piece_owner=Player.SENTE.value,
        row=RowIndex(1),
        col=ColIndex(1),
    ),
    PieceState(
        piece_id=PieceId(1),
        piece_type=PieceType.LION,
        piece_owner=Player.SENTE.value,
        row=RowIndex(1),
        col=ColIndex(2),
    ),
    PieceState(
        piece_id=PieceId(2),
        piece_type=PieceType.GIRAFFE,
        piece_owner=Player.SENTE.value,
        row=RowIndex(1),
        col=ColIndex(3),
    ),
    PieceState(
        piece_id=PieceId(3),
        piece_type=PieceType.CHICK,
        piece_owner=Player.SENTE.value,
        row=RowIndex(2),
        col=ColIndex(2),
    ),
    # Gote (top player) - Row 4
    PieceState(
        piece_id=PieceId(4),
        piece_type=PieceType.GIRAFFE,
        piece_owner=Player.GOTE.value,
        row=RowIndex(4),
        col=ColIndex(1),
    ),
    PieceState(
        piece_id=PieceId(5),
        piece_type=PieceType.LION,
        piece_owner=Player.GOTE.value,
        row=RowIndex(4),
        col=ColIndex(2),
    ),
    PieceState(
        piece_id=PieceId(6),
        piece_type=PieceType.ELEPHANT,
        piece_owner=Player.GOTE.value,
        row=RowIndex(4),
        col=ColIndex(3),
    ),
    PieceState(
        piece_id=PieceId(7),
        piece_type=PieceType.CHICK,
        piece_owner=Player.GOTE.value,
        row=RowIndex(3),
        col=ColIndex(2),
    ),
]


@dataclass
class DobutsuShogiZ3:
    """Complete Z3 model for Dōbutsu Shōgi."""

    # Constants
    ROWS: ClassVar[int] = 4  # Number of rows on the board
    COLS: ClassVar[int] = 3  # Number of columns on the board
    N_PIECES: ClassVar[int] = 8  # Total number of pieces (4 per player)

    # Solver configuration
    solver: Solver = field(default_factory=Solver, init=False)
    max_moves: int = 20  # Maximum number of half-moves to search
    initial_setup: list[PieceState] = field(default_factory=lambda: DEFAULT_INITIAL_SETUP.copy())

    # Variables
    piece_type: dict[PieceId, ArithRef] = field(default_factory=dict, init=False)
    piece_owner: dict[tuple[TimeIndex, PieceId], ArithRef] = field(default_factory=dict, init=False)
    piece_row: dict[tuple[TimeIndex, PieceId], ArithRef] = field(
        default_factory=dict,
        init=False,
    )  # Row of piece at time t (1-indexed). 0 means piece is in hand.
    piece_col: dict[tuple[TimeIndex, PieceId], ArithRef] = field(
        default_factory=dict,
        init=False,
    )  # Column of piece at time t (1-indexed). 0 means piece is in hand.
    piece_captured: dict[tuple[TimeIndex, PieceId], BoolRef] = field(default_factory=dict, init=False)
    piece_promoted: dict[tuple[TimeIndex, PieceId], BoolRef] = field(default_factory=dict, init=False)
    piece_in_hand_of: dict[tuple[TimeIndex, PieceId], ArithRef] = field(
        default_factory=dict,
        init=False,
    )  # Which player holds this piece (-1 if on board)
    moves: dict[TimeIndex, MoveVariables] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        """Initialize the model."""
        # Create variables
        self._create_variables()

        # Add game rules
        self._add_initial_position()
        self._add_basic_constraints()
        self._add_movement_constraints()

    def _create_variables(self) -> None:
        """Create all Z3 variables."""
        # Static piece properties (never change)
        for _p in range(self.N_PIECES):
            p = PieceId(_p)
            self.piece_type[p] = Int(f"piece_{p}_type")

            # Constraints
            self.solver.add(self.piece_type[p] >= PieceType.min_value())
            self.solver.add(self.piece_type[p] <= PieceType.max_value())

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

                # Constraints
                self.solver.add(Or(self.piece_owner[t, p] == 0, self.piece_owner[t, p] == 1))
                self.solver.add(self.piece_row[t, p] >= 1)
                self.solver.add(self.piece_row[t, p] <= self.ROWS)
                self.solver.add(self.piece_col[t, p] >= 1)
                self.solver.add(self.piece_col[t, p] <= self.COLS)
                self.solver.add(self.piece_in_hand_of[t, p] >= -1)
                self.solver.add(self.piece_in_hand_of[t, p] <= 1)

        # Move representation
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

            # Constraints on moves
            self.solver.add(self.moves[t].piece_id >= 0)
            self.solver.add(self.moves[t].piece_id < self.N_PIECES)
            self.solver.add(self.moves[t].from_row >= 0)  # 0 means drop
            self.solver.add(self.moves[t].from_row <= self.ROWS)
            self.solver.add(self.moves[t].from_col >= 0)
            self.solver.add(self.moves[t].from_col <= self.COLS)
            self.solver.add(self.moves[t].to_row >= 1)
            self.solver.add(self.moves[t].to_row <= self.ROWS)
            self.solver.add(self.moves[t].to_col >= 1)
            self.solver.add(self.moves[t].to_col <= self.COLS)
            self.solver.add(self.moves[t].captures >= -1)
            self.solver.add(self.moves[t].captures < self.N_PIECES)

    def _add_initial_position(self) -> None:
        """Set up the initial board position."""
        for piece_state in self.initial_setup:
            piece_id = piece_state.piece_id

            # Static properties
            self.solver.add(self.piece_type[piece_id] == piece_state.piece_type.value)

            # Initial state
            initial_time_index = TimeIndex(0)
            self.solver.add(self.piece_owner[initial_time_index, piece_id] == piece_state.piece_owner)
            self.solver.add(self.piece_row[initial_time_index, piece_id] == piece_state.row)
            self.solver.add(self.piece_col[initial_time_index, piece_id] == piece_state.col)
            self.solver.add(Not(self.piece_captured[initial_time_index, piece_id]))
            self.solver.add(Not(self.piece_promoted[initial_time_index, piece_id]))
            self.solver.add(self.piece_in_hand_of[initial_time_index, piece_id] == -1)  # On board

    def _add_basic_constraints(self) -> None:
        """Add basic game constraints."""
        for _t in range(self.max_moves + 1):
            t = TimeIndex(_t)
            # No two pieces on same square (unless one is captured)
            for _p1 in range(self.N_PIECES):
                p1 = PieceId(_p1)
                for _p2 in range(p1 + 1, self.N_PIECES):
                    p2 = PieceId(_p2)
                    self.solver.add(
                        Implies(
                            And(Not(self.piece_captured[t, p1]), Not(self.piece_captured[t, p2])),
                            Or(
                                self.piece_row[t, p1] != self.piece_row[t, p2],
                                self.piece_col[t, p1] != self.piece_col[t, p2],
                            ),
                        ),
                    )

            # Captured pieces are in someone's hand
            for _p in range(self.N_PIECES):
                p = PieceId(_p)
                self.solver.add(
                    self.piece_captured[t, p] == (self.piece_in_hand_of[t, p] >= 0),
                )

            # Only Chicks can be promoted (to Hen)
            for _p in range(self.N_PIECES):
                p = PieceId(_p)
                self.solver.add(
                    Implies(
                        self.piece_promoted[t, p],
                        self.piece_type[p] == PieceType.CHICK.value,
                    ),
                )

    def _square_empty_or_opponent(self, t: TimeIndex, row: int, col: int, current_player: PlayerId) -> BoolRef:
        """Check if a square is empty or contains an opponent's piece."""
        square_conditions = []
        for _p in range(self.N_PIECES):
            p = PieceId(_p)
            # Square is occupied by piece p
            occupied_by_p = And(
                Not(self.piece_captured[t, p]),
                self.piece_row[t, p] == row,
                self.piece_col[t, p] == col,
            )
            # If occupied, must be opponent's piece
            square_conditions.append(
                Implies(occupied_by_p, self.piece_owner[t, p] != current_player),
            )
        return And(square_conditions)

    def _add_movement_constraints(self) -> None:
        """Add constraints for piece movements."""
        for _t in range(self.max_moves):
            t = TimeIndex(_t)
            move = self.moves[t]
            current_player = PlayerId(t % 2)  # 0 for Sente, 1 for Gote

            # The moving piece must belong to current player
            # Note: move.piece_id is a Z3 Int variable, not a value
            # We need to constrain it for all possible pieces
            piece_owner_constraints = []
            for _p in range(self.N_PIECES):
                p = PieceId(_p)
                piece_owner_constraints.append(
                    Implies(
                        move.piece_id == p,
                        self.piece_owner[t, p] == current_player,
                    ),
                )
            self.solver.add(And(piece_owner_constraints))

            # Handle regular moves vs drops
            # Since move.piece_id is a Z3 variable, we need to handle all cases
            for _p in range(self.N_PIECES):
                p = PieceId(_p)
                self.solver.add(
                    Implies(
                        move.piece_id == p,
                        If(
                            move.is_drop,
                            # Drop constraints
                            And(
                                self.piece_captured[t, p],
                                self.piece_in_hand_of[t, p] == current_player,
                                move.from_row == 0,
                                move.from_col == 0,
                                move.captures == -1,
                                # Can't drop on occupied square
                                self._square_empty_or_opponent(t, move.to_row, move.to_col, current_player),
                            ),
                            # Regular move constraints
                            And(
                                Not(self.piece_captured[t, p]),
                                move.from_row == self.piece_row[t, p],
                                move.from_col == self.piece_col[t, p],
                                self._valid_move_pattern(t, move, p),
                                # Can't move to square with own piece
                                self._square_empty_or_opponent(t, move.to_row, move.to_col, current_player),
                            ),
                        ),
                    ),
                )

            # Apply move effects
            self._apply_move_effects(t)

    def _valid_move_pattern(self, t: TimeIndex, move: MoveVariables, piece_id: PieceId) -> BoolRef:
        """Check if move follows piece movement rules.

        Args:
            t: Time step
            move: Move dictionary with Z3 variables
            piece_id: The actual piece ID (integer)

        """
        from_row = move.from_row
        from_col = move.from_col
        to_row = move.to_row
        to_col = move.to_col

        # Calculate movement delta
        d_row = to_row - from_row
        d_col = to_col - from_col

        # Get piece type (considering promotion)
        effective_type = If(
            self.piece_promoted[t, piece_id],
            PieceType.HEN.value,
            self.piece_type[piece_id],
        )

        # Define movement patterns for each piece
        valid_patterns = []

        # Lion - moves 1 square in any direction
        lion_valid = And(
            Abs(d_row) <= 1,
            Abs(d_col) <= 1,
            Or(d_row != 0, d_col != 0),  # Must move
        )
        valid_patterns.append(Implies(effective_type == PieceType.LION.value, lion_valid))

        # Giraffe - moves 1 square orthogonally
        giraffe_valid = Or(
            And(d_row == 0, Or(d_col == 1, d_col == -1)),
            And(d_col == 0, Or(d_row == 1, d_row == -1)),
        )
        valid_patterns.append(Implies(effective_type == PieceType.GIRAFFE.value, giraffe_valid))

        # Elephant - moves 1 square diagonally
        elephant_valid = And(
            Abs(d_row) == 1,
            Abs(d_col) == 1,
        )
        valid_patterns.append(Implies(effective_type == PieceType.ELEPHANT.value, elephant_valid))

        # Chick - moves 1 square forward (direction depends on owner)
        chick_forward = If(
            self.piece_owner[t, piece_id] == Player.SENTE.value,
            d_row == 1,  # Sente moves up (from row 1 toward row 4)
            d_row == -1,  # Gote moves down (from row 4 toward row 1)
        )
        chick_valid = And(chick_forward, d_col == 0)
        valid_patterns.append(Implies(effective_type == PieceType.CHICK.value, chick_valid))

        # Hen (promoted Chick) - moves like Gold (1 square orthogonally or forward diagonal)
        hen_valid = Or(
            # Orthogonal moves
            And(d_row == 0, Or(d_col == 1, d_col == -1)),
            And(d_col == 0, Or(d_row == 1, d_row == -1)),
            # Forward diagonal moves
            And(
                If(self.piece_owner[t, piece_id] == Player.SENTE.value, d_row == 1, d_row == -1),
                Or(d_col == 1, d_col == -1),
            ),
        )
        valid_patterns.append(Implies(effective_type == PieceType.HEN.value, hen_valid))

        # Combine all patterns - ALL must be satisfied
        return And(valid_patterns)

    def _apply_move_effects(self, t: TimeIndex) -> None:
        """Apply the effects of a move to get next board state."""
        move = self.moves[t]
        next_t = TimeIndex(t + 1)

        for _p in range(self.N_PIECES):
            p = PieceId(_p)
            # Default: pieces stay in same state
            same_position = And(
                self.piece_row[next_t, p] == self.piece_row[t, p],
                self.piece_col[next_t, p] == self.piece_col[t, p],
            )
            same_captured = self.piece_captured[next_t, p] == self.piece_captured[t, p]
            same_promoted = self.piece_promoted[next_t, p] == self.piece_promoted[t, p]
            same_hand = self.piece_in_hand_of[next_t, p] == self.piece_in_hand_of[t, p]

            # Moving piece
            is_moving = move.piece_id == p

            # Captured piece
            is_captured = And(
                move.captures == p,
                Not(move.is_drop),
            )

            # Apply effects based on role in move
            self.solver.add(
                If(
                    is_moving,
                    # This piece is moving
                    And(
                        self.piece_row[next_t, p] == move.to_row,
                        self.piece_col[next_t, p] == move.to_col,
                        self.piece_captured[next_t, p] == False,
                        self.piece_in_hand_of[next_t, p] == -1,
                        self.piece_owner[next_t, p] == self.piece_owner[t, p],  # Owner stays same when moving
                        # Check promotion (Chick reaching last rank)
                        If(
                            And(
                                self.piece_type[p] == PieceType.CHICK.value,
                                Or(
                                    And(self.piece_owner[t, p] == Player.SENTE.value, move.to_row == self.ROWS),
                                    And(self.piece_owner[t, p] == Player.GOTE.value, move.to_row == 1),
                                ),
                            ),
                            self.piece_promoted[next_t, p] == True,
                            same_promoted,
                        ),
                    ),
                    If(
                        is_captured,
                        # This piece is being captured
                        And(
                            self.piece_captured[next_t, p] == True,
                            self.piece_in_hand_of[next_t, p] == (t % 2),  # Current player
                            self.piece_promoted[next_t, p] == False,  # Demoted when captured
                            self.piece_owner[next_t, p] == (t % 2),  # Ownership changes to capturing player!
                            same_position,  # Position doesn't matter when captured
                        ),
                        # This piece is not involved in the move
                        And(
                            same_position,
                            same_captured,
                            same_promoted,
                            same_hand,
                            self.piece_owner[next_t, p] == self.piece_owner[t, p],  # Owner stays same
                        ),
                    ),
                ),
            )

        # Determine what piece (if any) is at destination
        # IMPORTANT: Can only capture OPPONENT's pieces!
        current_player = t % 2
        for _p in range(self.N_PIECES):
            p = PieceId(_p)
            self.solver.add(
                Implies(
                    And(
                        Not(self.piece_captured[t, p]),
                        p != move.piece_id,
                        self.piece_row[t, p] == move.to_row,
                        self.piece_col[t, p] == move.to_col,
                        self.piece_owner[t, p] != current_player,
                    ),  # Must be opponent's piece!
                    move.captures == p,
                ),
            )

        # If no piece at destination OR piece belongs to same player, no capture
        no_valid_capture = And(
            *[
                Or(
                    self.piece_captured[t, PieceId(p)],
                    p == move.piece_id,
                    self.piece_row[t, PieceId(p)] != move.to_row,
                    self.piece_col[t, PieceId(p)] != move.to_col,
                    self.piece_owner[t, PieceId(p)] == current_player,
                )  # Can't capture own pieces
                for p in range(self.N_PIECES)
            ],
        )
        self.solver.add(Implies(no_valid_capture, move.captures == -1))

    def add_victory_condition(self, t: TimeIndex) -> BoolRef:
        """Check victory conditions at time t.

        1. Opponent's Lion is captured
        2. Own Lion reaches opponent's back rank (without being in check)
        """
        current_player = PlayerId(t % 2)

        victory_conditions = []

        for _p in range(self.N_PIECES):
            p = PieceId(_p)
            # Victory by capturing opponent's Lion
            is_opponent_lion = And(
                self.piece_type[p] == PieceType.LION.value,
                self.piece_owner[t, p] != current_player,
            )
            victory_conditions.append(
                And(is_opponent_lion, self.piece_captured[t, p]),
            )

            # Victory by reaching opponent's back rank
            is_own_lion = And(
                self.piece_type[p] == PieceType.LION.value,
                self.piece_owner[t, p] == current_player,
            )
            reaches_back_rank = If(
                current_player == Player.SENTE.value,
                self.piece_row[t, p] == self.ROWS,  # Row 4 for Sente
                self.piece_row[t, p] == 1,  # Row 1 for Gote
            )

            # Simplified check detection - Lion is safe if no opponent piece can capture it
            # In next turn, opponent pieces that could attack this position
            lion_safe = True  # Simplified for now

            victory_conditions.append(
                And(is_own_lion, Not(self.piece_captured[t, p]), reaches_back_rank, lion_safe),
            )

        return Or(victory_conditions)

    def solve_mate_in_n(self, n: TimeIndex, winning_player: Player = Player.SENTE) -> list[MoveData] | None:
        """Try to find a mate in exactly n moves for the specified player.

        Args:
            n: Number of moves (must be odd for Sente to win, even for Gote)
            winning_player: Which player should win (default: SENTE)

        Returns:
            List of moves if mate found, None otherwise

        """
        if n > self.max_moves:
            return None

        # Check move parity
        last_player = (n - 1) % 2  # Who makes the last move
        if last_player != winning_player.value:
            print(f"  Note: {winning_player.name} cannot win in {n} moves (wrong parity)")
            return None

        s = Solver()
        s.add(self.solver.assertions())

        # Add victory condition at move n FOR THE WINNING PLAYER
        # The player who just moved (at time n-1) should be the winner
        victory_for_winner = self._victory_condition_for_player(n, winning_player.value)
        s.add(victory_for_winner)

        # No victory before move n
        for _t in range(n):
            t = TimeIndex(_t)
            s.add(Not(self.add_victory_condition(t)))

        if s.check() == sat:
            model = s.model()

            # Debug: Print initial board state
            print("\nInitial board state:")
            self.print_board_state(model, TimeIndex(0))

            # Debug: Print final board state
            print(f"\nBoard state after move {n}:")
            self.print_board_state(model, n)

            moves: list[MoveData] = []

            for _t in range(n):
                t = TimeIndex(_t)
                move = self.moves[t]

                piece_id = PieceId(model[move.piece_id].as_long())
                piece_type_val: int = model[self.piece_type[piece_id]].as_long()

                move_data = MoveData(
                    move_number=TimeIndex(t),
                    player="Sente" if t % 2 == 0 else "Gote",
                    piece_id=piece_id,
                    is_drop=is_true(model[move.is_drop]),
                    from_=(RowIndex(model[move.from_row].as_long()), ColIndex(model[move.from_col].as_long())),
                    to=(RowIndex(model[move.to_row].as_long()), ColIndex(model[move.to_col].as_long())),
                    captures=model[move.captures].as_long(),
                    piece_type=PieceType(piece_type_val),
                )

                # Debug: Print piece owner
                owner = model[self.piece_owner[t, piece_id]].as_long()
                print(f"\nDebug Move {t + 1}: Piece {piece_id} (type={piece_type_val}, owner={owner})")
                print(f"  From: ({model[move.from_row].as_long()}, {model[move.from_col].as_long()})")
                print(f"  To: ({model[move.to_row].as_long()}, {model[move.to_col].as_long()})")
                if move_data.captures >= 0:
                    cap_type = model[self.piece_type[PieceId(move_data.captures)]].as_long()
                    cap_owner = model[self.piece_owner[t, PieceId(move_data.captures)]].as_long()
                    print(f"  Captures: Piece {move_data.captures} (type={cap_type}, owner={cap_owner})")

                moves.append(move_data)

            # Check victory condition
            print("\nVictory condition check:")
            for _p in range(self.N_PIECES):
                p = PieceId(_p)
                if model[self.piece_type[p]].as_long() == PieceType.LION.value:
                    captured = is_true(model[self.piece_captured[n, p]])
                    row = model[self.piece_row[n, p]].as_long()
                    owner = model[self.piece_owner[n, p]].as_long()
                    print(f"  Lion {p} (owner={owner}): captured={captured}, row={row}")

            return moves

        return None

    def _victory_condition_for_player(self, t: TimeIndex, winning_player: PlayerId) -> BoolRef:
        """Check if the specified player has won at time t."""
        victory_conditions = []

        for _p in range(self.N_PIECES):
            p = PieceId(_p)
            # Victory by capturing opponent's Lion
            is_opponent_lion = And(
                self.piece_type[p] == PieceType.LION.value,
                self.piece_owner[t, p] != winning_player,  # Opponent's Lion
            )
            victory_conditions.append(
                And(is_opponent_lion, self.piece_captured[t, p]),
            )

            # Victory by reaching opponent's back rank
            is_own_lion = And(
                self.piece_type[p] == PieceType.LION.value,
                self.piece_owner[t, p] == winning_player,  # Own Lion
            )
            reaches_back_rank = If(
                winning_player == Player.SENTE.value,
                self.piece_row[t, p] == self.ROWS,  # Row 4 for Sente
                self.piece_row[t, p] == 1,  # Row 1 for Gote
            )

            # Simplified: assume Lion is safe at back rank
            victory_conditions.append(
                And(is_own_lion, Not(self.piece_captured[t, p]), reaches_back_rank),
            )

        return Or(victory_conditions)

    def print_board_state(self, model: dict, t: TimeIndex) -> None:
        """Print the board state at time t given a model."""
        print(f"\n=== Board at time {t} ===")
        board = [[" . " for _ in range(self.COLS)] for _ in range(self.ROWS)]

        pieces_symbols = {
            (PieceType.LION.value, Player.SENTE.value, False): " L ",
            (PieceType.LION.value, Player.GOTE.value, False): " l ",
            (PieceType.GIRAFFE.value, Player.SENTE.value, False): " G ",
            (PieceType.GIRAFFE.value, Player.GOTE.value, False): " g ",
            (PieceType.ELEPHANT.value, Player.SENTE.value, False): " E ",
            (PieceType.ELEPHANT.value, Player.GOTE.value, False): " e ",
            (PieceType.CHICK.value, Player.SENTE.value, False): " C ",
            (PieceType.CHICK.value, Player.GOTE.value, False): " c ",
            (PieceType.CHICK.value, Player.SENTE.value, True): " H ",  # Hen
            (PieceType.CHICK.value, Player.GOTE.value, True): " h ",  # hen
        }

        for _p in range(self.N_PIECES):
            p = PieceId(_p)
            if not is_true(model[self.piece_captured[t, p]]):
                row = model[self.piece_row[t, p]].as_long() - 1
                col = model[self.piece_col[t, p]].as_long() - 1
                ptype = model[self.piece_type[p]].as_long()
                owner = model[self.piece_owner[t, p]].as_long()
                promoted = is_true(model[self.piece_promoted[t, p]])

                board[row][col] = pieces_symbols.get((ptype, owner, promoted), " ? ")

        # Print from Gote's perspective (row 4 at top)
        for row in reversed(range(self.ROWS)):
            print("".join(board[row]))

        # Print captured pieces
        sente_hand = []
        gote_hand = []
        for _p in range(self.N_PIECES):
            p = PieceId(_p)
            if is_true(model[self.piece_captured[t, p]]):
                holder = model[self.piece_in_hand_of[t, p]].as_long()
                ptype = model[self.piece_type[p]].as_long()
                piece_names = ["Lion", "Giraffe", "Elephant", "Chick"]
                if holder == 0:
                    sente_hand.append(piece_names[ptype])
                else:
                    gote_hand.append(piece_names[ptype])

        print(f"Sente's hand: {sente_hand}")
        print(f"Gote's hand: {gote_hand}")


# Example usage
def example_mate_problem() -> None:
    """Set up and solve a simple mate problem."""
    print("=== Dōbutsu Shōgi Mate Solver ===")
    print("Initial position: Standard starting position")

    # Create solver
    solver = DobutsuShogiZ3(max_moves=7)

    # First, let's verify what moves are possible from starting position
    print("\nTesting: What moves can Sente's Chick make from (2,2)?")
    test_solver = Solver()
    test_solver.add(solver.solver.assertions())

    # Force a specific move to see if it's valid
    move = solver.moves[TimeIndex(0)]
    test_solver.add(move.piece_id == 3)  # Sente's Chick
    test_solver.add(move.from_row == 2)
    test_solver.add(move.from_col == 2)
    test_solver.add(Not(move.is_drop))

    # Try different destinations
    for to_row, to_col in [(1, 2), (2, 1), (2, 3), (3, 2)]:
        s = Solver()
        s.add(test_solver.assertions())
        s.add(move.to_row == to_row)
        s.add(move.to_col == to_col)

        if s.check() == sat:
            print(f"  Can move to ({to_row}, {to_col}): YES")
        else:
            print(f"  Can move to ({to_row}, {to_col}): NO")

    print("\n" + "=" * 50 + "\n")

    # Try to find mate for SENTE (first player)
    print("Looking for mates where SENTE wins...")
    for _n in [1, 3, 5, 7]:
        n = TimeIndex(_n)
        print(f"\nSearching for SENTE mate in {n} moves...")
        solution = solver.solve_mate_in_n(n, Player.SENTE)

        if solution:
            print(f"Found SENTE mate in {n} moves!")
            for move in solution:
                if move.is_drop:
                    print(f"Move {move.move_number} ({move.player}): Drop {move.piece_type} at {move.to}")
                else:
                    print(
                        f"Move {move.move_number} ({move.player}): "
                        f"{move.piece_type} from {move.from_} to {move.to}"
                        f"{' (capture)' if move.captures >= 0 else ''}",
                    )
            break
    else:
        print("\nNo SENTE mate found within 7 moves")
        print("This is expected - Dōbutsu Shōgi has been solved,")
        print("and GOTE (second player) has a winning strategy from the start.")


def test_custom_position() -> None:
    """Test with a custom position where mate exists."""
    print("\n\n=== Custom Position Test ===")
    print("Setting up a position where SENTE can mate in 1...")

    # You would need to modify DobutsuShogiZ3 to accept custom positions
    # For now, this is just a placeholder
    print("(To test custom positions, modify the _add_initial_position method)")


if __name__ == "__main__":
    example_mate_problem()
