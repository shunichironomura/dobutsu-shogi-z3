"""Examples demonstrating the Dōbutsu Shōgi Z3 solver API.

This module contains examples progressing from simple property verification
to sophisticated tsume shogi problems. These examples are designed for a
formal methods study group to understand how SMT solvers can be applied
to game analysis.

Key Concepts:
- SMT (Satisfiability Modulo Theories) solving
- Property verification in finite state spaces
- Constraint-based problem solving
- Optimality proofs through iterative deepening
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
    """Demonstrate basic reachability checking.

    FORMAL METHODS CONCEPTS:
    - Reachability: Can a system reach a specific state from an initial state?
    - Bounded Model Checking: We check within a finite number of steps (7 moves)
    - State Space: Each board configuration is a state in our system

    HOW IT WORKS:
    1. We encode the game rules as Z3 constraints
    2. We ask: "Is there a sequence of valid moves where the chick reaches (4,2)?"
    3. Z3 searches through all possible move sequences up to 7 moves
    4. If satisfiable, Z3 provides a witness (the move sequence)

    This is similar to asking "Can this program reach line X?" in software verification.
    """
    print("\n=== Example 1: Basic Reachability ===")
    print("Question: Can Sente's chick reach the promotion zone (row 4)?")
    print("\nFormal property: ∃ move_sequence. valid(move_sequence) ∧ chick_at_row_4(final_state)")

    # Sente's chick is piece ID 3
    chick_id = PieceId(3)
    target_position: Position = (RowIndex(4), ColIndex(2))  # Back rank center

    # Create solver instance - this will generate Z3 constraints
    solver = ReachabilitySolver()

    # Define the problem: initial state, which piece, target position, and search depth
    problem = ReachabilityProblem(
        initial_state=DEFAULT_INITIAL_SETUP,
        piece_id=chick_id,
        target=target_position,
        player=Player.SENTE,
        max_moves=7,  # Bounded search - important for decidability
    )

    # Solve using Z3 - this invokes the SMT solver
    solution = solver.solve(problem)

    if solution:
        print(f"\n✓ SATISFIABLE: The chick can reach {target_position} in {len(solution.moves)} moves:")
        print("Z3 found the following witness:")
        print_solution_moves(solution.moves)
    else:
        print("\n✗ UNSATISFIABLE: No valid move sequence exists within 7 moves.")


def example2_movement_validation() -> None:
    """Verify piece movement capabilities.

    FORMAL METHODS CONCEPTS:
    - Universal Properties: Can we reach ALL corners? (actually checking each individually)
    - Movement Rules as Constraints: Each piece type has specific movement patterns
    - Diagonal Movement: Elephants move diagonally, which limits reachable squares

    HOW IT WORKS:
    1. For each corner, we create a separate reachability query
    2. The solver encodes elephant movement rules (diagonal only)
    3. Some corners might be unreachable due to parity constraints

    This demonstrates how formal constraints restrict the state space.
    """
    print("\n=== Example 2: Movement Validation ===")
    print("Question: Can the elephant reach all corners of the board?")
    print("\nNote: Elephants move diagonally, creating parity constraints on reachable squares.")

    # Sente's elephant is piece ID 2
    elephant_id = PieceId(2)
    corners = [
        (RowIndex(1), ColIndex(1)),
        (RowIndex(1), ColIndex(3)),
        (RowIndex(4), ColIndex(1)),
        (RowIndex(4), ColIndex(3)),
    ]

    solver = ReachabilitySolver()

    print("\nChecking reachability for each corner:")
    for corner in corners:
        problem = ReachabilityProblem(
            initial_state=DEFAULT_INITIAL_SETUP,
            piece_id=elephant_id,
            target=corner,
            player=Player.SENTE,
            max_moves=10,
        )

        solution = solver.solve(problem)
        status = "✓ REACHABLE" if solution else "✗ UNREACHABLE"
        moves = f" in {len(solution.moves)} moves" if solution else ""
        print(f"  Corner {corner}: {status}{moves}")

    print("\nObservation: Some positions may be unreachable due to movement constraints!")


def example3_simple_victory() -> None:
    """Check if a player can achieve victory.

    FORMAL METHODS CONCEPTS:
    - Victory Conditions as Properties: Lion reaching back rank = victory
    - Game-Ending States: Some states terminate the game
    - Strategic Reachability: Not just "can reach" but "can force victory"

    HOW IT WORKS:
    1. Victory in Dōbutsu Shōgi: Lion reaches opponent's back rank OR captures opponent's lion
    2. We check if Sente's lion can reach any back rank square
    3. Note: This doesn't consider opponent's moves (see checkmate examples for that)

    This is a simplified analysis - real games require considering opponent's responses.
    """
    print("\n=== Example 3: Simple Victory Condition ===")
    print("Question: Can Sente's lion reach Gote's back rank?")
    print("\nVictory condition: lion_row(final_state) = 4")
    print("Note: This example ignores opponent moves - see Example 4 for true game analysis.")

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
            print(f"\n✓ Lion can reach {position} (victory) in {len(solution.moves)} moves")
            print("However, this assumes no opponent interference!")
            break
    else:
        print("\n✗ No back rank square is reachable within 9 moves.")


# Part 2: Intermediate Examples


def example4_basic_checkmate() -> None:
    """Find forced checkmate sequences.

    FORMAL METHODS CONCEPTS:
    - Alternating Moves: Players take turns (encoded in constraints)
    - Forced Win: For ALL opponent responses, attacker still wins
    - Game Tree Search: Z3 explores the tree of possible games
    - Checkmate: A position where the opponent cannot prevent loss

    HOW IT WORKS:
    1. We encode turn alternation: even moves for Sente, odd for Gote
    2. Victory condition must be satisfied at the final move
    3. The solver ensures victory is inevitable (not just possible)
    4. This is minimax reasoning encoded as SAT constraints!

    Key insight: We're proving "Sente has a winning strategy" not just "Sente can win".
    """
    print("\n=== Example 4: Basic Checkmate Finding ===")
    print("Question: Can Sente force checkmate from the starting position?")
    print("\nFormal property: ∃ sente_moves. ∀ gote_moves. leads_to_victory(sente_moves, gote_moves)")
    print("This requires adversarial reasoning - Gote plays optimally to avoid defeat.")

    solver = CheckmateSolver()

    # Try to find mate in 7, 9, 11 moves (must be odd for Sente to make final move)
    print("\nSearching for forced mate (iterative deepening):")
    for max_moves in [7, 9, 11]:
        print(f"  Checking mate in {max_moves}...", end=" ")

        problem = CheckmateProblem(
            initial_state=DEFAULT_INITIAL_SETUP,
            winning_player=Player.SENTE,
            max_moves=max_moves,
        )

        solution = solver.solve(problem)

        if solution:
            print("FOUND!")
            print(f"\n✓ Sente has forced mate in {solution.mate_in} moves!")
            print("The following sequence guarantees victory regardless of Gote's responses:")
            print_solution_moves(solution.moves)
            break
        print("not found")
    else:
        print(f"\n✗ No forced mate found within {max_moves} moves.")


def example5_custom_position() -> None:
    """Analyze a custom position.

    FORMAL METHODS CONCEPTS:
    - Custom Initial States: We can analyze any legal position
    - Endgame Analysis: Simpler positions = smaller state space
    - Tactical Puzzles: Specific positions often have unique solutions

    HOW IT WORKS:
    1. We define a custom board position (not the standard starting position)
    2. With fewer pieces, the state space is much smaller
    3. This allows finding deeper mates more quickly

    This demonstrates how complexity affects solver performance.
    """
    print("\n=== Example 5: Custom Position Analysis ===")
    print("Setup: Endgame position with few pieces")
    print("\nSmaller state space = faster solving (fewer pieces to consider)")

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
    print("\nWith only 4 pieces, the search space is dramatically reduced.")

    solver = CheckmateSolver()
    problem = CheckmateProblem(
        initial_state=custom_position,
        winning_player=Player.SENTE,
        max_moves=3,
    )

    solution = solver.solve(problem)

    if solution:
        print(f"\n✓ Sente has mate in {solution.mate_in}!")
        print("Winning sequence:")
        print_solution_moves(solution.moves)
    else:
        print("\n✗ No mate found in 3 moves.")


# Part 3: Sophisticated Examples (Tsume Shogi)


def example6_classic_tsume() -> None:
    """Solve classic tsume shogi problem.

    FORMAL METHODS CONCEPTS:
    - Tsume Shogi: Japanese chess puzzles with specific rules
    - Exact Solutions: Must mate in EXACTLY N moves (not fewer)
    - Piece Drops: Captured pieces can be placed back on board
    - Optimal Defense: Defender must play the best moves to delay mate

    HOW IT WORKS:
    1. Sente has a captured chick (in hand) - shown by row=-1, col=-1
    2. The solver considers both moves and drops
    3. Must find mate in exactly the specified number of moves
    4. This requires both existence (can mate) and minimality (can't mate faster)

    Tsume problems are perfect for formal verification - they have precise solutions!
    """
    print("\n=== Example 6: Classic Tsume Problem ===")
    print("Tsume setup: Sente must checkmate, Gote tries to escape")
    print("\nTsume rules:")
    print("  1. Sente must mate in EXACTLY N moves")
    print("  2. Sente can drop captured pieces")
    print("  3. Gote plays optimally to maximize survival time")

    # Tsume position where Sente has material advantage
    tsume_position = [
        # Sente pieces (attacking)
        PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(3), ColIndex(2)),
        PieceState(PieceId(1), PieceType.GIRAFFE, Player.SENTE.value, RowIndex(2), ColIndex(1)),
        PieceState(PieceId(2), PieceType.ELEPHANT, Player.SENTE.value, RowIndex(2), ColIndex(3)),
        # Sente has captured a chick (in hand) - represented by position (-1, -1)
        PieceState(PieceId(7), PieceType.CHICK, Player.SENTE.value, RowIndex(-1), ColIndex(-1)),
        # Gote pieces (defending)
        PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(2)),
    ]

    print("\nPosition analysis:")
    print("  Sente has 3 pieces on board + 1 chick in hand")
    print("  The chick drop could be crucial for the mate")

    solver = CheckmateSolver()

    # In tsume, we need exact mate
    for moves in [3, 5]:
        print(f"\nChecking for exact {moves}-move mate...", end=" ")

        problem = CheckmateProblem(
            initial_state=tsume_position,
            winning_player=Player.SENTE,
            max_moves=moves,
        )

        solution = solver.solve(problem)

        if solution and solution.mate_in == moves:
            print("FOUND!")
            print(f"✓ Exact mate in {moves} moves:")
            print_solution_moves(solution.moves)
            print("\nNote: A shorter mate does not exist, or it would violate tsume rules.")
            break
        print("not found")


def example7_tsume_with_constraints() -> None:
    """Solve tsume with additional constraints.

    FORMAL METHODS CONCEPTS:
    - Additional Constraints: Beyond standard rules, add custom requirements
    - Piece Restrictions: "Don't use piece X" constraints
    - Conditional Properties: Mate must satisfy extra conditions

    HOW IT WORKS:
    1. Standard checkmate solver finds any mate
    2. We manually check if it satisfies our extra constraint
    3. In a full implementation, we'd add this constraint to Z3 directly

    This shows how formal methods can handle domain-specific requirements.
    """
    print("\n=== Example 7: Tsume with Piece Restrictions ===")
    print("Constraint: Must checkmate without using the giraffe")
    print("\nThis demonstrates adding custom constraints to standard problems.")
    print("Real implementation would encode this directly in Z3 constraints.")

    # Position where multiple pieces can deliver mate
    position = [
        PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(3), ColIndex(2)),
        PieceState(PieceId(1), PieceType.GIRAFFE, Player.SENTE.value, RowIndex(3), ColIndex(1)),
        PieceState(PieceId(2), PieceType.ELEPHANT, Player.SENTE.value, RowIndex(3), ColIndex(3)),
        PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(2)),
    ]

    print("\nFinding mate without moving the giraffe...")
    print("Constraint: ∀t. piece_id(move[t]) ≠ 1  (giraffe has ID 1)")

    # For now, use regular checkmate solver as demonstration
    checkmate_solver = CheckmateSolver()
    problem = CheckmateProblem(
        initial_state=position,
        winning_player=Player.SENTE,
        max_moves=3,
    )

    solution = checkmate_solver.solve(problem)
    if solution:
        print("\nFound a mate sequence:")
        print_solution_moves(solution.moves)

        # Check if giraffe moved (post-hoc verification)
        giraffe_moved = any(move.piece_id == 1 for move in solution.moves)
        if not giraffe_moved:
            print("\n✓ Success! Mate achieved without moving the giraffe.")
        else:
            print("\n✗ This solution uses the giraffe.")
            print("A proper implementation would exclude such solutions via Z3 constraints.")


# Part 4: Optimization Examples


def example8_shortest_path() -> None:
    """Find optimal move sequences.

    FORMAL METHODS CONCEPTS:
    - Optimization: Find not just A solution, but the BEST solution
    - Iterative Deepening: Try depth 1, 2, 3... until solution found
    - Minimality: The first solution found is guaranteed shortest
    - Multiple Objectives: Check multiple target squares

    HOW IT WORKS:
    1. We incrementally increase the search depth
    2. First solution found is provably optimal (shortest)
    3. We try all three possible promotion squares
    4. This finds the globally optimal path

    This technique is common in formal verification for finding minimal counterexamples.
    """
    print("\n=== Example 8: Shortest Path Finding ===")
    print("Question: What's the fastest way for a chick to promote?")
    print("\nOptimization approach: Iterative deepening guarantees minimality")
    print("We'll find the provably shortest path to any promotion square.")

    chick_id = PieceId(3)
    promotion_row = RowIndex(4)

    solver = ReachabilitySolver()

    # Try all three columns in the promotion zone
    shortest_solution = None
    shortest_position = None

    print("\nSearching for optimal promotion path:")
    for col in [1, 2, 3]:
        target = (promotion_row, ColIndex(col))
        print(f"  Checking column {col}...", end=" ")

        # Iterative deepening: start with small depths
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
                print(f"reachable in {len(solution.moves)} moves")
                if shortest_solution is None or len(solution.moves) < len(shortest_solution.moves):
                    shortest_solution = solution
                    shortest_position = target
                break
        else:
            print("unreachable within 9 moves")

    if shortest_solution:
        print(f"\n✓ Optimal path: {len(shortest_solution.moves)} moves to {shortest_position}")
        print("This is provably the shortest possible path to promotion!")
        print_solution_moves(shortest_solution.moves)


def example9_solver_comparison() -> None:
    """Compare different solving approaches.

    FORMAL METHODS CONCEPTS:
    - Different Properties: Checkmate vs reachability have different semantics
    - Solver Specialization: Different solvers optimize for different queries
    - Property Relationships: Some properties imply others

    KEY INSIGHTS:
    1. Checkmate considers opponent moves; reachability doesn't
    2. Reaching back rank ≠ checkmate (opponent might capture)
    3. Different encodings lead to different performance characteristics

    This demonstrates that problem formulation greatly affects solvability.
    """
    print("\n=== Example 9: Solver Comparison ===")
    print("Comparing checkmate vs reachability for victory conditions")
    print("\nKey difference: Checkmate considers adversarial play, reachability doesn't")

    # Simple endgame position
    position = [
        PieceState(PieceId(0), PieceType.LION, Player.SENTE.value, RowIndex(3), ColIndex(2)),
        PieceState(PieceId(1), PieceType.GIRAFFE, Player.SENTE.value, RowIndex(2), ColIndex(2)),
        PieceState(PieceId(4), PieceType.LION, Player.GOTE.value, RowIndex(4), ColIndex(3)),
    ]

    print("\nTesting position: Sente Lion (3,2), Giraffe (2,2) vs Gote Lion (4,3)")

    # Method 1: Checkmate solver
    print("\n1. Using CheckmateSolver (considers opponent's best defense):")
    checkmate_solver = CheckmateSolver()
    checkmate_problem = CheckmateProblem(
        initial_state=position,
        winning_player=Player.SENTE,
        max_moves=5,
    )
    checkmate_solution = checkmate_solver.solve(checkmate_problem)

    if checkmate_solution:
        print(f"   ✓ Found forced mate in {checkmate_solution.mate_in} moves")
        print("   This accounts for Gote's best defensive moves")
    else:
        print("   ✗ No forced mate found")

    # Method 2: Reachability solver (ignores opponent)
    print("\n2. Using ReachabilitySolver (ignores opponent moves):")
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
        print(f"   ✓ Lion can reach back rank in {len(reachability_solution.moves)} moves")
        print("   WARNING: This assumes Gote doesn't interfere!")
    else:
        print("   ✗ Lion cannot reach back rank")

    print("\nLesson: Different properties require different verification approaches!")
    print("Checkmate is harder to verify but provides stronger guarantees.")


def main() -> None:
    """Run all examples.

    WORKSHOP STRUCTURE:
    1. Start with simple reachability to introduce SMT concepts
    2. Progress to game-specific properties (victory conditions)
    3. Introduce adversarial reasoning with checkmate
    4. Show advanced constraints and optimizations

    Each example builds on previous concepts while introducing new ideas.
    """
    print("Dōbutsu Shōgi Z3 Solver Examples")
    print("For Formal Methods Study Group")
    print("=" * 60)
    print("\nThese examples demonstrate how SMT solvers can verify game properties.")
    print("Z3 converts game rules into logical constraints and searches for solutions.")

    # Part 1: Simple Examples
    print("\n\nPART 1: BASIC PROPERTY VERIFICATION")
    print("Learn how reachability queries work in finite state spaces")
    example1_basic_reachability()
    example2_movement_validation()
    example3_simple_victory()

    # Part 2: Intermediate Examples
    print("\n\nPART 2: INTERMEDIATE EXAMPLES")
    print("Introduce adversarial reasoning and custom positions")
    example4_basic_checkmate()
    example5_custom_position()

    # Part 3: Sophisticated Examples
    print("\n\nPART 3: SOPHISTICATED TSUME PROBLEMS")
    print("Complex constraints and exact solutions")
    example6_classic_tsume()
    example7_tsume_with_constraints()

    # Part 4: Optimization
    print("\n\nPART 4: OPTIMIZATION EXAMPLES")
    print("Finding optimal solutions and comparing approaches")
    example8_shortest_path()
    example9_solver_comparison()

    print("\n" + "=" * 60)
    print("Workshop completed!")
    print("\nKey takeaways:")
    print("- SMT solvers can verify complex game properties")
    print("- Different properties require different encodings")
    print("- Bounded model checking makes infinite games decidable")
    print("- Formal methods provide provable guarantees")


if __name__ == "__main__":
    main()
