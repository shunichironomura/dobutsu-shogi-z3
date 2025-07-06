# Dōbutsu Shōgi Z3 Solver - Workshop Materials

## Formal Methods Study Group

This workshop introduces formal methods concepts through game verification using the Z3 SMT solver. We analyze Dōbutsu Shōgi (Animal Chess), a simple yet rich game that's perfect for demonstrating verification techniques.

## Workshop Structure

### 1. Introduction (15 minutes)

- What is formal verification?
- SMT solvers and Z3
- Why games are good for learning formal methods
- Overview of Dōbutsu Shōgi rules

### 2. Examples Walkthrough (45 minutes)
Run and discuss `examples.py`:

```bash
uv run python examples.py
```

Key concepts covered:

- **Reachability**: Can a piece reach a specific position?
- **Bounded Model Checking**: Searching within finite steps
- **Adversarial Reasoning**: Proving forced wins
- **Optimization**: Finding shortest paths
- **Constraint Satisfaction**: Solving puzzles with specific requirements

### 3. Hands-on Exercises (60 minutes)
Students work on `exercises.py`:

```bash
uv run python exercises.py
```

Exercise difficulty levels:

- **Easy (3 exercises)**: Basic reachability queries
- **Medium (3 exercises)**: Checkmate finding and analysis
- **Hard (4 exercises)**: Advanced properties and theory

Solutions available in `exercises_solutions.py` for reference.

### 4. Discussion (30 minutes)

- How does this scale to larger games?
- What other domains can use similar techniques?
- Limitations of bounded model checking
- Connection to program verification

## Learning Objectives

By the end of this workshop, students will understand:

1. **SMT Solving**: How logical constraints encode problems
2. **Property Verification**: Different properties require different encodings
3. **State Space Analysis**: Complexity grows exponentially
4. **Adversarial Reasoning**: Minimax encoded as constraints
5. **Formal Guarantees**: Proofs vs. testing

## Key Formal Methods Concepts

### Reachability

- Question: Can state B be reached from state A?
- In games: Can a piece reach a target square?
- In programs: Can execution reach a specific line?

### Bounded Model Checking

- Explore states up to depth k
- Trade completeness for decidability
- Find bugs/solutions within bounds

### Constraint Satisfaction

- Encode rules as logical constraints
- SMT solver finds satisfying assignment
- Or proves no solution exists

### Adversarial Reasoning

- ∃ moves for player A, ∀ moves for player B
- Encode turn-taking and optimal play
- Prove inevitable outcomes

## File Descriptions

- `examples.py`: Fully explained examples with formal methods concepts
- `exercises.py`: Hands-on problems for students to solve
- `exercises_solutions.py`: Complete solutions with explanations
- `dobutsu-shogi-rules.md`: Game rules reference
- `examples_implementation_plan.md`: Design document for the examples

## Prerequisites

- Basic Python knowledge
- No prior formal methods experience required
- Interest in logic and problem solving

## Setup Instructions

1. Install UV package manager:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:

```bash
git clone https://github.com/shunichironomura/dobutsu-shogi-z3.git
cd dobutsu-shogi-z3
```

3. Install dependencies:

```bash
uv sync
```

4. Test the installation:

```bash
uv run python examples.py
```

## Workshop Tips

### For Instructors

- Start with visual demonstration of the game
- Run examples interactively, explaining output
- Encourage students to modify examples
- Discuss failed attempts and why they fail
- Connect game concepts to software verification

### For Students

- Try exercises before looking at solutions
- Experiment with different parameters
- Think about edge cases
- Ask: "What property am I trying to verify?"
- Consider computational complexity

## Extension Ideas

After the workshop, students can:

1. Add new piece types with different movements
2. Implement draw detection (repetition)
3. Create a puzzle generator
4. Analyze opening theory
5. Compare with other games (tic-tac-toe, checkers)

## Resources

- [Z3 Documentation](https://github.com/Z3Prover/z3/wiki)
- [SMT-LIB Standard](http://smtlib.cs.uiowa.edu/)
- [Dōbutsu Shōgi Rules](https://en.wikipedia.org/wiki/Dōbutsu_shōgi)
- [Formal Methods in Practice](https://formal.land/)

## Acknowledgments

This workshop demonstrates how formal methods can be applied to concrete, understandable domains. The simplicity of Dōbutsu Shōgi makes it ideal for teaching complex verification concepts.

Happy verifying! 🦁🦒🐘🐥
