"""Problem and solution type definitions for Dōbutsu Shōgi solver."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from .core import MoveData, PieceId, PieceState, Player, Position

if TYPE_CHECKING:
    from z3.z3 import BoolRef


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
Solution = CheckmateSolution | ReachabilitySolution | TsumeSolution


# Solver Protocol
class Solver(Protocol):
    """Protocol for all solver types."""

    def solve(self, problem: Problem) -> Solution | None:
        """Solve the given problem."""
        ...
