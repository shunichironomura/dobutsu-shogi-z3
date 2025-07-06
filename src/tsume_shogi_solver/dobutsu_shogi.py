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
    # Core types
    "Player",
    "PieceType",
    "PieceState",
    "PieceId",
    "Position",
    "DEFAULT_INITIAL_SETUP",
    # Problem types
    "CheckmateProblem",
    "ReachabilityProblem",
    "TsumeProblem",
    # Solution types
    "CheckmateSolution",
    "ReachabilitySolution",
    "TsumeSolution",
    # Solvers
    "CheckmateSolver",
    "ReachabilitySolver",
    "TsumeSolver",
    # Convenience functions
    "find_checkmate",
    "find_shortest_mate",
    "can_reach",
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
        raise ValueError(f"Piece {piece_id} not found in initial state")

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
        raise ValueError(f"Piece {piece_id} not found in initial state")

    problem = ReachabilityProblem(initial_state, piece_id, target, player, max_moves)
    solver = ReachabilitySolver()
    return solver.find_shortest_path(problem)


# Backward compatibility - preserve some of the original interface
class DobutsuShogiZ3:
    """Backward compatibility wrapper for the original interface."""

    def __init__(self, max_moves: int = 20, initial_setup: list[PieceState] | None = None):
        self.max_moves = max_moves
        self.initial_setup = initial_setup or DEFAULT_INITIAL_SETUP.copy()

    def solve_mate_in_n(self, n: int, winning_player: Player = Player.SENTE) -> list | None:
        """Backward compatibility method."""
        solution = find_checkmate(self.initial_setup, winning_player, n)
        return solution.moves if solution else None
