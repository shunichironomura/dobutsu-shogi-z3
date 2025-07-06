"""Exercises for Formal Methods Study Group - Dōbutsu Shōgi Z3 Solver.

These exercises progress from simple property verification to complex game analysis.
Students should refer to examples.py for implementation patterns and concepts.

INSTRUCTIONS:
1. Complete the TODOs in each exercise
2. Run the exercise to verify your solution
3. Check that the output makes sense
4. For difficult exercises, start by understanding the simpler ones first

HINT: Most exercises follow this pattern:
1. Define the problem parameters
2. Create a solver instance
3. Set up the problem with appropriate constraints
4. Call solver.solve()
5. Process and display the results
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


# Helper function from examples.py
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
# EASY EXERCISES (Basic Reachability)
# ============================================================================


def exercise1_giraffe_reachability() -> None:
    """Exercise 1 (Easy): Can Sente's giraffe reach the center square (2,2)?.

    Goal: Learn basic reachability queries.

    Learning objectives:
    - Basic reachability queries
    - Understanding piece IDs
    - Setting up a ReachabilityProblem

    Todo:
    1. Identify the correct piece ID for Sente's giraffe (hint: check DEFAULT_INITIAL_SETUP)
    2. Define the target position as the center square
    3. Create and solve a reachability problem
    4. Print whether it's reachable and the number of moves needed

    """
    print("\n=== Exercise 1: Giraffe to Center ===")
    print("Question: Can Sente's giraffe reach the center square (2,2)?")

    # TODO: Complete this exercise
    # Hint: Sente's giraffe is piece ID 1
    # Hint: Use ReachabilitySolver and ReachabilityProblem

    # Your code here:
    # giraffe_id = PieceId(1)  # TODO: Verify this is correct
    # target_position: Position = (RowIndex(2), ColIndex(2))  # TODO: Is this the center?

    # TODO: Create solver and problem
    # solver = ReachabilitySolver()
    # problem = ReachabilityProblem(...)
    # solution = solver.solve(problem)

    print("\nTODO: Complete this exercise!")


def exercise2_piece_swap() -> None:
    """Exercise 2 (Easy): Can the two elephants swap positions?.

    Goal: Understand piece movement constraints.

    Learning objectives:
    - Multiple reachability queries
    - Understanding piece constraints
    - Comparing different scenarios

    Todo:
    1. Find where both elephants start (Sente's and Gote's)
    2. Check if Sente's elephant can reach Gote's starting position
    3. Print the result with explanation

    Think about: Why might this be impossible? (Hint: diagonal movement)

    """
    print("\n=== Exercise 2: Elephant Position Swap ===")
    print("Question: Can Sente's elephant reach Gote's elephant starting position?")

    # TODO: Complete this exercise
    # Hint: Sente's elephant is piece ID 2, starts at (1,3)
    # Hint: Gote's elephant starts at (4,3)

    print("\nTODO: Complete this exercise!")


def exercise3_promotion_race() -> None:
    """Exercise 3 (Easy-Medium): Which piece can promote fastest?.

    Goal: Compare multiple pieces and find optimal paths.

    Learning objectives:
    - Comparing multiple pieces
    - Understanding promotion rules
    - Finding optimal paths

    Todo:
    1. Check how fast each of Sente's pieces can reach row 4
    2. Compare Lion, Giraffe, Elephant, and Chick
    3. Report which piece can promote fastest

    Note: Only chicks can promote, but other pieces reaching row 4 wins the game!

    """
    print("\n=== Exercise 3: Promotion Race ===")
    print("Question: Which Sente piece can reach row 4 (back rank) fastest?")

    # TODO: Complete this exercise
    # Hint: Check pieces with IDs 0, 1, 2, 3
    # Hint: Try different max_moves values to find minimum

    print("\nTODO: Complete this exercise!")


# ============================================================================
# MEDIUM EXERCISES (Checkmate and Victory Conditions)
# ============================================================================


def exercise4_gote_checkmate() -> None:
    """Exercise 4 (Medium): Can Gote (second player) force checkmate?.

    Goal: Understand turn parity and adversarial reasoning.

    Learning objectives:
    - Checkmate from defender's perspective
    - Understanding turn parity
    - Working with CheckmateSolver

    Todo:
    1. Set up checkmate search for Gote (not Sente)
    2. Remember: Gote moves on odd turns (1, 3, 5, ...)
    3. Search for checkmate in 8, 10, 12 moves
    4. Explain why the number must be even for Gote to win

    """
    print("\n=== Exercise 4: Gote's Counterattack ===")
    print("Question: Can Gote force checkmate from the starting position?")

    # TODO: Complete this exercise
    # Hint: Use CheckmateSolver with winning_player=Player.GOTE
    # Hint: max_moves must be even for Gote to make the final move

    print("\nTODO: Complete this exercise!")


def exercise5_endgame_analysis() -> None:
    """Exercise 5 (Medium): Analyze a specific endgame position.

    Learning objectives:
    - Creating custom positions
    - Analyzing non-standard scenarios
    - Finding forced wins

    Todo:
    1. Create the given position
    2. Check if Sente has a forced mate in 5 moves or less
    3. If yes, print the winning sequence

    """
    print("\n=== Exercise 5: Endgame Analysis ===")
    print("Position: Sente has Lion at (3,2) and captured Giraffe")
    print("         Gote has Lion at (4,1) and Elephant at (3,1)")

    # Position to analyze (uncomment when implementing):
    # endgame_position = [
    #     # Sente pieces
    #     PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(3), ColIndex(2)),
    #     # Sente has captured giraffe (in hand)
    #     PieceState(PieceId(5), PieceType.GIRAFFE, Player.SENTE.value, RowIndex(-1), ColIndex(-1)),
    #     # Gote pieces
    #     PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(1)),
    #     PieceState(PieceId(6), PieceType.ELEPHANT, Player.GOTE.value, RowIndex(3), ColIndex(1)),
    # ]

    # TODO: Complete the analysis
    # Hint: Try checkmate in 3, 5 moves
    # Hint: The captured giraffe can be dropped!

    print("\nTODO: Complete this exercise!")


def exercise6_defensive_checkmate() -> None:
    """Exercise 6 (Medium-Hard): Find a defensive checkmate puzzle.

    Learning objectives:
    - Creating positions where defense leads to victory
    - Understanding tempo in games
    - Complex position evaluation

    Todo:
    1. Create a position where Gote threatens immediate victory
    2. Find if Sente can checkmate first (before Gote wins)
    3. This requires careful move counting!

    """
    print("\n=== Exercise 6: Defensive Checkmate ===")
    print("Challenge: Create a position where both players threaten victory")
    print("Can Sente win before Gote?")

    # Create a tense position (uncomment when implementing):
    # race_position = [
    #     # Sente pieces (threatening)
    #     PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(3), ColIndex(2)),
    #     PieceState(PieceId(3), PieceType.HEN, Player.SENTE.value, RowIndex(3), ColIndex(3)),  # Promoted chick
    #     # Gote pieces (also threatening!)
    #     PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(2), ColIndex(1)),
    #     PieceState(PieceId(5), PieceType.GIRAFFE, Player.GOTE.value, RowIndex(2), ColIndex(2)),
    # ]

    # TODO: Analyze who wins with perfect play
    # Hint: Check both Sente and Gote for checkmate
    # Hint: Fewer moves = wins first!

    print("\nTODO: Complete this exercise!")


# ============================================================================
# DIFFICULT EXERCISES (Advanced Constraints and Properties)
# ============================================================================


def exercise7_piece_cooperation() -> None:
    """Exercise 7 (Hard): Prove that two pieces must cooperate to win.

    Learning objectives:
    - Analyzing piece interactions
    - Understanding why single pieces can't always win
    - Proving negative properties

    Todo:
    1. Create a position with only Sente's lion and one other piece vs Gote's lion
    2. Show that lion alone cannot checkmate
    3. Show that lion + giraffe CAN checkmate
    4. Prove the giraffe is necessary

    """
    print("\n=== Exercise 7: Piece Cooperation ===")
    print("Prove: Lion alone cannot checkmate, but Lion + Giraffe can")

    # Position 1: Lion alone (uncomment when implementing)
    # lion_only = [
    #     PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(2), ColIndex(2)),
    #     PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(2)),
    # ]

    # Position 2: Lion + Giraffe (uncomment when implementing)
    # lion_giraffe = [
    #     PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(2), ColIndex(2)),
    #     PieceState(PieceId(1), PieceType.GIRAFFE, Player.SENTE.value, RowIndex(2), ColIndex(3)),
    #     PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(2)),
    # ]

    # TODO: Analyze both positions
    # TODO: Explain why cooperation is necessary

    print("\nTODO: Complete this exercise!")


def exercise8_optimal_defense() -> None:
    """Exercise 8 (Hard): Find positions requiring optimal defense.

    Learning objectives:
    - Understanding the minimax principle in practice
    - Creating positions where one wrong move loses
    - Analyzing critical positions

    Todo:
    1. Analyze the given position
    2. Show that Sente wins with perfect play
    3. Find a specific Gote move that would allow faster checkmate
    4. Explain why optimal defense matters

    """
    print("\n=== Exercise 8: Optimal Defense Analysis ===")
    print("Find how suboptimal defense changes the outcome")

    # critical_position = [
    #     PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(2), ColIndex(2)),
    #     PieceState(PieceId(1), PieceType.GIRAFFE, Player.SENTE.value, RowIndex(1), ColIndex(1)),
    #     PieceState(PieceId(2), PieceType.ELEPHANT, Player.SENTE.value, RowIndex(3), ColIndex(3)),
    #     PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(2)),
    #     PieceState(PieceId(7), PieceType.CHICK, Player.GOTE.value, RowIndex(3), ColIndex(1)),
    # ]

    # TODO: Find checkmate length with optimal defense
    # TODO: Identify which Gote moves are critical
    # TODO: Explain the minimax principle at work

    print("\nTODO: Complete this exercise!")


def exercise9_tsume_creation() -> None:
    """Exercise 9 (Very Hard): Create your own tsume problem.

    Learning objectives:
    - Understanding tsume problem constraints
    - Creating balanced puzzles
    - Verifying unique solutions

    Todo:
    1. Create a position where Sente has mate in EXACTLY 5 moves
    2. Verify no mate exists in 3 moves
    3. Ensure the solution is unique (only one winning first move)
    4. Use at least one piece drop in the solution

    """
    print("\n=== Exercise 9: Tsume Problem Creation ===")
    print("Challenge: Create a position with mate in exactly 5 moves")

    # TODO: Design your own tsume position
    # Hints:
    # - Start with few pieces (4-5 total)
    # - Give Sente a piece in hand
    # - Place Gote's lion near the edge
    # - Test that mate exists in 5 but not in 3

    # your_tsume: list[PieceState] = [
    #     # TODO: Create your position here
    # ]

    print("\nTODO: Create your own tsume problem!")


def exercise10_theoretical_bounds() -> None:
    """Exercise 10 (Research): Explore theoretical game bounds.

    Learning objectives:
    - Understanding game complexity
    - Exploring computational limits
    - Connecting to theoretical computer science

    Todo:
    1. Find the shortest possible checkmate from starting position
    2. Estimate the longest possible game (before repetition)
    3. Discuss why these bounds matter for verification
    4. What happens if we increase board size or piece count?

    """
    print("\n=== Exercise 10: Theoretical Bounds ===")
    print("Research question: What are the bounds of Dōbutsu Shōgi?")

    # TODO: Implement experiments to find:
    # 1. Shortest possible checkmate (try 3, 5, 7, 9... moves)
    # 2. Positions with longest forced mate
    # 3. Discuss state space size

    print("\nTODO: Research game theoretical bounds!")


# ============================================================================
# MAIN FUNCTION
# ============================================================================


def main() -> None:
    """Run all exercises."""
    print("Dōbutsu Shōgi Z3 Solver - EXERCISES")
    print("For Formal Methods Study Group")
    print("=" * 60)
    print("\nComplete the TODOs in each exercise.")
    print("Refer to examples.py for implementation patterns.")

    # Easy exercises
    print("\n\nPART 1: EASY EXERCISES (Basic Reachability)")
    print("-" * 50)
    exercise1_giraffe_reachability()
    exercise2_piece_swap()
    exercise3_promotion_race()

    # Medium exercises
    print("\n\nPART 2: MEDIUM EXERCISES (Checkmate and Victory)")
    print("-" * 50)
    exercise4_gote_checkmate()
    exercise5_endgame_analysis()
    exercise6_defensive_checkmate()

    # Hard exercises
    print("\n\nPART 3: DIFFICULT EXERCISES (Advanced Properties)")
    print("-" * 50)
    exercise7_piece_cooperation()
    exercise8_optimal_defense()
    exercise9_tsume_creation()
    exercise10_theoretical_bounds()

    print("\n" + "=" * 60)
    print("Exercises completed!")
    print("\nReflection questions:")
    print("1. How does bounded model checking limit what we can verify?")
    print("2. Why is checkmate harder to verify than reachability?")
    print("3. What other game properties might be interesting to verify?")
    print("4. How would this approach scale to larger games like chess?")


if __name__ == "__main__":
    main()
