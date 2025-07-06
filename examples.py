"""Examples demonstrating the new modular Dōbutsu Shōgi solver."""

from tsume_shogi_solver import (
    DEFAULT_INITIAL_SETUP,
    CheckmateProblem,
    CheckmateSolver,
    PieceId,
    PieceState,
    PieceType,
    Player,
    ReachabilityProblem,
    ReachabilitySolver,
    TsumeProblem,
    TsumeSolver,
    can_reach,
    find_checkmate,
    find_shortest_mate,
    find_shortest_path,
)
from tsume_shogi_solver.types import ColIndex, RowIndex


def example_checkmate_solving():
    """Example 1: Find checkmate using the new solver."""
    print("=== Example 1: Checkmate Solving ===")

    # Method 1: Using convenience function
    print("\n1. Using convenience function:")
    solution = find_checkmate(DEFAULT_INITIAL_SETUP, Player.SENTE, 7)

    if solution:
        print(f"Found mate in {solution.mate_in} moves for {solution.winning_player.name}!")
        for move in solution.moves:
            print(
                f"  Move {move.move_number + 1} ({move.player}): {move.piece_type.name} from {move.from_} to {move.to}",
            )
    else:
        print("No mate found (expected - Gote has winning strategy)")

    # Method 2: Using solver directly
    print("\n2. Using solver directly:")
    solver = CheckmateSolver()
    problem = CheckmateProblem(DEFAULT_INITIAL_SETUP, Player.SENTE, 7)
    solution = solver.solve(problem)

    if solution:
        print(f"Found mate in {solution.mate_in} moves!")
    else:
        print("No mate found")

    # Method 3: Find shortest mate
    print("\n3. Finding shortest mate:")
    shortest = find_shortest_mate(DEFAULT_INITIAL_SETUP, Player.SENTE, 15)
    if shortest:
        print(f"Shortest mate: {shortest.mate_in} moves")
    else:
        print("No mate found within search limit")


def example_reachability_analysis():
    """Example 2: Prove piece reachability."""
    print("\n=== Example 2: Reachability Analysis ===")

    # Can Sente's chick reach the back rank?
    chick_id = PieceId(3)  # Sente's chick
    target_position = (4, 2)  # Back rank, center

    print(f"\nCan Sente's chick (piece {chick_id}) reach position {target_position}?")

    # Method 1: Using convenience function
    solution = can_reach(DEFAULT_INITIAL_SETUP, chick_id, target_position, 10)

    if solution:
        print(f"Yes! Can reach in {len(solution.moves)} moves:")
        for move in solution.moves:
            print(f"  Move {move.move_number + 1}: {move.piece_type.name} from {move.from_} to {move.to}")
    else:
        print("Cannot reach target position")

    # Method 2: Find shortest path
    print(f"\nFinding shortest path to {target_position}:")
    shortest_path = find_shortest_path(DEFAULT_INITIAL_SETUP, chick_id, target_position, 10)

    if shortest_path:
        print(f"Shortest path: {len(shortest_path.moves)} moves")
    else:
        print("No path found")


def example_custom_position():
    """Example 3: Custom position analysis."""
    print("\n=== Example 3: Custom Position Analysis ===")

    # Create a custom position where Sente has a quick mate
    custom_position = [
        # Sente pieces
        PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(2), ColIndex(2)),
        PieceState(PieceId(1), PieceType.GIRAFFE, Player.SENTE.value, RowIndex(3), ColIndex(2)),
        # Gote pieces
        PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(2)),
        PieceState(PieceId(5), PieceType.CHICK, Player.GOTE.value, RowIndex(4), ColIndex(1)),
    ]

    print("\nCustom position setup:")
    print("Sente Lion at (2,2), Giraffe at (3,2)")
    print("Gote Lion at (4,2), Chick at (4,1)")

    # Try to find mate for Sente
    solution = find_checkmate(custom_position, Player.SENTE, 3)

    if solution:
        print(f"\nFound mate in {solution.mate_in} moves!")
        for move in solution.moves:
            action = "Drop" if move.is_drop else "Move"
            capture = " (captures)" if move.captures >= 0 else ""
            print(f"  {action} {move.piece_type.name} from {move.from_} to {move.to}{capture}")
    else:
        print("\nNo mate found in 3 moves")


def example_tsume_solver():
    """Example 4: General Tsume solver."""
    print("\n=== Example 4: General Tsume Solver ===")

    # Create a custom problem with specific constraints
    solver = TsumeSolver()

    # For this example, we'll create a problem that just needs to satisfy
    # basic game rules (no additional constraints)
    problem = TsumeProblem(
        initial_state=DEFAULT_INITIAL_SETUP,
        constraints=[],  # No additional constraints
        max_moves=5,
    )

    print("Solving general Tsume problem...")
    solution = solver.solve(problem)

    if solution:
        print(f"Found solution in {len(solution.moves)} moves!")
        for move in solution.moves:
            print(f"  Move {move.move_number + 1}: {move.piece_type.name} from {move.from_} to {move.to}")
    else:
        print("No solution found")


def example_solver_comparison():
    """Example 5: Compare different solver approaches."""
    print("\n=== Example 5: Solver Comparison ===")

    # Test the same position with different solvers
    print("\nTesting same position with different solvers:")

    # Checkmate solver
    checkmate_solver = CheckmateSolver()
    checkmate_problem = CheckmateProblem(DEFAULT_INITIAL_SETUP, Player.SENTE, 5)
    checkmate_result = checkmate_solver.solve(checkmate_problem)

    print(f"Checkmate solver: {'Found' if checkmate_result else 'Not found'}")

    # Reachability solver - can any piece reach opponent's back rank?
    reachability_solver = ReachabilitySolver()
    for piece_id in [PieceId(0), PieceId(1), PieceId(2), PieceId(3)]:  # Sente pieces
        reachability_problem = ReachabilityProblem(
            DEFAULT_INITIAL_SETUP,
            piece_id,
            (4, 2),
            Player.SENTE,
            5,
        )
        reachability_result = reachability_solver.solve(reachability_problem)

        piece_type = next(p.piece_type for p in DEFAULT_INITIAL_SETUP if p.piece_id == piece_id)
        print(
            f"Reachability solver - {piece_type.name}: {'Can reach' if reachability_result else 'Cannot reach'} (4,2)",
        )

    # General Tsume solver
    tsume_solver = TsumeSolver()
    tsume_problem = TsumeProblem(DEFAULT_INITIAL_SETUP, [], 5)
    tsume_result = tsume_solver.solve(tsume_problem)

    print(f"General Tsume solver: {'Found solution' if tsume_result else 'No solution'}")


if __name__ == "__main__":
    print("Dōbutsu Shōgi Solver Examples")
    print("=" * 50)

    # Run all examples
    example_checkmate_solving()
    example_reachability_analysis()
    example_custom_position()
    example_tsume_solver()
    example_solver_comparison()

    print("\n" + "=" * 50)
    print("Examples completed!")
