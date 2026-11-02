# Tic-Tac-Toe: from two players to minimax

Each step builds on the previous one. Run them in order. 


| Step | File | What is new |
|------|------|-------------|
| 1 | `forza_3.py` | Two players, row/column input, win and draw check |
| 2 | `forza_3_rand.py` | One player against a computer that picks random free cells |
| 3 | `forza_3_rand2.py` | Cells numbered 1-9, player name and sign, play again, input timeout. The computer wins or blocks when it can, otherwise random |
| 4 | `tic_tac_toe_minimax_viz.py` | The computer now plays **minimax** (never loses). Matplotlib window shows the search on the game graph |
| 5 | `website/index.html` | The same idea in the browser: no install, click to play |

When I realized that minimax was a good strategy (it never loses), I worked with Claude (Anthropic) to build the website (step 5).

```bash
python3 forza_3.py                    # 1. two players
python3 forza_3_rand.py               # 2. against random moves
python3 forza_3_rand2.py              # 3. against win/block/random
pip install matplotlib
python3 tic_tac_toe_minimax_viz.py    # 4. minimax + game graph
open website/index.html               # 5. (or double-click the file)
```

## Minimax in one paragraph

From the current board, try every move, then every reply, until the game ends.
A finished game scores `+10 - moves` for a computer win, `moves - 10` for a loss and `0` for a draw.
Scores travel back up the tree: the computer picks the highest score on its turn, the human is assumed to pick the lowest on theirs.
Faster wins score higher, so it takes a win when it can.

## Reading the game graph (steps 4 and 5)

- Each dot is a board position, each line is a move. Rotations and mirror images count as one position: 5,478 reachable boards become 765 dots.
- Colour is the result with perfect play: blue X wins, grey draw, red O wins. The empty board is grey, since perfect play always draws.
- When the computer thinks, dots light up in the order minimax finishes them: finished games first, then their parents, up to the current board.
- Lines leaving the current position are the computer's options with their scores. The thick green line is the chosen move.
- The "Show values of my moves" switch labels each free cell win / draw / lose.
