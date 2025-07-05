"""Implements a complete Z3 model for Dōbutsu Shōgi (Animal Chess)."""

from enum import Enum
from typing import TYPE_CHECKING, NewType

from z3 import Abs, And, Bool, BoolRef, If, Implies, Int, Not, Or, Solver, is_true, sat

if TYPE_CHECKING:
    from z3.z3 import ArithRef

# ===========================================================================
# Dōbutsu Shōgi (Animal Chess) - Complete Z3 Model
# ===========================================================================


PieceId = NewType("PieceId", int)
PieceTypeId = NewType("PieceTypeId", int)
PlayerId = NewType("PlayerId", int)
MoveIndex = NewType("MoveIndex", int)


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


class DobutsuShogiZ3:
    """Complete Z3 model for Dōbutsu Shōgi."""

    def __init__(self, max_moves: int = 20) -> None:
        """Initialize the model.

        Args:
            max_moves: Maximum number of half-moves to search

        """
        # Board dimensions
        self.ROWS = 4
        self.COLS = 3
        self.max_moves = max_moves

        # Piece counts
        self.NUM_PIECES = 8  # 4 pieces per player

        # Initialize solver
        self.solver = Solver()

        # Create variables
        self._create_variables()

        # Add game rules
        self._add_initial_position()
        self._add_basic_constraints()
        self._add_movement_constraints()

    def _create_variables(self) -> None:
        """Create all Z3 variables."""
        # Static piece properties (never change)
        self.piece_type: dict[PieceId, ArithRef] = {}  # piece id -> piece type
        self.piece_owner: dict[PieceId, ArithRef] = {}  # piece id -> owner (0 for Sente, 1 for Gote)
        for _p in range(self.NUM_PIECES):
            p = PieceId(_p)
            self.piece_type[p] = Int(f"piece_{p}_type")
            self.piece_owner[p] = Int(f"piece_{p}_owner")
            # Constraints on static properties
            self.solver.add(self.piece_type[p] >= PieceType.min_value())
            self.solver.add(self.piece_type[p] <= PieceType.max_value())
            self.solver.add(Or(self.piece_owner[p] == 0, self.piece_owner[p] == 1))

        # Dynamic piece state (changes over time)
        self.piece_row: dict[MoveIndex, dict[PieceId, ArithRef]] = {}  # (move index, piece id) -> row
        self.piece_col: dict[MoveIndex, dict[PieceId, ArithRef]] = {}
        self.piece_captured: dict[MoveIndex, dict[PieceId, BoolRef]] = {}
        self.piece_promoted: dict[MoveIndex, dict[PieceId, BoolRef]] = {}
        self.piece_in_hand_of: dict[
            MoveIndex,
            dict[PieceId, ArithRef],
        ] = {}  # Which player holds this piece (-1 if on board)

        for _t in range(self.max_moves + 1):
            t = MoveIndex(_t)
            self.piece_row[t] = {}
            self.piece_col[t] = {}
            self.piece_captured[t] = {}
            self.piece_promoted[t] = {}
            self.piece_in_hand_of[t] = {}

            for _p in range(self.NUM_PIECES):
                p = PieceId(_p)
                self.piece_row[t][p] = Int(f"piece_{p}_row_t{t}")
                self.piece_col[t][p] = Int(f"piece_{p}_col_t{t}")
                self.piece_captured[t][p] = Bool(f"piece_{p}_captured_t{t}")
                self.piece_promoted[t][p] = Bool(f"piece_{p}_promoted_t{t}")
                self.piece_in_hand_of[t][p] = Int(f"piece_{p}_in_hand_t{t}")

                # Constraints
                self.solver.add(self.piece_row[t][p] >= 1)
                self.solver.add(self.piece_row[t][p] <= self.ROWS)
                self.solver.add(self.piece_col[t][p] >= 1)
                self.solver.add(self.piece_col[t][p] <= self.COLS)
                self.solver.add(self.piece_in_hand_of[t][p] >= -1)
                self.solver.add(self.piece_in_hand_of[t][p] <= 1)

        # Move representation
        self.moves = []
        for _t in range(self.max_moves):
            t = MoveIndex(_t)
            self.moves.append(
                {
                    "piece_id": Int(f"move_{t}_piece"),
                    "from_row": Int(f"move_{t}_from_row"),
                    "from_col": Int(f"move_{t}_from_col"),
                    "to_row": Int(f"move_{t}_to_row"),
                    "to_col": Int(f"move_{t}_to_col"),
                    "is_drop": Bool(f"move_{t}_is_drop"),
                    "captures": Int(f"move_{t}_captures"),  # -1 if no capture, else piece id
                },
            )

            # Constraints on moves
            move = self.moves[t]
            self.solver.add(move["piece_id"] >= 0)
            self.solver.add(move["piece_id"] < self.NUM_PIECES)
            self.solver.add(move["from_row"] >= 0)  # 0 means drop
            self.solver.add(move["from_row"] <= self.ROWS)
            self.solver.add(move["from_col"] >= 0)
            self.solver.add(move["from_col"] <= self.COLS)
            self.solver.add(move["to_row"] >= 1)
            self.solver.add(move["to_row"] <= self.ROWS)
            self.solver.add(move["to_col"] >= 1)
            self.solver.add(move["to_col"] <= self.COLS)
            self.solver.add(move["captures"] >= -1)
            self.solver.add(move["captures"] < self.NUM_PIECES)

    def _add_initial_position(self) -> None:
        """Set up the initial board position."""
        # Define initial pieces
        initial_setup = [
            # Sente (bottom player)
            (0, PieceType.ELEPHANT, Player.SENTE, 1, 1),  # Elephant at bottom-left
            (1, PieceType.LION, Player.SENTE, 1, 2),  # Lion at bottom-center
            (2, PieceType.GIRAFFE, Player.SENTE, 1, 3),  # Giraffe at bottom-right
            (3, PieceType.CHICK, Player.SENTE, 2, 2),  # Chick in front of Lion
            # Gote (top player)
            (4, PieceType.GIRAFFE, Player.GOTE, 4, 1),  # Giraffe at top-left
            (5, PieceType.LION, Player.GOTE, 4, 2),  # Lion at top-center
            (6, PieceType.ELEPHANT, Player.GOTE, 4, 3),  # Elephant at top-right
            (7, PieceType.CHICK, Player.GOTE, 3, 2),  # Chick in front of Lion
        ]

        for _piece_id, ptype, owner, row, col in initial_setup:
            piece_id = PieceId(_piece_id)
            # Static properties
            self.solver.add(self.piece_type[piece_id] == ptype.value)
            self.solver.add(self.piece_owner[piece_id] == owner.value)

            # Initial position
            initial_move_index = MoveIndex(0)
            self.solver.add(self.piece_row[initial_move_index][piece_id] == row)
            self.solver.add(self.piece_col[initial_move_index][piece_id] == col)
            self.solver.add(Not(self.piece_captured[initial_move_index][piece_id]))
            self.solver.add(Not(self.piece_promoted[initial_move_index][piece_id]))
            self.solver.add(self.piece_in_hand_of[initial_move_index][piece_id] == -1)  # On board

    def _add_basic_constraints(self) -> None:
        """Add basic game constraints."""
        for _t in range(self.max_moves + 1):
            t = MoveIndex(_t)
            # No two pieces on same square (unless one is captured)
            for _p1 in range(self.NUM_PIECES):
                p1 = PieceId(_p1)
                for _p2 in range(p1 + 1, self.NUM_PIECES):
                    p2 = PieceId(_p2)
                    self.solver.add(
                        Implies(
                            And(Not(self.piece_captured[t][p1]), Not(self.piece_captured[t][p2])),
                            Or(
                                self.piece_row[t][p1] != self.piece_row[t][p2],
                                self.piece_col[t][p1] != self.piece_col[t][p2],
                            ),
                        ),
                    )

            # Captured pieces are in someone's hand
            for _p in range(self.NUM_PIECES):
                p = PieceId(_p)
                self.solver.add(
                    self.piece_captured[t][p] == (self.piece_in_hand_of[t][p] >= 0),
                )

            # Only Chicks can be promoted (to Hen)
            for _p in range(self.NUM_PIECES):
                p = PieceId(_p)
                self.solver.add(
                    Implies(
                        self.piece_promoted[t][p],
                        self.piece_type[p] == PieceType.CHICK.value,
                    ),
                )

    def _add_movement_constraints(self) -> None:
        """Add constraints for piece movements."""
        for _t in range(self.max_moves):
            t = MoveIndex(_t)
            move = self.moves[t]
            current_player = t % 2  # 0 for Sente, 1 for Gote

            # The moving piece must belong to current player
            self.solver.add(
                self.piece_owner[move["piece_id"]] == current_player,
            )

            # Handle regular moves vs drops
            self.solver.add(
                If(
                    move["is_drop"],
                    # Drop constraints
                    And(
                        self.piece_captured[t][move["piece_id"]],
                        self.piece_in_hand_of[t][move["piece_id"]] == current_player,
                        move["from_row"] == 0,
                        move["from_col"] == 0,
                        move["captures"] == -1,
                    ),
                    # Regular move constraints
                    And(
                        Not(self.piece_captured[t][move["piece_id"]]),
                        move["from_row"] == self.piece_row[t][move["piece_id"]],
                        move["from_col"] == self.piece_col[t][move["piece_id"]],
                        self._valid_move_pattern(t, move),
                    ),
                ),
            )

            # Apply move effects
            self._apply_move_effects(t)

    def _valid_move_pattern(self, t: MoveIndex, move: dict) -> BoolRef:
        """Check if move follows piece movement rules."""
        piece_id = move["piece_id"]
        from_row = move["from_row"]
        from_col = move["from_col"]
        to_row = move["to_row"]
        to_col = move["to_col"]

        # Calculate movement delta
        d_row = to_row - from_row
        d_col = to_col - from_col

        # Get piece type (considering promotion)
        effective_type = If(
            self.piece_promoted[t][piece_id],
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
        valid_patterns.append((effective_type == PieceType.LION.value, lion_valid))

        # Giraffe - moves 1 square orthogonally
        giraffe_valid = Or(
            And(d_row == 0, Or(d_col == 1, d_col == -1)),
            And(d_col == 0, Or(d_row == 1, d_row == -1)),
        )
        valid_patterns.append((effective_type == PieceType.GIRAFFE.value, giraffe_valid))

        # Elephant - moves 1 square diagonally
        elephant_valid = And(
            Abs(d_row) == 1,
            Abs(d_col) == 1,
        )
        valid_patterns.append((effective_type == PieceType.ELEPHANT.value, elephant_valid))

        # Chick - moves 1 square forward (direction depends on owner)
        chick_forward = If(
            self.piece_owner[piece_id] == Player.SENTE.value,
            d_row == 1,  # Sente moves up
            d_row == -1,  # Gote moves down
        )
        chick_valid = And(chick_forward, d_col == 0)
        valid_patterns.append((effective_type == PieceType.CHICK.value, chick_valid))

        # Hen (promoted Chick) - moves like Gold (1 square orthogonally or forward diagonal)
        hen_valid = Or(
            # Orthogonal moves
            And(d_row == 0, Or(d_col == 1, d_col == -1)),
            And(d_col == 0, Or(d_row == 1, d_row == -1)),
            # Forward diagonal moves
            And(
                If(self.piece_owner[piece_id] == Player.SENTE.value, d_row == 1, d_row == -1),
                Or(d_col == 1, d_col == -1),
            ),
        )
        valid_patterns.append((effective_type == PieceType.HEN.value, hen_valid))

        # Combine all patterns
        return Or(*[Implies(ptype == effective_type, pattern) for ptype, pattern in valid_patterns])

    def _apply_move_effects(self, t: int) -> None:
        """Apply the effects of a move to get next board state."""
        move = self.moves[t]

        for p in range(self.NUM_PIECES):
            # Default: pieces stay in same state
            same_position = And(
                self.piece_row[t + 1][p] == self.piece_row[t][p],
                self.piece_col[t + 1][p] == self.piece_col[t][p],
            )
            same_captured = self.piece_captured[t + 1][p] == self.piece_captured[t][p]
            same_promoted = self.piece_promoted[t + 1][p] == self.piece_promoted[t][p]
            same_hand = self.piece_in_hand_of[t + 1][p] == self.piece_in_hand_of[t][p]

            # Moving piece
            is_moving = move["piece_id"] == p

            # Captured piece
            is_captured = And(
                move["captures"] == p,
                Not(move["is_drop"]),
            )

            # Apply effects based on role in move
            self.solver.add(
                If(
                    is_moving,
                    # This piece is moving
                    And(
                        self.piece_row[t + 1][p] == move["to_row"],
                        self.piece_col[t + 1][p] == move["to_col"],
                        self.piece_captured[t + 1][p] == False,
                        self.piece_in_hand_of[t + 1][p] == -1,
                        # Check promotion (Chick reaching last rank)
                        If(
                            And(
                                self.piece_type[p] == PieceType.CHICK.value,
                                Or(
                                    And(self.piece_owner[p] == Player.SENTE.value, move["to_row"] == self.ROWS),
                                    And(self.piece_owner[p] == Player.GOTE.value, move["to_row"] == 1),
                                ),
                            ),
                            self.piece_promoted[t + 1][p] == True,
                            same_promoted,
                        ),
                    ),
                    If(
                        is_captured,
                        # This piece is being captured
                        And(
                            self.piece_captured[t + 1][p] == True,
                            self.piece_in_hand_of[t + 1][p] == (t % 2),  # Current player
                            self.piece_promoted[t + 1][p] == False,  # Demoted when captured
                            same_position,  # Position doesn't matter when captured
                        ),
                        # This piece is not involved in the move
                        And(same_position, same_captured, same_promoted, same_hand),
                    ),
                ),
            )

        # Determine what piece (if any) is at destination
        for p in range(self.NUM_PIECES):
            self.solver.add(
                Implies(
                    And(
                        Not(self.piece_captured[t][p]),
                        p != move["piece_id"],
                        self.piece_row[t][p] == move["to_row"],
                        self.piece_col[t][p] == move["to_col"],
                    ),
                    move["captures"] == p,
                ),
            )

        # If no piece at destination, no capture
        no_piece_at_dest = And(
            *[
                Or(
                    self.piece_captured[t][p],
                    p == move["piece_id"],
                    self.piece_row[t][p] != move["to_row"],
                    self.piece_col[t][p] != move["to_col"],
                )
                for p in range(self.NUM_PIECES)
            ],
        )
        self.solver.add(Implies(no_piece_at_dest, move["captures"] == -1))

    def add_victory_condition(self, t: int) -> BoolRef:
        """Check victory conditions at time t:
        1. Opponent's Lion is captured
        2. Own Lion reaches opponent's back rank (without being in check)
        """
        current_player = t % 2

        # Find Lions
        sente_lion = None
        gote_lion = None
        for p in range(self.NUM_PIECES):
            if self.solver.check() == sat:
                m = self.solver.model()
                if m.eval(self.piece_type[p]).as_long() == PieceType.LION.value:
                    if m.eval(self.piece_owner[p]).as_long() == Player.SENTE.value:
                        sente_lion = p
                    else:
                        gote_lion = p

        # For actual solving, we need to find Lions dynamically
        victory_conditions = []

        for p in range(self.NUM_PIECES):
            # Victory by capturing opponent's Lion
            is_opponent_lion = And(
                self.piece_type[p] == PieceType.LION.value,
                self.piece_owner[p] != current_player,
            )
            victory_conditions.append(
                And(is_opponent_lion, self.piece_captured[t][p]),
            )

            # Victory by reaching opponent's back rank
            is_own_lion = And(
                self.piece_type[p] == PieceType.LION.value,
                self.piece_owner[p] == current_player,
            )
            reaches_back_rank = If(
                current_player == Player.SENTE.value,
                self.piece_row[t][p] == self.ROWS,  # Row 4 for Sente
                self.piece_row[t][p] == 1,  # Row 1 for Gote
            )

            # Check if Lion would be in check at back rank
            # (Simplified - full implementation would check all opponent pieces)
            not_in_check = True  # Placeholder

            victory_conditions.append(
                And(is_own_lion, reaches_back_rank, not_in_check),
            )

        return Or(victory_conditions)

    def solve_mate_in_n(self, n: int) -> list[dict] | None:
        """Try to find a mate in exactly n moves

        Args:
            n: Number of moves (must be odd for first player to win)

        Returns:
            List of moves if mate found, None otherwise

        """
        if n > self.max_moves:
            return None

        s = Solver()
        s.add(self.solver.assertions())

        # Add victory condition at move n
        s.add(self.add_victory_condition(n))

        # No victory before move n
        for t in range(n):
            s.add(Not(self.add_victory_condition(t)))

        if s.check() == sat:
            model = s.model()
            moves = []

            for t in range(n):
                move = self.moves[t]
                move_data = {
                    "move_number": t + 1,
                    "player": "Sente" if t % 2 == 0 else "Gote",
                    "piece_id": model[move["piece_id"]].as_long(),
                    "is_drop": is_true(model[move["is_drop"]]),
                    "from": (model[move["from_row"]].as_long(), model[move["from_col"]].as_long()),
                    "to": (model[move["to_row"]].as_long(), model[move["to_col"]].as_long()),
                    "captures": model[move["captures"]].as_long(),
                }

                # Get piece info
                pid = move_data["piece_id"]
                piece_type_val = model[self.piece_type[pid]].as_long()
                piece_types = ["Lion", "Giraffe", "Elephant", "Chick", "Hen"]
                move_data["piece_type"] = piece_types[piece_type_val]

                moves.append(move_data)

            return moves

        return None

    def print_board_state(self, model, t: int) -> None:
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

        for p in range(self.NUM_PIECES):
            if not is_true(model[self.piece_captured[t][p]]):
                row = model[self.piece_row[t][p]].as_long() - 1
                col = model[self.piece_col[t][p]].as_long() - 1
                ptype = model[self.piece_type[p]].as_long()
                owner = model[self.piece_owner[p]].as_long()
                promoted = is_true(model[self.piece_promoted[t][p]])

                board[row][col] = pieces_symbols.get((ptype, owner, promoted), " ? ")

        # Print from Gote's perspective (row 4 at top)
        for row in reversed(range(self.ROWS)):
            print("".join(board[row]))

        # Print captured pieces
        sente_hand = []
        gote_hand = []
        for p in range(self.NUM_PIECES):
            if is_true(model[self.piece_captured[t][p]]):
                holder = model[self.piece_in_hand_of[t][p]].as_long()
                ptype = model[self.piece_type[p]].as_long()
                piece_names = ["Lion", "Giraffe", "Elephant", "Chick"]
                if holder == 0:
                    sente_hand.append(piece_names[ptype])
                else:
                    gote_hand.append(piece_names[ptype])

        print(f"Sente's hand: {sente_hand}")
        print(f"Gote's hand: {gote_hand}")


# Example usage
def example_mate_problem():
    """Set up and solve a simple mate problem"""
    print("=== Dōbutsu Shōgi Mate Solver ===")

    # Create solver
    solver = DobutsuShogiZ3(max_moves=7)

    # Try to find mate in 1, 3, 5 moves
    for n in [1, 3, 5]:
        print(f"\nSearching for mate in {n} moves...")
        solution = solver.solve_mate_in_n(n)

        if solution:
            print(f"Found mate in {n} moves!")
            for move in solution:
                if move["is_drop"]:
                    print(f"Move {move['move_number']} ({move['player']}): Drop {move['piece_type']} at {move['to']}")
                else:
                    print(
                        f"Move {move['move_number']} ({move['player']}): "
                        f"{move['piece_type']} from {move['from']} to {move['to']}"
                        f"{' (capture)' if move['captures'] >= 0 else ''}",
                    )
            break
    else:
        print("No mate found within 5 moves")


if __name__ == "__main__":
    example_mate_problem()
