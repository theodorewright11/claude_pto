"""
Visualization functions for the chaos explorer.

All figures use a dark background (#0a0a0a) for maximum visual contrast.
Figures are returned unfinalised — callers are responsible for saving
via `save_figure`.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — registers 3D projection


# ── Palette ──────────────────────────────────────────────────────────────────

BG        = "#0a0a0a"
GRID      = "#1a1a2e"
TICK      = "#555566"
LABEL     = "#999aaa"
TITLE     = "#ddddee"


def _style_ax(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(BG)
    ax.set_title(title,  color=TITLE, fontsize=12, pad=10)
    ax.set_xlabel(xlabel, color=LABEL, fontsize=9)
    ax.set_ylabel(ylabel, color=LABEL, fontsize=9)
    ax.tick_params(colors=TICK, labelsize=7)
    for spine in ax.spines.values():
        spine.set_color(GRID)


def save_figure(fig, name: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    return path


# ── Continuous attractors ─────────────────────────────────────────────────────

def plot_lorenz_3d(states: np.ndarray, title: str = "Lorenz Attractor"):
    """3D trajectory, coloured by time (plasma)."""
    fig = plt.figure(figsize=(10, 8), facecolor=BG)
    ax  = fig.add_subplot(111, projection="3d")
    ax.set_facecolor(BG)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor(GRID)
    ax.yaxis.pane.set_edgecolor(GRID)
    ax.zaxis.pane.set_edgecolor(GRID)
    ax.xaxis.line.set_color(GRID)
    ax.yaxis.line.set_color(GRID)
    ax.zaxis.line.set_color(GRID)
    ax.tick_params(colors=TICK, labelsize=6)

    n = len(states)
    seg = 500
    cmap = plt.get_cmap("plasma")
    for i in range(0, n - seg, seg):
        c = cmap(i / n)
        ax.plot(states[i:i+seg+1, 0],
                states[i:i+seg+1, 1],
                states[i:i+seg+1, 2],
                color=c, linewidth=0.25, alpha=0.8)

    ax.set_title(title, color=TITLE, fontsize=13, pad=15)
    fig.tight_layout()
    return fig


def plot_2d_projection(states: np.ndarray, title: str,
                       xi: int = 0, yi: int = 2,
                       xlabel: str = "X", ylabel: str = "Z"):
    """2D projection of a 3D trajectory, coloured by time."""
    fig, ax = plt.subplots(figsize=(7, 7), facecolor=BG)
    _style_ax(ax, title=title, xlabel=xlabel, ylabel=ylabel)

    n = len(states)
    seg = 300
    cmap = plt.get_cmap("plasma")
    for i in range(0, n - seg, seg):
        c = cmap(i / n)
        ax.plot(states[i:i+seg+1, xi],
                states[i:i+seg+1, yi],
                color=c, linewidth=0.2, alpha=0.7)

    fig.tight_layout()
    return fig


def plot_sensitivity(states1: np.ndarray, states2: np.ndarray,
                     title: str = "Butterfly Effect — Lorenz"):
    """
    Two-panel figure:
      left  — both trajectories in the XZ plane (they start together, diverge)
      right — Euclidean distance between the trajectories over time (log scale)
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=BG)

    ax1 = axes[0]
    _style_ax(ax1, title="Two Trajectories,  ε = 10⁻⁸",
              xlabel="X", ylabel="Z")
    n = min(len(states1), len(states2))
    ax1.plot(states1[:n, 0], states1[:n, 2],
             color="#4ecdc4", linewidth=0.25, alpha=0.8, label="Trajectory A")
    ax1.plot(states2[:n, 0], states2[:n, 2],
             color="#ff6b6b", linewidth=0.25, alpha=0.8, label="Trajectory B")
    ax1.legend(fontsize=8, facecolor=BG, labelcolor=TITLE,
               framealpha=0.6, edgecolor=GRID)

    ax2 = axes[1]
    _style_ax(ax2, title="Divergence of Nearby Trajectories",
              xlabel="Time step", ylabel="Distance (log scale)")
    distances = np.linalg.norm(states1[:n] - states2[:n], axis=1)
    distances = np.maximum(distances, 1e-18)
    ax2.semilogy(np.arange(n), distances, color="#ffa552", linewidth=0.9)
    ax2.tick_params(colors=TICK, labelsize=7)

    fig.suptitle(title, color=TITLE, fontsize=13, y=1.01)
    fig.tight_layout()
    return fig


# ── Discrete iterated maps ────────────────────────────────────────────────────

def plot_density(x: np.ndarray, y: np.ndarray,
                 title: str, cmap: str = "inferno",
                 resolution: int = 900):
    """
    Density plot for a 2D iterated map.

    Computes a 2D histogram and displays it on a log scale — this turns
    the scatter of millions of points into a glowing luminosity map.
    """
    fig, ax = plt.subplots(figsize=(8, 8), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_title(title, color=TITLE, fontsize=13, pad=10)
    ax.tick_params(colors=TICK, labelsize=6)
    for spine in ax.spines.values():
        spine.set_color(BG)
    ax.set_xticks([])
    ax.set_yticks([])

    margin = 0.05
    x_range = [x.min() - margin, x.max() + margin]
    y_range = [y.min() - margin, y.max() + margin]

    H, xedges, yedges = np.histogram2d(x, y, bins=resolution,
                                        range=[x_range, y_range])
    H = np.log1p(H).T   # log scale; transpose for correct orientation

    ax.imshow(H,
              extent=[x_range[0], x_range[1], y_range[0], y_range[1]],
              origin="lower", cmap=cmap, aspect="equal",
              interpolation="bilinear")

    fig.tight_layout(pad=0.5)
    return fig


# ── Logistic map ──────────────────────────────────────────────────────────────

def plot_bifurcation(r_vals: np.ndarray, x_vals: np.ndarray,
                     title: str = "Logistic Map — Route to Chaos"):
    """
    Bifurcation diagram of x_{n+1} = r·x·(1−x).

    The x-axis is the parameter r.  The y-axis shows the long-run
    behaviour: fixed points, period-2 cycles, period-4, ..., chaos.
    """
    fig, ax = plt.subplots(figsize=(14, 6), facecolor=BG)
    _style_ax(ax, title=title, xlabel="r  (growth rate)", ylabel="x  (long-run population)")

    ax.scatter(r_vals, x_vals,
               s=0.008, c="#e94560", alpha=0.25, rasterized=True)

    # Annotate key transitions
    for r_val, label, ha in [
        (3.0,  "period 2",     "left"),
        (3.449, "period 4",    "left"),
        (3.544, "period 8",    "left"),
        (3.57,  "chaos onset", "right"),
    ]:
        ax.axvline(r_val, color=GRID, linewidth=0.6, alpha=0.6)
        ax.text(r_val + (0.005 if ha == "left" else -0.005), 0.97,
                label, color=LABEL, fontsize=7, ha=ha,
                transform=ax.get_xaxis_transform(), va="top")

    fig.tight_layout()
    return fig
