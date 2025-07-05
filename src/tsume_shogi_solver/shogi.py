"""Shogi model."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum, StrEnum, auto


class PieceType(Enum):
    """Shogi piece types."""

    # (Piece name, number of pieces)
    OSHO = ("王将", 2)
    HISHA = ("飛車", 2)
    KAKUGYO = ("角行", 2)
    KINSHO = ("金将", 4)
    GINSHO = ("銀将", 4)
    KEIMA = ("桂馬", 4)
    KYOSHA = ("香車", 4)
    FUHYO = ("歩兵", 18)

    def __str__(self) -> str:
        """Get the string representation of the piece type."""
        return self.value[0]

    def n_pieces(self) -> int:
        """Get the number of pieces of this type."""
        return self.value[1]

    def abbreviation(self) -> str:
        """Get the abbreviation of the piece type."""
        return self.value[0][0]

    def can_promote(self) -> bool:
        """Check if the piece can promote."""
        return self in {
            PieceType.HISHA,
            PieceType.KAKUGYO,
            PieceType.GINSHO,
            PieceType.KEIMA,
            PieceType.KYOSHA,
            PieceType.FUHYO,
        }

    def promote(self) -> PromotedPieceType:
        """Promote the piece to its promoted type."""
        match self:
            case PieceType.HISHA:
                return PromotedPieceType.RYUO
            case PieceType.KAKUGYO:
                return PromotedPieceType.RYUMA
            case PieceType.GINSHO:
                return PromotedPieceType.NARIGIN
            case PieceType.KEIMA:
                return PromotedPieceType.NARIKEI
            case PieceType.KYOSHA:
                return PromotedPieceType.NARIKYO
            case PieceType.FUHYO:
                return PromotedPieceType.TOKIN
            case _:
                msg = f"Cannot promote {self.value}"
                raise ValueError(msg)


class PromotedPieceType(StrEnum):
    """Shogi promoted piece types."""

    # Promoted pieces
    RYUO = "龍王"
    RYUMA = "龍馬"
    NARIGIN = "成銀"
    NARIKEI = "成桂"
    NARIKYO = "成香"
    TOKIN = "と金"

    def abbreviation(self) -> str:
        """Get the abbreviation of the piece type."""
        if self is PromotedPieceType.RYUMA:
            # Special case for 龍馬 (Ryūma) to return "馬" instead of "龍"
            return "馬"
        return self.value[0]

    def promoted_from(self) -> PieceType:
        """Get the basic piece type that this piece was promoted from."""
        match self:
            case PromotedPieceType.RYUO:
                return PieceType.HISHA
            case PromotedPieceType.RYUMA:
                return PieceType.KAKUGYO
            case PromotedPieceType.NARIGIN:
                return PieceType.GINSHO
            case PromotedPieceType.NARIKEI:
                return PieceType.KEIMA
            case PromotedPieceType.NARIKYO:
                return PieceType.KYOSHA
            case PromotedPieceType.TOKIN:
                return PieceType.FUHYO
            case _:
                msg = f"Cannot demote {self.value}"
                raise ValueError(msg)


class Column(Enum):
    """Shogi board columns."""

    one = 1
    two = 2
    three = 3
    four = 4
    five = 5
    six = 6
    seven = 7
    eight = 8
    nine = 9

    def __str__(self) -> str:
        """Get the string representation of the column."""
        return str(self.value)


TO_JAPANESE_NUMBER = {
    1: "一",
    2: "二",
    3: "三",
    4: "四",
    5: "五",
    6: "六",
    7: "七",
    8: "八",
    9: "九",
}


class Row(Enum):
    """Shogi board rows."""

    one = 1
    two = 2
    three = 3
    four = 4
    five = 5
    six = 6
    seven = 7
    eight = 8
    nine = 9

    def __str__(self) -> str:
        """Get the string representation of the row."""
        return TO_JAPANESE_NUMBER[self.value]


@dataclass(frozen=True, slots=True)
class Cell:
    """Shogi board locations."""

    column: Column
    row: Row

    def __str__(self) -> str:
        """Get the string representation of the board location."""
        return f"{self.column}{self.row}"

    def as_tuple(self) -> tuple[int, int]:
        """Get the board location as a tuple of (column, row)."""
        return (self.column.value, self.row.value)


class PieceStand:
    """Shogi piece stand."""


class Player(Enum):
    """Players in Tsume-Shogi."""

    SENTE = auto()  # First player (attacker in Tsume-Shogi)
    GOTE = auto()  # Second player (defender)


@dataclass(frozen=True, slots=True)
class PieceState:
    """Shogi piece state."""

    owner: Player
    location: Cell | PieceStand
    is_promoted: bool = False


@dataclass(frozen=True, slots=True)
class Move:
    """Shogi move."""

    piece_type: PieceType
    from_location: Cell | PieceStand
    to_location: Cell
    is_promotion: bool = False

    def __str__(self) -> str:
        """Get the string representation of the move."""
        return f"{self.piece_type.abbreviation()} {self.from_location} -> {self.to_location}"


@dataclass(frozen=True, slots=True)
class ShogiState:
    """Shogi game state."""

    piece_states: frozenset[tuple[PieceType, PieceState]]
    next_player: Player

    def __post_init__(self) -> None:
        """Post-initialization checks."""
        # Check the number of pieces for each type
        n_pieces_counter = Counter(piece_type for piece_type, _ in self.piece_states)
        for piece_type in PieceType:
            assert n_pieces_counter[piece_type] == piece_type.n_pieces(), (
                f"Invalid number of pieces for {piece_type}: "
                f"{n_pieces_counter[piece_type]} instead of {piece_type.n_pieces()}"
            )

        # Check that atmost one piece can be in a cell
        locations = [
            piece_state.location for _, piece_state in self.piece_states if isinstance(piece_state.location, Cell)
        ]
        assert len(locations) == len(set(locations)), "Multiple pieces in the same cell"

        # TODO: There are plenty of other checks that can be added here

    def move(self, move: Move) -> ShogiState:
        """Return a new ShogiState with the given move applied."""
        # Find the piece to move. We need this because `move` does not contain `is_promoted` information.
        piece_to_move = next(
            iter(
                piece
                for piece in self.piece_states
                if piece[0] == move.piece_type
                and piece[1].owner == self.next_player
                and piece[1].location == move.from_location
            ),
        )
        try:
            piece_at_destination: tuple[PieceType, PieceState] | None = next(
                iter(piece for piece in self.piece_states if piece[1].location == move.to_location),
            )
        except StopIteration:
            piece_at_destination = None

        piece_at_destination

        new_piece_states = set(self.piece_states)

        # Remove the piece from its current location
        new_piece_states.remove((move.piece_type, PieceState(self.next_player, move.from_location, Player.SENTE)))

        # Add the piece to its new location
        new_piece_states.add(
            (move.piece_type, PieceState(move.to_location, Player.SENTE, is_promoted=move.is_promotion)),
        )

        # Switch the next player
        next_player = Player.GOTE if self.next_player == Player.SENTE else Player.SENTE

        return ShogiState(frozenset(new_piece_states), next_player)
