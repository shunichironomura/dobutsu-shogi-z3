"""Core game types and data structures for Dōbutsu Shōgi."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import NewType

# Basic type aliases
PieceId = NewType("PieceId", int)
PieceTypeId = NewType("PieceTypeId", int)
PlayerId = NewType("PlayerId", int)
TimeIndex = NewType("TimeIndex", int)
ColIndex = NewType("ColIndex", int)
RowIndex = NewType("RowIndex", int)


@dataclass(frozen=True, slots=True)
class Position:
    """Position on the Dōbutsu Shōgi board."""

    row: RowIndex  # 1-4
    col: ColIndex  # 1-3

    def __str__(self) -> str:
        """Return string representation of the position."""
        col_letter = chr(ord("A") + self.col - 1)  # Convert 1-3 to A-C
        row_number = 5 - self.row  # Convert 1-4 to 4-1
        return f"{col_letter}{row_number}"

    def __repr__(self) -> str:
        """Return string representation of the position."""
        return f"Position(row={self.row}, col={self.col})"


class PieceType(Enum):
    """Piece types in Dōbutsu Shōgi."""

    LION = PieceTypeId(0)
    GIRAFFE = PieceTypeId(1)
    ELEPHANT = PieceTypeId(2)
    CHICK = PieceTypeId(3)
    HEN = PieceTypeId(4)

    @classmethod
    def min_value_basic(cls) -> PieceTypeId:
        """Get the minimum value of the basic piece types."""
        return cls.LION.value

    @classmethod
    def max_value_basic(cls) -> PieceTypeId:
        """Get the maximum value of the basic piece types."""
        return cls.CHICK.value


class Player(Enum):
    """Players - using Shogi terminology."""

    SENTE = PlayerId(0)
    GOTE = PlayerId(1)


@dataclass(frozen=True, slots=True)
class PieceState:
    """State of a piece in Dōbutsu Shōgi."""

    piece_id: PieceId
    piece_type: PieceType
    piece_owner: PlayerId
    row: RowIndex
    col: ColIndex


@dataclass(frozen=True, slots=True)
class MoveData:
    """Data structure for a move in Dōbutsu Shōgi."""

    move_number: TimeIndex
    player: str
    piece_id: PieceId
    is_drop: bool
    from_: Position
    to: Position
    captures: int
    piece_type: PieceType
