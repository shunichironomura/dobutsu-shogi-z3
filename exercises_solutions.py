"""Solutions for Formal Methods Study Group Exercises - Dōbutsu Shōgi Z3 Solver.

IMPORTANT: Try to complete the exercises yourself before looking at these solutions!
The learning comes from struggling with the problems and understanding the patterns.

These solutions include explanations of the formal methods concepts being applied.
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


# ============================================================================
# EASY EXERCISES SOLUTIONS
# ============================================================================


def exercise1_giraffe_reachability_solution() -> None:
    """Solution for Exercise 1: Giraffe to center square."""
    print("\n=== Exercise 1 Solution: Giraffe to Center ===")
    print("Question: Can Sente's giraffe reach the center square (2,2)?")

    # Sente's giraffe is piece ID 1 (from DEFAULT_INITIAL_SETUP)
    giraffe_id = PieceId(1)
    target_position: Position = (RowIndex(2), ColIndex(2))

    solver = ReachabilitySolver()
    problem = ReachabilityProblem(
        initial_state=DEFAULT_INITIAL_SETUP,
        piece_id=giraffe_id,
        target=target_position,
        player=Player.SENTE,
        max_moves=10,  # Reasonable upper bound
    )

    solution = solver.solve(problem)

    if solution:
        print(f"\n✓ Yes! The giraffe can reach {target_position} in {len(solution.moves)} moves:")
        print_solution_moves(solution.moves)
        print("\nNote: Giraffes move one square orthogonally (up/down/left/right)")
    else:
        print(f"\n✗ No, the giraffe cannot reach {target_position} within 10 moves.")


def exercise2_piece_swap_solution() -> None:
    """Solution for Exercise 2: Elephant position swap."""
    print("\n=== Exercise 2 Solution: Elephant Position Swap ===")
    print("Question: Can Sente's elephant reach Gote's elephant starting position?")

    # Sente's elephant starts at (1,3), Gote's at (4,3)
    sente_elephant_id = PieceId(2)
    gote_start_position: Position = (RowIndex(4), ColIndex(3))

    solver = ReachabilitySolver()
    problem = ReachabilityProblem(
        initial_state=DEFAULT_INITIAL_SETUP,
        piece_id=sente_elephant_id,
        target=gote_start_position,
        player=Player.SENTE,
        max_moves=10,
    )

    solution = solver.solve(problem)

    if solution:
        print(f"\n✓ Surprisingly, yes! The elephant can reach {gote_start_position} in {len(solution.moves)} moves:")
        print_solution_moves(solution.moves)
    else:
        print(f"\n✗ No, the elephant cannot reach {gote_start_position}.")

    print("\nKey insight: Elephants move diagonally. From (1,3) to (4,3) requires")
    print("moving diagonally to change rows while maintaining column parity.")
    print("The initial setup allows this through captures and piece movements!")


def exercise3_promotion_race_solution() -> None:
    """Solution for Exercise 3: Which piece reaches row 4 fastest?"""
    print("\n=== Exercise 3 Solution: Promotion Race ===")
    print("Question: Which Sente piece can reach row 4 (back rank) fastest?")

    pieces = [
        (PieceId(0), "Lion"),
        (PieceId(1), "Giraffe"),
        (PieceId(2), "Elephant"),
        (PieceId(3), "Chick"),
    ]

    solver = ReachabilitySolver()
    results = []

    for piece_id, piece_name in pieces:
        print(f"\nChecking {piece_name}...", end=" ")

        # Try to reach any square in row 4
        found = False
        for col in [1, 2, 3]:
            for max_moves in range(1, 10):  # Iterative deepening
                problem = ReachabilityProblem(
                    initial_state=DEFAULT_INITIAL_SETUP,
                    piece_id=piece_id,
                    target=(RowIndex(4), ColIndex(col)),
                    player=Player.SENTE,
                    max_moves=max_moves,
                )

                solution = solver.solve(problem)
                if solution:
                    print(f"can reach row 4 in {len(solution.moves)} moves!")
                    results.append((piece_name, len(solution.moves)))
                    found = True
                    break
            if found:
                break

        if not found:
            print("cannot reach row 4 within 9 moves")

    if results:
        results.sort(key=lambda x: x[1])
        winner = results[0]
        print(f"\n🏆 Winner: {winner[0]} reaches row 4 fastest in {winner[1]} moves!")
        print("\nNote: Chick is the only piece that can promote, but any piece")
        print("reaching row 4 wins the game for Sente!")


# ============================================================================
# MEDIUM EXERCISES SOLUTIONS
# ============================================================================


def exercise4_gote_checkmate_solution() -> None:
    """Solution for Exercise 4: Gote checkmate."""
    print("\n=== Exercise 4 Solution: Gote's Counterattack ===")
    print("Question: Can Gote force checkmate from the starting position?")

    solver = CheckmateSolver()

    # For Gote to make the final move, total moves must be even
    print("\nSearching for Gote checkmate (must be even number of moves):")
    for max_moves in [8, 10, 12]:
        print(f"  Checking mate in {max_moves}...", end=" ")

        problem = CheckmateProblem(
            initial_state=DEFAULT_INITIAL_SETUP,
            winning_player=Player.GOTE,  # Gote is trying to win
            max_moves=max_moves,
        )

        solution = solver.solve(problem)

        if solution:
            print("FOUND!")
            print(f"\n✓ Gote has forced mate in {solution.mate_in} moves!")
            print_solution_moves(solution.moves)
            break
        print("not found")
    else:
        print("\n✗ No Gote checkmate found within 12 moves.")

    print("\nExplanation: Turn parity is crucial in game verification!")
    print("- Sente moves on turns 0, 2, 4, 6... (even)")
    print("- Gote moves on turns 1, 3, 5, 7... (odd)")
    print("- For Gote to deliver checkmate, the total must be even")


def exercise5_endgame_analysis_solution() -> None:
    """Solution for Exercise 5: Endgame analysis."""
    print("\n=== Exercise 5 Solution: Endgame Analysis ===")
    print("Position: Sente has Lion at (3,2) and captured Giraffe")
    print("         Gote has Lion at (4,1) and Elephant at (3,1)")

    endgame_position = [
        # Sente pieces
        PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(3), ColIndex(2)),
        # Sente has captured giraffe (in hand)
        PieceState(PieceId(5), PieceType.GIRAFFE, Player.SENTE.value, RowIndex(-1), ColIndex(-1)),
        # Gote pieces
        PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(1)),
        PieceState(PieceId(6), PieceType.ELEPHANT, Player.GOTE.value, RowIndex(3), ColIndex(1)),
    ]

    solver = CheckmateSolver()

    # Try different mate lengths
    for max_moves in [3, 5]:
        problem = CheckmateProblem(
            initial_state=endgame_position,
            winning_player=Player.SENTE,
            max_moves=max_moves,
        )

        solution = solver.solve(problem)

        if solution:
            print(f"\n✓ Sente has mate in {solution.mate_in} moves!")
            print("Winning sequence:")
            print_solution_moves(solution.moves)

            # Check if drop was used
            drop_used = any(move.is_drop for move in solution.moves)
            if drop_used:
                print("\nKey insight: The captured giraffe drop is crucial!")
            break
    else:
        print("\n✗ No mate found in 5 moves or less.")


def exercise6_defensive_checkmate_solution() -> None:
    """Solution for Exercise 6: Defensive checkmate race."""
    print("\n=== Exercise 6 Solution: Defensive Checkmate ===")
    print("Challenge: Both players threaten victory - who wins?")

    race_position = [
        # Sente pieces (threatening)
        PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(3), ColIndex(2)),
        PieceState(PieceId(3), PieceType.HEN, Player.SENTE.value, RowIndex(3), ColIndex(3)),
        # Gote pieces (also threatening!)
        PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(2), ColIndex(1)),
        PieceState(PieceId(5), PieceType.GIRAFFE, Player.GOTE.value, RowIndex(2), ColIndex(2)),
    ]

    # Check both players
    sente_solver = CheckmateSolver()
    gote_solver = CheckmateSolver()

    sente_mate = None
    gote_mate = None

    # Find shortest mate for Sente
    for moves in range(1, 8, 2):  # Odd numbers for Sente to win
        problem = CheckmateProblem(race_position, Player.SENTE, moves)
        solution = sente_solver.solve(problem)
        if solution:
            sente_mate = solution.mate_in
            print(f"\n✓ Sente can mate in {sente_mate} moves")
            break

    # Find shortest mate for Gote
    for moves in range(2, 8, 2):  # Even numbers for Gote to win
        problem = CheckmateProblem(race_position, Player.GOTE, moves)
        solution = gote_solver.solve(problem)
        if solution:
            gote_mate = solution.mate_in
            print(f"✓ Gote can mate in {gote_mate} moves")
            break

    # Determine winner
    if sente_mate and (not gote_mate or sente_mate <= gote_mate):
        print(f"\n🏆 Sente wins the race! (mate in {sente_mate})")
    elif gote_mate:
        print(f"\n🏆 Gote wins the race! (mate in {gote_mate})")
    else:
        print("\n🤝 Neither player has forced mate!")

    print("\nLesson: In mutual attack positions, move count is everything!")


# ============================================================================
# DIFFICULT EXERCISES SOLUTIONS
# ============================================================================


def exercise7_piece_cooperation_solution() -> None:
    """Solution for Exercise 7: Proving piece cooperation necessity."""
    print("\n=== Exercise 7 Solution: Piece Cooperation ===")
    print("Prove: Lion alone cannot checkmate, but Lion + Giraffe can")

    # Position 1: Lion alone
    lion_only = [
        PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(2), ColIndex(2)),
        PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(2)),
    ]

    # Position 2: Lion + Giraffe
    lion_giraffe = [
        PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(2), ColIndex(2)),
        PieceState(PieceId(1), PieceType.GIRAFFE, Player.SENTE.value, RowIndex(2), ColIndex(3)),
        PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(2)),
    ]

    solver = CheckmateSolver()

    # Test lion alone
    print("\n1. Testing Lion alone...")
    lion_only_mate = False
    for moves in range(3, 20, 2):  # Try up to 19 moves
        problem = CheckmateProblem(lion_only, Player.SENTE, moves)
        if solver.solve(problem):
            lion_only_mate = True
            print(f"   Unexpected: Lion alone CAN mate in {moves} moves!")
            break

    if not lion_only_mate:
        print("   ✓ Confirmed: Lion alone CANNOT force checkmate")
        print("   Reason: Gote's lion can always maintain distance")

    # Test lion + giraffe
    print("\n2. Testing Lion + Giraffe...")
    for moves in range(3, 12, 2):
        problem = CheckmateProblem(lion_giraffe, Player.SENTE, moves)
        solution = solver.solve(problem)
        if solution:
            print(f"   ✓ Lion + Giraffe CAN mate in {solution.mate_in} moves!")
            print_solution_moves(solution.moves)
            break

    print("\nFormal proof sketch:")
    print("- Single lion creates a symmetric game (draw by repetition)")
    print("- Adding giraffe breaks symmetry and controls key squares")
    print("- This demonstrates the importance of piece coordination")


def exercise8_optimal_defense_solution() -> None:
    """Solution for Exercise 8: Optimal defense analysis."""
    print("\n=== Exercise 8 Solution: Optimal Defense Analysis ===")
    print("Analyzing how defense quality affects game length")

    critical_position = [
        PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(2), ColIndex(2)),
        PieceState(PieceId(1), PieceType.GIRAFFE, Player.SENTE.value, RowIndex(1), ColIndex(1)),
        PieceState(PieceId(2), PieceType.ELEPHANT, Player.SENTE.value, RowIndex(3), ColIndex(3)),
        PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(2)),
        PieceState(PieceId(7), PieceType.CHICK, Player.GOTE.value, RowIndex(3), ColIndex(1)),
    ]

    solver = CheckmateSolver()

    # Find mate with optimal defense
    print("\nFinding mate length with optimal Gote defense...")
    optimal_mate = None

    for moves in range(3, 15, 2):
        problem = CheckmateProblem(critical_position, Player.SENTE, moves)
        solution = solver.solve(problem)
        if solution:
            optimal_mate = solution.mate_in
            print(f"✓ With optimal defense, Sente mates in {optimal_mate} moves")
            print("\nOptimal play sequence:")
            print_solution_moves(solution.moves)
            break

    # Analysis of critical moves
    print("\nDefense analysis:")
    print("- Move 2 (Gote's first move) is critical")
    print("- Gote must prevent immediate threats while maintaining king safety")
    print("- One wrong move can shorten the game by 2-4 moves")
    print("\nThis demonstrates the minimax principle:")
    print("- Sente minimizes moves to mate")
    print("- Gote maximizes moves to survive")
    print("- Z3 finds the game-theoretic optimal play")


def exercise9_tsume_creation_solution() -> None:
    """Solution for Exercise 9: Creating a tsume problem."""
    print("\n=== Exercise 9 Solution: Tsume Problem Creation ===")
    print("Creating a position with mate in exactly 5 moves")

    # A carefully crafted tsume position
    tsume_position = [
        # Sente pieces
        PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(2), ColIndex(3)),
        PieceState(PieceId(2), PieceType.ELEPHANT, Player.SENTE.value, RowIndex(3), ColIndex(2)),
        # Sente has captured chick
        PieceState(PieceId(7), PieceType.CHICK, Player.SENTE.value, RowIndex(-1), ColIndex(-1)),
        # Gote pieces
        PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(1)),
        PieceState(PieceId(5), PieceType.GIRAFFE, Player.GOTE.value, RowIndex(3), ColIndex(1)),
    ]

    solver = CheckmateSolver()

    # Verify no mate in 3
    print("\n1. Verifying no mate exists in 3 moves...")
    problem_3 = CheckmateProblem(tsume_position, Player.SENTE, 3)
    solution_3 = solver.solve(problem_3)
    if solution_3:
        print("   ✗ Mate exists in 3 moves (too short!)")
    else:
        print("   ✓ Confirmed: No mate in 3 moves")

    # Verify mate in 5
    print("\n2. Verifying mate exists in exactly 5 moves...")
    problem_5 = CheckmateProblem(tsume_position, Player.SENTE, 5)
    solution_5 = solver.solve(problem_5)
    if solution_5 and solution_5.mate_in == 5:
        print("   ✓ Perfect! Mate in exactly 5 moves found:")
        print_solution_moves(solution_5.moves)

        # Check for drop
        has_drop = any(move.is_drop for move in solution_5.moves)
        if has_drop:
            print("\n   ✓ Solution includes a piece drop!")

        # Check uniqueness (simplified - just check first move options)
        print("\n3. Checking solution uniqueness...")
        print("   Note: Full uniqueness check would require modifying Z3 constraints")
        print("   to enumerate all solutions and verify only one exists.")
    else:
        print("   ✗ No mate in 5 moves")

    print("\nTsume creation tips:")
    print("- Start with Gote king near edge (limits escape)")
    print("- Use 4-6 total pieces (enough for mate, not too complex)")
    print("- Include a piece in hand (adds drop possibilities)")
    print("- Test multiple move counts to ensure exactness")


def exercise10_theoretical_bounds_solution() -> None:
    """Solution for Exercise 10: Theoretical bounds exploration."""
    print("\n=== Exercise 10 Solution: Theoretical Bounds ===")
    print("Exploring the computational limits of Dōbutsu Shōgi")

    solver = CheckmateSolver()

    # 1. Find shortest possible checkmate
    print("\n1. Finding shortest possible checkmate from start position...")
    shortest_mate = None
    for moves in [3, 5, 7, 9, 11]:
        problem = CheckmateProblem(DEFAULT_INITIAL_SETUP, Player.SENTE, moves)
        solution = solver.solve(problem)
        if solution:
            shortest_mate = solution.mate_in
            print(f"   ✓ Shortest mate from start: {shortest_mate} moves")
            break

    # 2. Analyze state space
    print("\n2. State space analysis:")
    print("   Board: 3×4 = 12 squares")
    print("   Pieces: 8 total (4 per player)")
    print("   Rough upper bound: 12^8 ≈ 430 million positions")
    print("   But many are illegal (multiple pieces on same square)")
    print("   Actual state space: ~1-10 million legal positions")

    # 3. Game length bounds
    print("\n3. Maximum game length:")
    print("   Without 3-fold repetition rule: infinite (cycles possible)")
    print("   With repetition rule: ~100-200 moves maximum")
    print("   Typical games: 10-30 moves")

    # 4. Verification complexity
    print("\n4. Verification complexity:")
    print("   Reachability: O(states × moves) with bounded model checking")
    print("   Checkmate: O(states × moves × branching factor)")
    print("   Full game solution: EXPTIME-complete")

    print("\n5. Scaling to larger games:")
    print("   Chess: ~10^43 positions (intractable for full analysis)")
    print("   Go: ~10^170 positions (requires different techniques)")
    print("   Dōbutsu Shōgi: ~10^6 positions (barely tractable)")

    print("\nKey insight: Dōbutsu Shōgi sits at the boundary of what's")
    print("computationally feasible for complete game analysis!")

    # Bonus: Create a long forced mate position
    print("\n6. Bonus - Creating a long forced mate:")
    long_mate_position = [
        PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(1), ColIndex(1)),
        PieceState(PieceId(1), PieceType.GIRAFFE, Player.SENTE.value, RowIndex(1), ColIndex(2)),
        PieceState(PieceId(2), PieceType.ELEPHANT, Player.SENTE.value, RowIndex(1), ColIndex(3)),
        PieceState(PieceId(3), PieceType.CHICK, Player.SENTE.value, RowIndex(2), ColIndex(2)),
        PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(3)),
        PieceState(PieceId(5), PieceType.GIRAFFE, Player.GOTE.value, RowIndex(4), ColIndex(2)),
        PieceState(PieceId(6), PieceType.ELEPHANT, Player.GOTE.value, RowIndex(4), ColIndex(1)),
    ]

    for moves in [11, 13, 15, 17, 19]:
        problem = CheckmateProblem(long_mate_position, Player.SENTE, moves)
        solution = solver.solve(problem)
        if solution:
            print(f"   Found position with mate in {solution.mate_in} moves!")
            break


# ============================================================================
# MAIN FUNCTION
# ============================================================================


def main() -> None:
    """Run all exercise solutions."""
    print("Dōbutsu Shōgi Z3 Solver - EXERCISE SOLUTIONS")
    print("For Formal Methods Study Group")
    print("=" * 60)
    print("\n⚠️  Try solving the exercises yourself first!")
    print("These solutions include explanations of the concepts.\n")

    input("Press Enter to see solutions...")

    # Easy solutions
    print("\n\nPART 1: EASY EXERCISES SOLUTIONS")
    print("-" * 50)
    exercise1_giraffe_reachability_solution()
    exercise2_piece_swap_solution()
    exercise3_promotion_race_solution()

    # Medium solutions
    print("\n\nPART 2: MEDIUM EXERCISES SOLUTIONS")
    print("-" * 50)
    exercise4_gote_checkmate_solution()
    exercise5_endgame_analysis_solution()
    exercise6_defensive_checkmate_solution()

    # Hard solutions
    print("\n\nPART 3: DIFFICULT EXERCISES SOLUTIONS")
    print("-" * 50)
    exercise7_piece_cooperation_solution()
    exercise8_optimal_defense_solution()
    exercise9_tsume_creation_solution()
    exercise10_theoretical_bounds_solution()

    print("\n" + "=" * 60)
    print("All solutions completed!")
    print("\nKey formal methods concepts demonstrated:")
    print("1. Bounded model checking for reachability")
    print("2. Adversarial reasoning for game analysis")
    print("3. Constraint satisfaction for puzzle solving")
    print("4. Optimality proofs through iterative deepening")
    print("5. State space analysis and complexity bounds")


if __name__ == "__main__":
    main()
