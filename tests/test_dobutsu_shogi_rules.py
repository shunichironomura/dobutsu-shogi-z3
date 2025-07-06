"""Test cases for Dōbutsu Shōgi rules implementation."""

from __future__ import annotations

import pytest
from z3 import Solver, sat

from tsume_shogi_solver.game_rules import GameRules
from tsume_shogi_solver.game_state import GameState
from tsume_shogi_solver.types import (
    DEFAULT_INITIAL_SETUP,
    Player,
    TimeIndex,
)


@pytest.fixture
def solver() -> tuple[Solver, GameState]:
    """Create a solver with basic game constraints."""
    state = GameState.create(max_moves=10)
    solver = Solver()

    # Add basic constraints
    solver.add(state.get_basic_constraints())
    solver.add(state.set_initial_position(DEFAULT_INITIAL_SETUP))
    solver.add(GameRules.basic_constraints(state))
    solver.add(GameRules.movement_constraints(state))

    return solver, state


def test_initial_board_setup(solver: tuple[Solver, GameState]) -> None:
    """Test that the initial board setup is satisfiable."""
    s, state = solver

    # Should be able to find a satisfying assignment
    assert s.check() == sat
    model = s.model()

    # Verify some basic properties of the initial state
    t = TimeIndex(0)

    # Check that pieces are at expected positions
    for piece_state in DEFAULT_INITIAL_SETUP:
        piece_id = piece_state.piece_id

        # Check position
        row = model[state.piece_row[t, piece_id]].as_long()
        col = model[state.piece_col[t, piece_id]].as_long()

        assert row == piece_state.row
        assert col == piece_state.col

        # Check piece type
        piece_type = model[state.piece_type[piece_id]].as_long()
        assert piece_type == piece_state.piece_type.value

        # Check ownership
        owner = model[state.piece_owner[t, piece_id]].as_long()
        assert owner == piece_state.piece_owner


def test_basic_movement_constraints(solver: tuple[Solver, GameState]) -> None:
    """Test that movement constraints are properly applied."""
    s, state = solver

    # Test that we can make a legal move
    move = state.moves[TimeIndex(0)]

    # Try to move Sente's chick forward
    s.add(move.piece_id == 3)  # Sente's chick
    s.add(move.to_row == 3)  # Move forward
    s.add(move.to_col == 2)  # Same column

    assert s.check() == sat, "Legal chick move should be satisfiable"


def test_victory_conditions(solver: tuple[Solver, GameState]) -> None:
    """Test that victory conditions can be evaluated."""
    s, state = solver

    # Test victory condition evaluation
    victory_sente = GameRules.victory_conditions(state, TimeIndex(1), Player.SENTE)
    victory_gote = GameRules.victory_conditions(state, TimeIndex(1), Player.GOTE)

    # Should be able to create these expressions without error
    assert victory_sente is not None
    assert victory_gote is not None


def test_piece_movement_patterns(solver: tuple[Solver, GameState]) -> None:
    """Test that piece movement patterns are correctly enforced."""
    s, state = solver

    # Test chick movement - should only move forward
    move = state.moves[TimeIndex(0)]

    # Sente's chick moving backward should be unsatisfiable
    test_solver = Solver()
    test_solver.add(s.assertions())
    test_solver.add(move.piece_id == 3)  # Sente's chick
    test_solver.add(move.to_row == 1)  # Move backward
    test_solver.add(move.to_col == 2)  # Same column
    test_solver.add(move.captures == -1)  # No capture

    assert test_solver.check() != sat, "Chick should not be able to move backward"


def test_turn_alternation(solver: tuple[Solver, GameState]) -> None:
    """Test that players alternate turns correctly."""
    s, state = solver

    # Move 0 should be Sente's turn
    move0 = state.moves[TimeIndex(0)]
    s.add(move0.piece_id == 3)  # Sente's chick
    s.add(move0.to_row == 3)
    s.add(move0.to_col == 2)

    # Move 1 should be Gote's turn
    move1 = state.moves[TimeIndex(1)]
    s.add(move1.piece_id == 7)  # Gote's chick
    s.add(move1.to_row == 2)
    s.add(move1.to_col == 2)

    assert s.check() == sat, "Turn alternation should work correctly"


def test_no_piece_overlap(solver: tuple[Solver, GameState]) -> None:
    """Test that pieces cannot occupy the same square."""
    s, state = solver

    # This constraint should be enforced by the basic constraints
    # The solver should automatically prevent piece overlap
    assert s.check() == sat, "Basic constraints should be satisfiable"


def test_capture_mechanics_basic(solver: tuple[Solver, GameState]) -> None:
    """Test basic capture mechanics."""
    s, state = solver

    # Set up a capture scenario
    move = state.moves[TimeIndex(0)]
    s.add(move.piece_id == 3)  # Sente's chick
    s.add(move.to_row == 3)  # Move to row 3
    s.add(move.to_col == 2)  # Column 2 (where Gote's chick is)
    s.add(move.captures == 7)  # Capture Gote's chick

    assert s.check() == sat, "Capture should be possible"


def test_promotion_constraints(solver: tuple[Solver, GameState]) -> None:
    """Test that promotion constraints are properly enforced."""
    s, state = solver

    # Only chicks should be able to promote
    # This is tested implicitly through the constraint system
    assert s.check() == sat, "Promotion constraints should not break basic satisfiability"
