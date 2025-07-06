"""Core algebraic types and protocols for Dōbutsu Shōgi solver."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, NewType, Protocol, Union

if TYPE_CHECKING:
    from z3.z3 import ArithRef, BoolRef

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


@dataclass
class MoveVariables:
    """Variables for a move in Dōbutsu Shōgi."""

    piece_id: ArithRef
    from_row: ArithRef
    from_col: ArithRef
    to_row: ArithRef
    to_col: ArithRef
    is_drop: BoolRef
    captures: ArithRef


# Problem Types
@dataclass(frozen=True)
class CheckmateProblem:
    """Problem specification for finding checkmate."""

    initial_state: list[PieceState]
    winning_player: Player
    max_moves: int


@dataclass(frozen=True)
class ReachabilityProblem:
    """Problem specification for proving piece reachability."""

    initial_state: list[PieceState]
    piece_id: PieceId
    target: Position
    player: Player
    max_moves: int


@dataclass(frozen=True)
class TsumeProblem:
    """Problem specification for general Tsume solving."""

    initial_state: list[PieceState]
    constraints: list[BoolRef]
    max_moves: int


# Union type for all problems
Problem = CheckmateProblem | ReachabilityProblem | TsumeProblem


# Solution Types
@dataclass(frozen=True)
class CheckmateSolution:
    """Solution for checkmate problem."""

    moves: list[MoveData]
    winning_player: Player
    mate_in: int


@dataclass(frozen=True)
class ReachabilitySolution:
    """Solution for reachability problem."""

    moves: list[MoveData]
    piece_id: PieceId
    reached: Position


@dataclass(frozen=True)
class TsumeSolution:
    """Solution for general Tsume problem."""

    moves: list[MoveData]
    satisfied_constraints: list[BoolRef]


# Union type for all solutions
Solution = Union[CheckmateSolution, ReachabilitySolution, TsumeSolution]


# Solver Protocol
class Solver(Protocol):
    """Protocol for all solver types."""

    def solve(self, problem: Problem) -> Solution | None:
        """Solve the given problem."""
        ...


# Default initial board setup
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
