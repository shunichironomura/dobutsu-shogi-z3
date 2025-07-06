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
Position = tuple[RowIndex, ColIndex]


class PieceType(Enum):
    """Piece types in Dōbutsu Shōgi."""

    LION = PieceTypeId(0)
    GIRAFFE = PieceTypeId(1)
    ELEPHANT = PieceTypeId(2)
    CHICK = PieceTypeId(3)
    HEN = PieceTypeId(4)

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
