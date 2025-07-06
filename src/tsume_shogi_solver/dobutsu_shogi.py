"""Dōbutsu Shōgi (Animal Chess) - Modular solver with multiple capabilities."""

from __future__ import annotations

from .solvers import CheckmateSolver, ReachabilitySolver, TsumeSolver
from .types import (
    DEFAULT_INITIAL_SETUP,
    CheckmateProblem,
    CheckmateSolution,
    PieceId,
    PieceState,
    PieceType,
    Player,
    Position,
    ReachabilityProblem,
    ReachabilitySolution,
    TsumeProblem,
    TsumeSolution,
)

__all__ = [
    # Problem types
    "CheckmateProblem",
    "CheckmateSolution",
    "CheckmateSolver",
    # Core types
    "DEFAULT_INITIAL_SETUP",
    "PieceId",
    "PieceState",
    "PieceType",
    "Player",
    "Position",
    # Reachability
    "ReachabilityProblem",
    "ReachabilitySolution",
    "ReachabilitySolver",
    # Tsume
    "TsumeProblem",
    "TsumeSolution",
    "TsumeSolver",
    # Convenience functions
    "can_reach",
    "find_checkmate",
    "find_shortest_mate",
    "find_shortest_path",
]


def find_checkmate(
    initial_state: list[PieceState],
    player: Player,
    max_moves: int,
) -> CheckmateSolution | None:
    """Find checkmate for given player within max_moves."""
    problem = CheckmateProblem(initial_state, player, max_moves)
    solver = CheckmateSolver()
    return solver.solve(problem)


def find_shortest_mate(
    initial_state: list[PieceState],
    player: Player,
    max_search: int = 15,
) -> CheckmateSolution | None:
    """Find shortest possible mate for given player."""
    problem = CheckmateProblem(initial_state, player, max_search)
    solver = CheckmateSolver()
    return solver.find_shortest_mate(problem)


def can_reach(
    initial_state: list[PieceState],
    piece_id: PieceId,
    target: Position,
    max_moves: int,
) -> ReachabilitySolution | None:
    """Check if piece can reach target position."""
    # Determine player from piece ownership
    player = None
    for piece in initial_state:
        if piece.piece_id == piece_id:
            player = Player(piece.piece_owner)
            break

    if player is None:
        msg = f"Piece {piece_id} not found in initial state"
        raise ValueError(msg)

    problem = ReachabilityProblem(initial_state, piece_id, target, player, max_moves)
    solver = ReachabilitySolver()
    return solver.solve(problem)


def find_shortest_path(
    initial_state: list[PieceState],
    piece_id: PieceId,
    target: Position,
    max_moves: int,
) -> ReachabilitySolution | None:
    """Find shortest path for piece to reach target."""
    # Determine player from piece ownership
    player = None
    for piece in initial_state:
        if piece.piece_id == piece_id:
            player = Player(piece.piece_owner)
            break

    if player is None:
        msg = f"Piece {piece_id} not found in initial state"
        raise ValueError(msg)

    problem = ReachabilityProblem(initial_state, piece_id, target, player, max_moves)
    solver = ReachabilitySolver()
    return solver.find_shortest_path(problem)
