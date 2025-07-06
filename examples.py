"""Examples demonstrating the Dōbutsu Shōgi Z3 solver API.

This module contains examples progressing from simple property verification
to sophisticated tsume shogi problems.
"""

from dobutsu_shogi_z3.constants import DEFAULT_INITIAL_SETUP
from dobutsu_shogi_z3.core import (
    ColIndex,
    MoveData,
    PieceId,
    PieceState,
    PieceType,
    Player,
    Position,
    RowIndex,
)
from dobutsu_shogi_z3.solvers.checkmate import CheckmateProblem, CheckmateSolver
from dobutsu_shogi_z3.solvers.reachability import (
    ReachabilityProblem,
    ReachabilitySolver,
)


# Helper functions
def describe_move(move: MoveData) -> str:
    """Create human-readable move description."""
    action = "drops" if move.is_drop else "moves"
    from_str = f" from {move.from_}" if not move.is_drop else ""
    capture_str = " (capture)" if move.captures >= 0 else ""
    return f"{move.player} {action} {move.piece_type.name}{from_str} to {move.to}{capture_str}"


def print_solution_moves(moves: list[MoveData]) -> None:
    """Print a sequence of moves in readable format."""
    for i, move in enumerate(moves, 1):
        print(f"  {i}. {describe_move(move)}")


# Part 1: Basic Property Verification (Simple Examples)

def example1_basic_reachability() -> None:
    """Demonstrate basic reachability checking."""
    print("\n=== Example 1: Basic Reachability ===")
    print("Question: Can Sente's chick reach the promotion zone (row 4)?")

    # Sente's chick is piece ID 3
    chick_id = PieceId(3)
    target_position: Position = (RowIndex(4), ColIndex(2))  # Back rank center

    solver = ReachabilitySolver()
    problem = ReachabilityProblem(
        initial_state=DEFAULT_INITIAL_SETUP,
        piece_id=chick_id,
        target=target_position,
        player=Player.SENTE,
        max_moves=7,
    )

    solution = solver.solve(problem)

    if solution:
        print(f"Yes! The chick can reach {target_position} in {len(solution.moves)} moves:")
        print_solution_moves(solution.moves)
    else:
        print("No, the chick cannot reach the target position within 7 moves.")


def example2_movement_validation() -> None:
    """Verify piece movement capabilities."""
    print("\n=== Example 2: Movement Validation ===")
    print("Question: Can the elephant reach all corners of the board?")

    # Sente's elephant is piece ID 2
    elephant_id = PieceId(2)
    corners = [
        (RowIndex(1), ColIndex(1)),
        (RowIndex(1), ColIndex(3)),
        (RowIndex(4), ColIndex(1)),
        (RowIndex(4), ColIndex(3)),
    ]

    solver = ReachabilitySolver()

    for corner in corners:
        problem = ReachabilityProblem(
            initial_state=DEFAULT_INITIAL_SETUP,
            piece_id=elephant_id,
            target=corner,
            player=Player.SENTE,
            max_moves=10,
        )

        solution = solver.solve(problem)
        status = "YES" if solution else "NO"
        moves = f" in {len(solution.moves)} moves" if solution else ""
        print(f"  Can reach {corner}: {status}{moves}")


def example3_simple_victory() -> None:
    """Check if a player can achieve victory."""
    print("\n=== Example 3: Simple Victory Condition ===")
    print("Question: Can Sente's lion reach Gote's back rank?")

    # Sente's lion is piece ID 0
    lion_id = PieceId(0)
    back_rank_positions = [
        (RowIndex(4), ColIndex(1)),
        (RowIndex(4), ColIndex(2)),
        (RowIndex(4), ColIndex(3)),
    ]

    solver = ReachabilitySolver()

    for position in back_rank_positions:
        problem = ReachabilityProblem(
            initial_state=DEFAULT_INITIAL_SETUP,
            piece_id=lion_id,
            target=position,
            player=Player.SENTE,
            max_moves=9,
        )

        solution = solver.solve(problem)
        if solution:
            print(f"Yes! Lion can reach {position} (victory) in {len(solution.moves)} moves")
            break
    else:
        print("No, the lion cannot reach the back rank within 9 moves.")


# Part 2: Intermediate Examples

def example4_basic_checkmate() -> None:
    """Find forced checkmate sequences."""
    print("\n=== Example 4: Basic Checkmate Finding ===")
    print("Question: Can Sente force checkmate from the starting position?")

    solver = CheckmateSolver()

    # Try to find mate in 7, 9, 11 moves
    for max_moves in [7, 9, 11]:
        problem = CheckmateProblem(
            initial_state=DEFAULT_INITIAL_SETUP,
            winning_player=Player.SENTE,
            max_moves=max_moves,
        )

        solution = solver.solve(problem)

        if solution:
            print(f"\nFound mate in {solution.mate_in} moves!")
            print_solution_moves(solution.moves)
            break
    else:
        print(f"No mate found in {max_moves} moves.")


def example5_custom_position() -> None:
    """Analyze a custom position."""
    print("\n=== Example 5: Custom Position Analysis ===")
    print("Setup: Endgame position with few pieces")

    # Custom position: Near-endgame scenario
    custom_position = [
        # Sente pieces
        PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(2), ColIndex(2)),
        PieceState(PieceId(1), PieceType.GIRAFFE, Player.SENTE.value, RowIndex(3), ColIndex(3)),
        # Gote pieces
        PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(2)),
        PieceState(PieceId(7), PieceType.CHICK, Player.GOTE.value, RowIndex(4), ColIndex(1)),
    ]

    print("\nPosition:")
    print("  Sente: Lion (2,2), Giraffe (3,3)")
    print("  Gote: Lion (4,2), Chick (4,1)")

    solver = CheckmateSolver()
    problem = CheckmateProblem(
        initial_state=custom_position,
        winning_player=Player.SENTE,
        max_moves=3,
    )

    solution = solver.solve(problem)

    if solution:
        print(f"\nSente has mate in {solution.mate_in}!")
        print_solution_moves(solution.moves)
    else:
        print("\nNo mate found in 3 moves.")


# Part 3: Sophisticated Examples (Tsume Shogi)

def example6_classic_tsume() -> None:
    """Solve classic tsume shogi problem."""
    print("\n=== Example 6: Classic Tsume Problem ===")
    print("Tsume setup: Sente must checkmate, Gote tries to escape")

    # Tsume position where Sente has material advantage
    tsume_position = [
        # Sente pieces (attacking)
        PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(3), ColIndex(2)),
        PieceState(PieceId(1), PieceType.GIRAFFE, Player.SENTE.value, RowIndex(2), ColIndex(1)),
        PieceState(PieceId(2), PieceType.ELEPHANT, Player.SENTE.value, RowIndex(2), ColIndex(3)),
        # Sente has captured a chick (in hand)
        PieceState(PieceId(7), PieceType.CHICK, Player.SENTE.value, RowIndex(-1), ColIndex(-1)),
        # Gote pieces (defending)
        PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(2)),
    ]

    solver = CheckmateSolver()

    # In tsume, we need exact mate
    for moves in [3, 5]:
        problem = CheckmateProblem(
            initial_state=tsume_position,
            winning_player=Player.SENTE,
            max_moves=moves,
        )

        solution = solver.solve(problem)

        if solution and solution.mate_in == moves:
            print(f"\nFound exact mate in {moves}!")
            print_solution_moves(solution.moves)
            break


def example7_tsume_with_constraints() -> None:
    """Solve tsume with additional constraints."""
    print("\n=== Example 7: Tsume with Piece Restrictions ===")
    print("Constraint: Must checkmate without using the giraffe")

    # Position where multiple pieces can deliver mate
    position = [
        PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(3), ColIndex(2)),
        PieceState(PieceId(1), PieceType.GIRAFFE, Player.SENTE.value, RowIndex(3), ColIndex(1)),
        PieceState(PieceId(2), PieceType.ELEPHANT, Player.SENTE.value, RowIndex(3), ColIndex(3)),
        PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(2)),
    ]

    # Create constraint: Giraffe must not move
    # This is a simplified example - real implementation would need proper constraint generation
    print("\nFinding mate without moving the giraffe...")

    # For now, use regular checkmate solver as demonstration
    checkmate_solver = CheckmateSolver()
    problem = CheckmateProblem(
        initial_state=position,
        winning_player=Player.SENTE,
        max_moves=3,
    )

    solution = checkmate_solver.solve(problem)
    if solution:
        print("Found a mate sequence:")
        print_solution_moves(solution.moves)

        # Check if giraffe moved
        giraffe_moved = any(
            move.piece_id == 1 for move in solution.moves
        )
        if not giraffe_moved:
            print("Success! Mate achieved without moving the giraffe.")
        else:
            print("This solution uses the giraffe.")


# Part 4: Optimization Examples

def example8_shortest_path() -> None:
    """Find optimal move sequences."""
    print("\n=== Example 8: Shortest Path Finding ===")
    print("Question: What's the fastest way for a chick to promote?")

    chick_id = PieceId(3)
    promotion_row = RowIndex(4)

    solver = ReachabilitySolver()

    # Try all three columns in the promotion zone
    shortest_solution = None
    shortest_position = None

    for col in [1, 2, 3]:
        target = (promotion_row, ColIndex(col))

        # Use find_shortest_path method
        for max_moves in range(3, 10):
            problem = ReachabilityProblem(
                initial_state=DEFAULT_INITIAL_SETUP,
                piece_id=chick_id,
                target=target,
                player=Player.SENTE,
                max_moves=max_moves,
            )

            solution = solver.solve(problem)

            if solution:
                if shortest_solution is None or len(solution.moves) < len(shortest_solution.moves):
                    shortest_solution = solution
                    shortest_position = target
                break

    if shortest_solution:
        print(f"\nShortest path to promotion: {len(shortest_solution.moves)} moves to {shortest_position}")
        print_solution_moves(shortest_solution.moves)


def example9_solver_comparison() -> None:
    """Compare different solving approaches."""
    print("\n=== Example 9: Solver Comparison ===")
    print("Comparing checkmate vs reachability for victory conditions")

    # Simple endgame position
    position = [
        PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(3), ColIndex(2)),
        PieceState(PieceId(1), PieceType.GIRAFFE, Player.SENTE.value, RowIndex(2), ColIndex(2)),
        PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(3)),
    ]

    print("\nTesting position: Sente Lion (3,2), Giraffe (2,2) vs Gote Lion (4,3)")

    # Method 1: Checkmate solver
    print("\n1. Using CheckmateSolver:")
    checkmate_solver = CheckmateSolver()
    checkmate_problem = CheckmateProblem(
        initial_state=position,
        winning_player=Player.SENTE,
        max_moves=5,
    )
    checkmate_solution = checkmate_solver.solve(checkmate_problem)

    if checkmate_solution:
        print(f"   Found mate in {checkmate_solution.mate_in} moves")
    else:
        print("   No mate found")

    # Method 2: Reachability solver (lion to back rank)
    print("\n2. Using ReachabilitySolver (lion to back rank):")
    reachability_solver = ReachabilitySolver()
    reachability_problem = ReachabilityProblem(
        initial_state=position,
        piece_id=PieceId(0),
        target=(RowIndex(4), ColIndex(2)),
        player=Player.SENTE,
        max_moves=5,
    )
    reachability_solution = reachability_solver.solve(reachability_problem)

    if reachability_solution:
        print(f"   Lion can reach back rank in {len(reachability_solution.moves)} moves")
    else:
        print("   Lion cannot reach back rank")

    print("\nAnalysis: Different solvers reveal different aspects of the position")


def main() -> None:
    """Run all examples."""
    print("Dōbutsu Shōgi Z3 Solver Examples")
    print("=" * 60)

    # Part 1: Simple Examples
    print("\nPART 1: BASIC PROPERTY VERIFICATION")
    example1_basic_reachability()
    example2_movement_validation()
    example3_simple_victory()

    # Part 2: Intermediate Examples
    print("\n\nPART 2: INTERMEDIATE EXAMPLES")
    example4_basic_checkmate()
    example5_custom_position()

    # Part 3: Sophisticated Examples
    print("\n\nPART 3: SOPHISTICATED TSUME PROBLEMS")
    example6_classic_tsume()
    example7_tsume_with_constraints()

    # Part 4: Optimization
    print("\n\nPART 4: OPTIMIZATION EXAMPLES")
    example8_shortest_path()
    example9_solver_comparison()

    print("\n" + "=" * 60)
    print("Examples completed!")


if __name__ == "__main__":
    main()
