# Task List for Claude Code

## How to use this file
This file is a task list for Claude Code (claude.ai/code) to follow when working on the Dōbutsu Shōgi (Animal Chess) project. It outlines the tasks that need to be completed, including reading rules, implementing tests, and ensuring code quality.

When you complete a task, check the box next to it, i.e., change `- [ ]` to `- [x]`. This helps track progress and ensures that all tasks are addressed.

When you add a new task, use the format `- [ ] Task description`. This keeps the task list organized and easy to read.

Tasks are sorted by logical order, so please follow the sequence to ensure a smooth workflow.

## Tasks

- [x] Read the rules of Dōbutsu Shōgi (Animal Chess) written in dobutsu-shogi-rules.md and confirm it is correct.
- [x] Implement pytest cases for the rules. DO NOT use class based tests, use pytest fixtures and functions.
- [x] Use defined type for initial board state setup. The initial implementation is done in `PieceState` class, so proceed with that.
- [ ] I don't like some of the variables are structured as nested dictionaries, so refactor the code to use flat dictionaries with tuple keys.
- [ ] Refactor the code so that users can easily use it for various purposes, such as proving a checkmate (Tsume), proving a reachability of a piece to a cell, or solving a Tsume Shogi problem.
