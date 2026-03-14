"""
evo_game/visualize.py — Plotting functions for the evolutionary game theory lab.

Dark-background aesthetic, consistent with the chaos module.
All functions return a matplotlib Figure; callers save via save_figure().
"""

import os
from typing import List, Tuple

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib.gridspec import GridSpec
from matplotlib.collections import LineCollection

from evo_game.games import Game
from evo_game.replicator import to_ternary


# ── Palette (same dark background as chaos module) ────────────────────────────

BG    = "#0a0a0a"
GRID  = "#1a1a2e"
TICK  = "#555566"
LABEL = "#999aaa"
TITLE = "#ddddee"
DIM   = "#444455"


def _style_ax(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(BG)
    ax.set_title(title,  color=TITLE, fontsize=11, pad=8)
    ax.set_xlabel(xlabel, color=LABEL, fontsize=8)
    ax.set_ylabel(ylabel, color=LABEL, fontsize=8)
    ax.tick_params(colors=TICK, labelsize=7)
    for spine in ax.spines.values():
        spine.set_color(GRID)


def save_figure(fig, name: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    return path


# ── Replicator: 2-strategy games ─────────────────────────────────────────────

def plot_2strategy_replicator(
    game: Game,
    results: List[Tuple[np.ndarray, np.ndarray]],
) -> plt.Figure:
    """
    Two-panel figure for a 2-strategy game:
      Left:  strategy frequency over time (multiple initial conditions)
      Right: phase portrait — dx₀/dt as a function of x₀

    results: list of (t, x) pairs from multi_simulate
    """
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), facecolor=BG)
    fig.suptitle(game.name, color=TITLE, fontsize=14, y=1.01)

    c0, c1 = game.colors[0], game.colors[1]
    s0, s1 = game.strategies[0], game.strategies[1]

    # ── Left: time series ────────────────────────────────────────────────────
    ax = axes[0]
    _style_ax(ax, title=f"Strategy Frequency over Time",
              xlabel="Time", ylabel=f"Frequency of {s0}")

    for t, x in results:
        freq_0 = x[:, 0]
        ax.plot(t, freq_0, color=c0, linewidth=0.9, alpha=0.8)

    ax.axhline(0.0, color=DIM, linewidth=0.5, linestyle="--")
    ax.axhline(1.0, color=DIM, linewidth=0.5, linestyle="--")
    ax.set_ylim(-0.05, 1.05)

    # Mark equilibria from phase portrait analysis
    _mark_2strategy_equilibria(ax, game, orientation="h")

    legend_elements = [
        Line2D([0], [0], color=c0, label=s0, linewidth=2),
        Line2D([0], [0], color=c1, label=s1, linewidth=2),
    ]
    ax.legend(handles=legend_elements, fontsize=8, facecolor=BG,
              labelcolor=TITLE, framealpha=0.6, edgecolor=GRID)

    # ── Right: phase portrait ─────────────────────────────────────────────
    ax2 = axes[1]
    _style_ax(ax2, title="Phase Portrait  (replicator velocity)",
              xlabel=f"Frequency of {s0}", ylabel="dx₀/dt")

    p = np.linspace(0.001, 0.999, 500)
    A = game.payoff

    # dx₀/dt = x₀*(1-x₀) * [(A00-A10)*x₀ + (A01-A11)*(1-x₀)]
    dpdt = p * (1 - p) * ((A[0, 0] - A[1, 0]) * p + (A[0, 1] - A[1, 1]) * (1 - p))

    pos_mask = dpdt >= 0
    ax2.plot(p[pos_mask],  dpdt[pos_mask],  color=c0, linewidth=2.0)
    ax2.plot(p[~pos_mask], dpdt[~pos_mask], color=c1, linewidth=2.0)
    ax2.axhline(0, color=LABEL, linewidth=0.8, alpha=0.6)
    ax2.axvline(0, color=DIM, linewidth=0.5)
    ax2.axvline(1, color=DIM, linewidth=0.5)

    # Shade direction of flow
    ax2.fill_between(p, 0, dpdt, where=pos_mask,  alpha=0.12, color=c0)
    ax2.fill_between(p, 0, dpdt, where=~pos_mask, alpha=0.12, color=c1)

    _mark_2strategy_equilibria(ax2, game, orientation="v")

    # Annotate with description
    fig.text(0.5, -0.04, game.description, ha="center", va="top",
             color=LABEL, fontsize=8, wrap=True)

    fig.tight_layout()
    return fig


def _mark_2strategy_equilibria(ax, game: Game, orientation="h"):
    """Mark fixed points on a 2-strategy plot."""
    A = game.payoff
    # Interior fixed point: (A00-A10)*p + (A01-A11)*(1-p) = 0
    # p* = (A11 - A01) / (A00 - A10 - A01 + A11)
    denom = (A[0, 0] - A[1, 0] - A[0, 1] + A[1, 1])
    interior_eq = None
    if abs(denom) > 1e-10:
        p_star = (A[1, 1] - A[0, 1]) / denom
        if 0.01 < p_star < 0.99:
            interior_eq = p_star

    eqs = [0.0, 1.0]
    if interior_eq is not None:
        eqs.append(interior_eq)

    for p_eq in eqs:
        # Determine stability: df/dp at p_eq
        # For boundary: check sign of dpdt just inside
        eps = 0.005
        p_test = min(max(p_eq + eps, 0.001), 0.999) if p_eq < 0.5 else \
                 min(max(p_eq - eps, 0.001), 0.999)
        dpdt = p_test * (1 - p_test) * (
            (A[0, 0] - A[1, 0]) * p_test + (A[0, 1] - A[1, 1]) * (1 - p_test)
        )
        if p_eq < 0.5:
            stable = dpdt < 0   # flow toward 0
        else:
            stable = dpdt > 0   # flow toward 1

        # Interior: stable if dpdt changes from + to - as p increases through p*
        if interior_eq is not None and abs(p_eq - interior_eq) < 0.001:
            p_lo = max(p_eq - 0.02, 0.001)
            p_hi = min(p_eq + 0.02, 0.999)
            dpdt_lo = p_lo * (1 - p_lo) * ((A[0, 0] - A[1, 0]) * p_lo + (A[0, 1] - A[1, 1]) * (1 - p_lo))
            dpdt_hi = p_hi * (1 - p_hi) * ((A[0, 0] - A[1, 0]) * p_hi + (A[0, 1] - A[1, 1]) * (1 - p_hi))
            stable = (dpdt_lo > 0 and dpdt_hi < 0)

        color = "#aaffaa" if stable else "#ffaaaa"
        marker = "o" if stable else "s"

        if orientation == "h":
            ax.axvline(p_eq, color=color, linewidth=0.8, linestyle=":", alpha=0.7)
        else:
            ax.axvline(p_eq, color=color, linewidth=0.8, linestyle=":")
            if abs(p_eq - 0.0) < 0.01 or abs(p_eq - 1.0) < 0.01 or interior_eq is not None:
                ax.scatter([p_eq], [0.0], color=color, s=60, zorder=5,
                           marker=marker, edgecolors="white", linewidths=0.5)


# ── Replicator: 3-strategy (simplex / ternary) ───────────────────────────────

def plot_rps_replicator(
    game: Game,
    results: List[Tuple[np.ndarray, np.ndarray]],
    single_result: Tuple[np.ndarray, np.ndarray] = None,
) -> plt.Figure:
    """
    Two-panel figure for Rock-Paper-Scissors:
      Left:  ternary simplex showing orbits from multiple initial conditions
      Right: time series of one representative trajectory
    """
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), facecolor=BG)
    fig.suptitle(game.name, color=TITLE, fontsize=14, y=1.01)

    c0, c1, c2 = game.colors[0], game.colors[1], game.colors[2]
    s0, s1, s2 = game.strategies[0], game.strategies[1], game.strategies[2]

    # ── Left: simplex ─────────────────────────────────────────────────────
    ax = axes[0]
    ax.set_facecolor(BG)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Replicator Dynamics on the Simplex", color=TITLE, fontsize=11, pad=8)

    # Draw simplex edges
    verts = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2]])
    triangle = plt.Polygon(verts, fill=False, edgecolor=GRID, linewidth=1.0)
    ax.add_patch(triangle)

    # Label vertices — offset slightly outside
    offsets = [(-0.09, -0.06), (0.03, -0.06), (0.0, 0.05)]
    for (vx, vy), label, color, off in zip(verts, [s0, s1, s2], [c0, c1, c2], offsets):
        ax.text(vx + off[0], vy + off[1], label,
                color=color, fontsize=9, fontweight="bold", ha="center")
        ax.scatter([vx], [vy], color=color, s=30, zorder=5)

    # Interior Nash equilibrium
    cx, cy = to_ternary(np.array([[1/3, 1/3, 1/3]]))[0][0], \
             to_ternary(np.array([[1/3, 1/3, 1/3]]))[1][0]
    ax.scatter([cx], [cy], color="#ffffff", s=60, zorder=6,
               marker="x", linewidths=1.5)
    ax.text(cx + 0.02, cy + 0.02, "Nash\nequilibrium",
            color=LABEL, fontsize=7, ha="left")

    # Draw trajectories
    cmap = plt.get_cmap("plasma")
    for k, (t, x) in enumerate(results):
        px, py = to_ternary(x)
        alpha = 0.55
        color = cmap(k / max(len(results) - 1, 1))
        ax.plot(px, py, color=color, linewidth=0.9, alpha=alpha)
        ax.scatter([px[0]], [py[0]], color=color, s=15, zorder=5, alpha=0.8)

    ax.set_xlim(-0.15, 1.15)
    ax.set_ylim(-0.12, 1.0)

    # Cyclic arrows along edges
    for i, (a, b, clr) in enumerate([(s0, s1, c0), (s1, s2, c1), (s2, s0, c2)]):
        pass  # nice to have but skip for now

    # ── Right: time series ────────────────────────────────────────────────
    ax2 = axes[1]
    _style_ax(ax2, title="Strategy Frequencies — one trajectory",
              xlabel="Time", ylabel="Frequency")

    if single_result is None and results:
        # Use the one closest to equal split
        single_result = results[len(results) // 2]

    t, x = single_result
    for i, (color, label) in enumerate(zip(game.colors, game.strategies)):
        ax2.plot(t, x[:, i], color=color, linewidth=1.2, label=label)

    ax2.axhline(1/3, color=DIM, linewidth=0.6, linestyle="--", alpha=0.7)
    ax2.text(t[-1] * 0.98, 1/3 + 0.01, "1/3", color=DIM, fontsize=7, ha="right")
    ax2.set_ylim(-0.02, 1.02)
    ax2.legend(fontsize=8, facecolor=BG, labelcolor=TITLE,
               framealpha=0.6, edgecolor=GRID)

    fig.text(0.5, -0.04, game.description, ha="center", va="top",
             color=LABEL, fontsize=8)

    fig.tight_layout()
    return fig


# ── Spatial games ─────────────────────────────────────────────────────────────

def plot_spatial_snapshots(
    game: Game,
    times: List[int],
    snapshots: List[np.ndarray],
    freq_hist: np.ndarray,
) -> plt.Figure:
    """
    Grid of spatial snapshots + cooperation frequency over time.

    Shows snapshots at selected time steps, then a line plot of
    strategy frequencies over all steps.
    """
    n_snaps = len(snapshots)
    n_strats = game.n

    fig = plt.figure(figsize=(14, 6), facecolor=BG)
    gs = GridSpec(
        2, n_snaps,
        figure=fig,
        height_ratios=[3, 1.2],
        hspace=0.35,
        wspace=0.08,
    )

    # ── Top row: spatial snapshots ────────────────────────────────────────
    colors_rgb = [mcolors.to_rgb(c) for c in game.colors]
    # Build (n_strats, 3) colour map
    cmap_arr = np.array(colors_rgb)

    for k, (t_step, grid) in enumerate(zip(times, snapshots)):
        ax = fig.add_subplot(gs[0, k])
        ax.set_facecolor(BG)
        ax.axis("off")
        ax.set_title(f"t = {t_step}", color=TITLE, fontsize=9, pad=4)

        # Convert strategy grid to RGB image
        img = cmap_arr[grid]   # (N, N, 3)
        ax.imshow(img, interpolation="nearest", aspect="equal")

    # ── Bottom: frequency over time ───────────────────────────────────────
    ax_freq = fig.add_subplot(gs[1, :])
    _style_ax(ax_freq, title="", xlabel="Time step", ylabel="Frequency")

    n_steps_total = freq_hist.shape[0] - 1
    step_range = np.arange(freq_hist.shape[0])

    for s in range(n_strats):
        ax_freq.plot(step_range, freq_hist[:, s],
                     color=game.colors[s],
                     linewidth=1.4,
                     label=game.strategies[s])

    ax_freq.set_xlim(0, n_steps_total)
    ax_freq.set_ylim(-0.02, 1.02)
    ax_freq.axhline(1/n_strats, color=DIM, linewidth=0.5, linestyle="--", alpha=0.6)
    ax_freq.legend(fontsize=8, facecolor=BG, labelcolor=TITLE,
                   framealpha=0.6, edgecolor=GRID, loc="right")

    fig.suptitle(f"Spatial {game.name}", color=TITLE, fontsize=13, y=1.01)
    return fig


# ── Tournament ────────────────────────────────────────────────────────────────

def plot_tournament_results(result) -> plt.Figure:
    """
    Three-panel figure for the tournament:
      Left:   total payoff leaderboard (horizontal bar chart)
      Center: overall cooperation rate per strategy
      Right:  pairwise cooperation heatmap
    """
    n = len(result.names)
    order = np.argsort(result.total_scores)[::-1]   # highest first

    fig = plt.figure(figsize=(16, 6), facecolor=BG)
    gs = GridSpec(1, 3, figure=fig, wspace=0.4)

    # ── Left: leaderboard ─────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    _style_ax(ax1, title="Total Payoff  (round-robin)", xlabel="Total Payoff", ylabel="")

    names_ord  = [result.names[i]  for i in order]
    scores_ord = [result.total_scores[i] for i in order]
    colors_ord = [result.colors[i] for i in order]

    bars = ax1.barh(
        range(n), scores_ord,
        color=colors_ord, edgecolor=BG, linewidth=0.5, alpha=0.85
    )
    ax1.set_yticks(range(n))
    ax1.set_yticklabels(names_ord, fontsize=7.5, color=TITLE)
    ax1.tick_params(axis="x", colors=TICK, labelsize=7)
    ax1.invert_yaxis()

    # Score labels
    max_s = max(scores_ord)
    for i, (bar, score) in enumerate(zip(bars, scores_ord)):
        ax1.text(score + max_s * 0.01, i, f"{score:.0f}",
                 va="center", ha="left", fontsize=7, color=LABEL)

    # ── Center: cooperation rate ──────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    _style_ax(ax2, title="Cooperation Rate", xlabel="Fraction of moves cooperated", ylabel="")

    coops_ord = [result.coop_rates[i] for i in order]
    bars2 = ax2.barh(
        range(n), coops_ord,
        color=colors_ord, edgecolor=BG, linewidth=0.5, alpha=0.85
    )
    ax2.set_yticks(range(n))
    ax2.set_yticklabels(names_ord, fontsize=7.5, color=TITLE)
    ax2.tick_params(axis="x", colors=TICK, labelsize=7)
    ax2.set_xlim(0, 1.1)
    ax2.axvline(0.5, color=DIM, linewidth=0.6, linestyle="--", alpha=0.6)
    ax2.invert_yaxis()

    for i, (bar, coop) in enumerate(zip(bars2, coops_ord)):
        ax2.text(coop + 0.01, i, f"{coop:.0%}",
                 va="center", ha="left", fontsize=7, color=LABEL)

    # ── Right: pairwise cooperation heatmap ───────────────────────────────
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.set_facecolor(BG)
    ax3.set_title("Cooperation in Each Matchup\n(row strategy cooperates with column)",
                  color=TITLE, fontsize=9, pad=6)

    # Reorder matrix by leaderboard rank
    coop_matrix = result.match_coop[np.ix_(order, order)]
    im = ax3.imshow(coop_matrix, vmin=0, vmax=1, cmap="RdYlGn", aspect="auto")

    ax3.set_xticks(range(n))
    ax3.set_yticks(range(n))
    short_names = [_shorten(result.names[i]) for i in order]
    ax3.set_xticklabels(short_names, rotation=45, ha="right",
                        fontsize=7, color=TICK)
    ax3.set_yticklabels(short_names, fontsize=7, color=TICK)

    # Cell annotations
    for i in range(n):
        for j in range(n):
            val = coop_matrix[i, j]
            txt_color = "black" if 0.3 < val < 0.75 else "white"
            ax3.text(j, i, f"{val:.0%}", ha="center", va="center",
                     fontsize=6.5, color=txt_color)

    cbar = fig.colorbar(im, ax=ax3, fraction=0.04, pad=0.04)
    cbar.ax.tick_params(colors=TICK, labelsize=7)
    cbar.set_label("Cooperation rate", color=LABEL, fontsize=8)

    fig.suptitle(
        f"Iterated Prisoner's Dilemma Tournament  "
        f"({result.n_rounds} rounds/match, {n} strategies)",
        color=TITLE, fontsize=13, y=1.01,
    )
    fig.tight_layout()
    return fig


def _shorten(name: str) -> str:
    """Short label for the heatmap axis."""
    mapping = {
        "Always Cooperate": "AllC",
        "Always Defect": "AllD",
        "Tit-for-Tat": "TFT",
        "Pavlov (WSLS)": "Pavlov",
        "Grim Trigger": "Grim",
        "Random": "Random",
        "Generous TFT": "GenTFT",
        "Suspicious TFT": "SusTFT",
        "Contrite TFT": "ConTFT",
    }
    return mapping.get(name, name[:7])
