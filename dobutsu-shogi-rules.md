# 📘 Dōbutsu Shogi Comprehensive Rules (LLM-Friendly Markdown)

## 🎯 Overview

Dōbutsu Shogi is a simplified version of Shogi (Japanese chess), designed for educational and introductory purposes. The board is smaller, with simpler rules, but it retains key strategic elements like promotion, capturing, and winning through checkmate or capture of the opponent’s lion.

## 🧩 Game Components

📏 Board
 • Size: 3 rows × 4 columns (3×4 grid)
 • Orientation: Each player sees their Lion on the bottom row.

## ♟ Pieces

Each player has 4 pieces:

Piece Symbol Moves Promotes Representation
🦁 Lion L 1 square in any direction No King
🐘 Elephant E Diagonal only No Bishop-like
🐓 Chick → Hen C → H Forward 1 (C) → all directions except diagonals back (H) Yes Pawn → Gold
🐦 Giraffe G Orthogonal (up, down, left, right) No Rook-like

Total pieces on board: 8 (4 per player)

## 🧑‍🤝‍🧑 Setup

Each player’s starting position (from bottom to top):

Rank Column 1 Column 2 Column 3 Column 4
P2 (opponent) G L E
P2 (opponent)  C
P1 (you)  C
P1 (you) E L G

Note: Pieces are rotated 180° to indicate opponent’s ownership.

## 🕹️ Turn Order
 • Players alternate turns.
 • On your turn, you must either:

 1. Move a piece already on the board.
 2. Drop a captured piece back onto the board.

## 🔀 Piece Movement Rules

🦁 Lion
 • Moves: 1 square in any direction
 • Cannot promote

🐘 Elephant
 • Moves: 1 square diagonally
 • Cannot promote

🐦 Giraffe
 • Moves: 1 square orthogonally (up, down, left, right)
 • Cannot promote

🐣 Chick → 🐓 Hen
 • Chick moves: 1 square forward
 • Hen (promoted chick) moves: 1 square any direction except diagonally backward
 • Chick promotes to Hen when it moves into or inside the opponent’s back row (3rd row from the player)

## 🪙 Captures
 • When a piece moves to a square occupied by an enemy piece, the enemy piece is captured and goes into the capturing player’s hand.
 • Captured pieces lose promotion status (e.g., Hen becomes Chick).
 • Captured pieces can be dropped back on any empty square as the player’s own.

## 🔁 Dropping Rules
 • You may drop a captured piece from your hand onto any empty square, as your turn.
 • You cannot drop a Chick that would immediately checkmate the opponent’s Lion. (This is called the Chick-drop mate prohibition.)

## 📈 Promotion Rules
 • A Chick must promote to Hen if:
 • It moves into, within, or out of the furthest row from the owner (i.e., the opponent’s home row).
 • Promotion is automatic and irreversible.

## 🏁 Win Conditions

A player wins the game in either of the following ways:

1. Lion Capture
 • You capture the opponent’s Lion.

2. Try Rule (Lion Escape)
 • You move your Lion into the opponent’s back row, and the opponent cannot capture or block it on their next move.
 • This counts as a victory by Try.

## ⚠️ Special Restrictions
 • 🐣 Chick-Drop Checkmate is Forbidden: You may not drop a Chick in a way that delivers immediate checkmate.
 • 🦁 Lions may face each other on adjacent squares, but a player can move the Lion to check as long as it isn’t immediately capturable.

## 💡 Example: Legal Moves Summary (per piece)

{
  "Lion": ["up", "down", "left", "right", "up-left", "up-right", "down-left", "down-right"],
  "Elephant": ["up-left", "up-right", "down-left", "down-right"],
  "Giraffe": ["up", "down", "left", "right"],
  "Chick": ["up"],
  "Hen": ["up", "down", "left", "right", "up-left", "up-right"]
}

## 🧾 External References
 • Wikipedia: [どうぶつしょうぎ](https://ja.wikipedia.org/wiki/%E3%81%A9%E3%81%86%E3%81%B6%E3%81%A4%E3%81%97%E3%82%87%E3%81%86%E3%81%8E)
 • English Overview: <https://en.wikipedia.org/wiki/Dōbutsu_shōgi>
