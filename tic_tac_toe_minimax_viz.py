"""
Play tic-tac-toe against minimax and watch the search on the game graph.

Left:  the board. Click a cell to play.
Right: the tic-tac-toe game graph (765 positions up to symmetry).
       - Faint dots: positions the current search has not reached.
       - When the computer thinks, the positions it evaluates light up in the
         order minimax *finishes* them: leaves first, then their parents,
         as the values are backed up the tree.
       - Colour = value with perfect play: blue X wins, grey draw, red O wins.
       - Coloured edges from the current position: the computer's options,
         labelled with its scores; the thick green edge is the move it chose.
       - Black line: the game played so far.

Buttons: new game as X or as O, and a toggle that shows, on the board,
what each of your moves is worth (win / draw / lose with perfect play).

Usage:  python tic_tac_toe_minimax_viz.py
Needs:  matplotlib  (pip install matplotlib)
"""
import os
import random
from functools import lru_cache

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.widgets import Button

ANIMATE = os.environ.get("TTT_NO_ANIMATION") is None
ANIMATION_FRAMES = 45          # more frames = slower, smoother animation
FRAME_PAUSE = 0.03             # seconds per frame

LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
         (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]

BLUE, GREY, RED, GREEN = "#2457A6", "#8C8C8C", "#B5283A", "#2E8B2E"
FAINT = (0.85, 0.85, 0.85, 0.6)
VALUE_COLOUR = {1: BLUE, 0: GREY, -1: RED}


# ---------------------------------------------------------------- game logic
def _rot(p):
    return tuple(p[i] for i in (6, 3, 0, 7, 4, 1, 8, 5, 2))


def _flip(p):
    return tuple(p[i] for i in (2, 1, 0, 5, 4, 3, 8, 7, 6))


SYMMETRIES = []
_p = tuple(range(9))
for _ in range(4):
    SYMMETRIES += [_p, _flip(_p)]
    _p = _rot(_p)


@lru_cache(maxsize=None)
def canonical(b):
    """Representative of the board up to rotations and reflections."""
    return min("".join(b[i] for i in s) for s in SYMMETRIES)


def winner(b):
    for line in LINES:
        a, c, d = line
        if b[a] != "." and b[a] == b[c] == b[d]:
            return b[a], line
    return None, None


def is_over(b):
    return winner(b)[0] is not None or "." not in b


def to_move(b):
    return "X" if b.count("X") == b.count("O") else "O"


def children(b):
    p = to_move(b)
    return [(i, b[:i] + p + b[i + 1:]) for i in range(9) if b[i] == "."]


@lru_cache(maxsize=None)
def value(b):
    """Minimax value from X's point of view: +1 X wins, 0 draw, -1 O wins."""
    w, _ = winner(b)
    if w:
        return 1 if w == "X" else -1
    if "." not in b:
        return 0
    vals = [value(c) for _, c in children(b)]
    return max(vals) if to_move(b) == "X" else min(vals)


@lru_cache(maxsize=None)
def tree_size(b):
    """Number of nodes a plain (non-memoised) minimax visits below b."""
    if is_over(b):
        return 1
    return 1 + sum(tree_size(c) for _, c in children(b))


# --------------------------------------------------------------- the graph
def build_graph():
    start = canonical("." * 9)
    levels, edges, seen = [[start]], set(), {start}
    for depth in range(9):
        nxt = []
        for b in levels[depth]:
            if is_over(b):
                continue
            for _, c in children(b):
                c = canonical(c)
                edges.add((b, c))
                if c not in seen:
                    seen.add(c)
                    nxt.append(c)
        if not nxt:
            break
        levels.append(nxt)

    parents = {}
    for a, c in edges:
        parents.setdefault(c, []).append(a)
    pos = {}
    for d, lvl in enumerate(levels):
        ordered = lvl if d == 0 else sorted(
            lvl, key=lambda b: (sum(pos[p][0] for p in parents[b]) / len(parents[b]), value(b)))
        for k, b in enumerate(ordered):
            pos[b] = ((k + 0.5) / len(ordered), -d)
    return levels, edges, pos


# ---------------------------------------------------------------- the app
class App:
    def __init__(self):
        self.levels, self.edges, self.pos = build_graph()
        self.nodes = [b for lvl in self.levels for b in lvl]
        self.index = {b: k for k, b in enumerate(self.nodes)}
        self.show_values = False
        self.busy = False

        self.fig = plt.figure(figsize=(17, 9.5))
        try:
            self.fig.canvas.manager.set_window_title("Tic-tac-toe: minimax on the game graph")
        except AttributeError:
            pass

        # ---- graph panel
        g = self.ax_graph = self.fig.add_axes([0.34, 0.04, 0.65, 0.9])
        segs = [[self.pos[a], self.pos[c]] for a, c in self.edges]
        g.add_collection(LineCollection(segs, colors="black", linewidths=0.15, alpha=0.18, zorder=1))
        xs = [self.pos[b][0] for b in self.nodes]
        ys = [self.pos[b][1] for b in self.nodes]
        self.colours = [FAINT] * len(self.nodes)
        self.sizes = [8] * len(self.nodes)
        self.scatter = g.scatter(xs, ys, s=self.sizes, c=self.colours, zorder=2, linewidths=0)
        self.option_lines = LineCollection([], zorder=3)
        g.add_collection(self.option_lines)
        self.option_texts = []
        (self.path_line,) = g.plot([], [], color="black", lw=2.4, zorder=4, solid_capstyle="round")
        self.current = g.scatter([], [], s=230, facecolors="none", edgecolors="black",
                                 linewidths=2.2, zorder=5)
        g.set_xlim(-0.01, 1.01)
        g.set_ylim(-len(self.levels) + 0.4, 0.6)
        g.set_yticks([-d for d in range(len(self.levels))])
        g.set_yticklabels([f"move {d}" for d in range(len(self.levels))])
        g.set_xticks([])
        for s in ("top", "right", "bottom"):
            g.spines[s].set_visible(False)
        g.set_title(f"Game graph: {len(self.nodes)} positions up to symmetry, "
                    f"{len(self.edges)} moves", fontsize=12)
        for v, lab in ((1, "X wins"), (0, "draw"), (-1, "O wins")):
            g.scatter([], [], color=VALUE_COLOUR[v], s=30, label=lab)
        g.scatter([], [], color=FAINT, s=30, label="not searched (this move)")
        g.legend(loc="lower right", title="value with perfect play", fontsize=9)

        # ---- board panel
        bx = self.ax_board = self.fig.add_axes([0.03, 0.32, 0.27, 0.48])
        bx.set_xlim(0, 3)
        bx.set_ylim(0, 3)
        bx.set_aspect("equal")
        bx.axis("off")
        for k in (1, 2):
            bx.plot([k, k], [0, 3], color="black", lw=2)
            bx.plot([0, 3], [k, k], color="black", lw=2)
        self.cell_texts, self.hint_texts = [], []
        for i in range(9):
            x, y = i % 3 + 0.5, 2 - i // 3 + 0.5
            self.cell_texts.append(bx.text(x, y, "", ha="center", va="center",
                                           fontsize=46, fontweight="bold"))
            self.hint_texts.append(bx.text(x, y - 0.33, "", ha="center", va="center", fontsize=10))
        (self.win_line,) = bx.plot([], [], color=GREEN, lw=6, alpha=0.7)

        self.info = self.fig.text(0.165, 0.915, "", ha="center", va="center", fontsize=10)
        self.status = self.fig.text(0.165, 0.835, "", ha="center", va="center",
                                    fontsize=14, fontweight="bold")

        # ---- buttons
        self.b_x = Button(self.fig.add_axes([0.03, 0.2, 0.13, 0.06]), "New game: I'm X")
        self.b_o = Button(self.fig.add_axes([0.17, 0.2, 0.13, 0.06]), "New game: I'm O")
        self.b_v = Button(self.fig.add_axes([0.03, 0.12, 0.27, 0.06]), "Show values of my moves: off")
        self.b_x.on_clicked(lambda _: self.new_game("X"))
        self.b_o.on_clicked(lambda _: self.new_game("O"))
        self.b_v.on_clicked(self.toggle_values)
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)

        self.new_game("X")

    # ---------------------------------------------------------- helpers
    def refresh(self):
        self.fig.canvas.draw_idle()
        if ANIMATE:
            plt.pause(0.001)

    def reset_graph(self):
        self.colours = [FAINT] * len(self.nodes)
        self.sizes = [8] * len(self.nodes)
        self.scatter.set_facecolors(self.colours)
        self.scatter.set_sizes(self.sizes)
        self.option_lines.set_segments([])
        for t in self.option_texts:
            t.remove()
        self.option_texts = []

    def light_up(self, boards):
        for b in boards:
            k = self.index[b]
            self.colours[k] = VALUE_COLOUR[value(b)]
            self.sizes[k] = 16
        self.scatter.set_facecolors(self.colours)
        self.scatter.set_sizes(self.sizes)

    def draw_board(self):
        for i, ch in enumerate(self.board):
            t = self.cell_texts[i]
            t.set_text("" if ch == "." else ch)
            t.set_color(BLUE if ch == "X" else RED)
            self.hint_texts[i].set_text("")
        pts = [self.pos[canonical(b)] for b in self.history]
        self.path_line.set_data([p[0] for p in pts], [p[1] for p in pts])
        self.current.set_offsets([pts[-1]])

        w, line = winner(self.board)
        if line:
            a, c = line[0], line[2]
            self.win_line.set_data([a % 3 + 0.5, c % 3 + 0.5], [2 - a // 3 + 0.5, 2 - c // 3 + 0.5])
        else:
            self.win_line.set_data([], [])

        if is_over(self.board):
            if w == self.human:
                self.status.set_text("You win!")
            elif w:
                self.status.set_text("The computer wins.")
            else:
                self.status.set_text("Draw.")
        elif to_move(self.board) == self.human:
            self.status.set_text(f"Your move ({self.human})")
            if self.show_values:
                self.show_hints()

    def show_hints(self):
        sign = 1 if self.human == "X" else -1
        for i, c in children(self.board):
            v = sign * value(c)
            txt, col = {1: ("win", GREEN), 0: ("draw", GREY), -1: ("lose", RED)}[v]
            self.hint_texts[i].set_text(txt)
            self.hint_texts[i].set_color(col)

    # ---------------------------------------------------------- actions
    def new_game(self, human):
        if self.busy:
            return
        self.human, self.cpu = human, ("O" if human == "X" else "X")
        self.board = "." * 9
        self.history = [self.board]
        self.reset_graph()
        self.info.set_text("Click a cell to play." if human == "X"
                           else "The computer opens. Watch the graph.")
        self.draw_board()
        self.refresh()
        if self.cpu == "X":
            self.computer_move()

    def toggle_values(self, _):
        self.show_values = not self.show_values
        self.b_v.label.set_text(f"Show values of my moves: {'on' if self.show_values else 'off'}")
        self.draw_board()
        self.refresh()

    def on_click(self, event):
        if event.inaxes is not self.ax_board or self.busy or event.xdata is None:
            return
        if is_over(self.board) or to_move(self.board) != self.human:
            return
        col, row = int(event.xdata), 2 - int(event.ydata)
        if not (0 <= col < 3 and 0 <= row < 3):
            return
        i = 3 * row + col
        if self.board[i] != ".":
            return
        self.play(i, self.human)
        if not is_over(self.board):
            self.computer_move()

    def play(self, i, sign):
        self.board = self.board[:i] + sign + self.board[i + 1:]
        self.history.append(self.board)
        self.draw_board()
        self.refresh()

    def computer_move(self):
        self.busy = True
        self.status.set_text("Computer is thinking…")
        self.reset_graph()
        root = self.board
        root_depth = 9 - root.count(".")

        # Minimax with the game's scores (+10-d win, d-10 loss, 0 draw), remembering
        # the order in which positions are *finished*, i.e. when their value is known.
        order, seen, memo = [], set(), {}

        def minimax(b):
            if b in memo:
                return memo[b]
            d = 9 - b.count(".") - root_depth
            w, _ = winner(b)
            if w == self.cpu:
                s = 10 - d
            elif w == self.human:
                s = d - 10
            elif "." not in b:
                s = 0
            else:
                vals = [minimax(c) for _, c in children(b)]
                s = max(vals) if to_move(b) == self.cpu else min(vals)
            memo[b] = s
            c = canonical(b)
            if c not in seen:
                seen.add(c)
                order.append(c)
            return s

        options = [(i, c, minimax(c)) for i, c in children(root)]
        best = max(s for _, _, s in options)
        choice = random.choice([i for i, _, s in options if s == best])
        rc = canonical(root)
        if rc not in seen:
            order.append(rc)

        self.info.set_text(
            f"Plain minimax visits {tree_size(root) - 1:,} tree nodes here\n"
            f"({len(memo):,} distinct boards = {len(order)} graph positions).")

        # Animate: positions light up as minimax finishes evaluating them
        step = max(1, len(order) // ANIMATION_FRAMES)
        for k in range(0, len(order), step):
            self.light_up(order[k:k + step])
            if ANIMATE:
                self.fig.canvas.draw_idle()
                plt.pause(FRAME_PAUSE)

        # Show the computer's options from the current position
        segs, cols, widths = [], [], []
        x0, y0 = self.pos[rc]
        for i, c, s in options:
            x1, y1 = self.pos[canonical(c)]
            chosen = i == choice
            segs.append([(x0, y0), (x1, y1)])
            cols.append(GREEN if chosen else VALUE_COLOUR[value(c)])
            widths.append(3.5 if chosen else 1.4)
            if not any(abs(t.get_position()[0] - x1) < 1e-9 and abs(t.get_position()[1] - y1 - 0.18) < 1e-9
                       for t in self.option_texts):
                self.option_texts.append(self.ax_graph.text(
                    x1, y1 + 0.18, f"{s:+d}" if s else "0", ha="center", va="bottom", fontsize=9,
                    fontweight="bold", color=GREEN if chosen else "black", zorder=6,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.8)))
        self.option_lines.set_segments(segs)
        self.option_lines.set_color(cols)
        self.option_lines.set_linewidth(widths)

        if best > 0:
            verdict = "it can force a win"
        elif best == 0:
            verdict = "the best it can get is a draw"
        else:
            verdict = "it can only delay losing"
        self.info.set_text(self.info.get_text() +
                           f"\nBest score {best:+d}: {verdict}.\nIt plays cell {choice + 1}."
                           .replace("+0", "0"))
        self.play(choice, self.cpu)
        self.busy = False
        self.draw_board()
        self.refresh()


if __name__ == "__main__":
    app = App()
    plt.show()
