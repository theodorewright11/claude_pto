"""
evo_game/spatial.py — Spatial evolutionary games on a 2D grid.

In well-mixed populations (replicator dynamics), defectors destroy cooperators.
But when agents interact only with their immediate neighbours, cooperation can
survive: clusters of cooperators protect each other from exploitation.

Setup (Nowak & May 1992 for PD; May, Nowak & Bonhoeffer for RPS):
  - Agents on an N×N toroidal grid (periodic boundaries)
  - Each agent plays all 8 Moore neighbours + itself each round
  - Each agent then adopts the strategy of the highest-scoring agent
    in its 3×3 neighbourhood (including itself)
  - Synchronous update

This deterministic rule is sufficient to produce self-organising patterns:
cooperator clusters, checkerboards, chaotic spirals.
"""

from typing import List, Tuple

import numpy as np

from evo_game.games import Game


def _moore_payoffs(grid: np.ndarray, A: np.ndarray, N: int) -> np.ndarray:
    """
    Compute total payoff for each cell from playing all 8 Moore neighbours.

    Uses numpy roll for periodic (toroidal) boundary conditions.
    grid: (N, N) integer array of strategy indices.
    A:    (n_strategies, n_strategies) payoff matrix.
    Returns: (N, N) float array of total payoffs.
    """
    n_s = A.shape[0]
    scores = np.zeros((N, N), dtype=float)

    for ds in range(-1, 2):
        for dt in range(-1, 2):
            if ds == 0 and dt == 0:
                continue  # play neighbours only (self is added below)
            neighbour = np.roll(np.roll(grid, ds, axis=0), dt, axis=1)
            for s in range(n_s):
                for opp in range(n_s):
                    mask = (grid == s) & (neighbour == opp)
                    scores[mask] += A[s, opp]

    # Also play self
    for s in range(n_s):
        for opp in range(n_s):
            mask = (grid == s) & (grid == opp)
            scores[mask] += A[s, opp]

    return scores


def _best_neighbour_update(grid: np.ndarray, scores: np.ndarray, N: int) -> np.ndarray:
    """
    Each cell adopts the strategy of the highest-scoring cell in its
    3×3 Moore neighbourhood (including itself).
    """
    new_grid = grid.copy()
    best_score = scores.copy()
    best_strat = grid.copy()

    for ds in range(-1, 2):
        for dt in range(-1, 2):
            if ds == 0 and dt == 0:
                continue
            neighbour_scores = np.roll(np.roll(scores, ds, axis=0), dt, axis=1)
            neighbour_strats = np.roll(np.roll(grid,   ds, axis=0), dt, axis=1)
            mask = neighbour_scores > best_score
            best_score[mask] = neighbour_scores[mask]
            best_strat[mask] = neighbour_strats[mask]

    return best_strat


def run_spatial(
    game: Game,
    N: int = 150,
    n_steps: int = 200,
    snapshot_steps: Tuple[int, ...] = (0, 1, 5, 20, 50, 100, 200),
    seed: int = 42,
) -> Tuple[List[int], List[np.ndarray], np.ndarray]:
    """
    Run the spatial evolutionary game.

    Returns:
        times      — list of step numbers at which snapshots were taken
        snapshots  — list of (N, N) strategy grids at those steps
        freq_hist  — (n_steps+1, n_strategies) strategy frequency history
    """
    rng = np.random.default_rng(seed)
    n_s = game.n

    # Random initialisation — equal probability of each strategy
    grid = rng.integers(0, n_s, size=(N, N))

    snap_set = set(snapshot_steps)
    times: List[int] = []
    snapshots: List[np.ndarray] = []
    freq_hist = np.zeros((n_steps + 1, n_s), dtype=float)

    def record_freq(step: int):
        for s in range(n_s):
            freq_hist[step, s] = np.mean(grid == s)

    record_freq(0)
    if 0 in snap_set:
        times.append(0)
        snapshots.append(grid.copy())

    for step in range(1, n_steps + 1):
        scores = _moore_payoffs(grid, game.payoff, N)
        grid = _best_neighbour_update(grid, scores, N)
        record_freq(step)
        if step in snap_set:
            times.append(step)
            snapshots.append(grid.copy())

    return times, snapshots, freq_hist


# ── Nowak-May Prisoner's Dilemma parametrisation ─────────────────────────────

def nowak_may_pd(b: float = 1.65) -> Game:
    """
    Nowak & May (1992) Prisoner's Dilemma.

    Simplified payoffs: T=b, R=1, P=0, S=0.
    With b ∈ (1, 2) this produces diverse spatial patterns — cooperators
    survive in clusters despite defectors having local advantage.

    b=1.65 gives complex 'chaotic' patterns (neither fully ordered nor random).
    """
    from evo_game.games import Game
    A = np.array([
        [1.0, 0.0],   # C vs {C, D}
        [b,   0.0],   # D vs {C, D}
    ])
    return Game(
        name=f"Spatial PD  (b={b})",
        strategies=["Cooperate", "Defect"],
        payoff=A,
        description=(
            f"Nowak-May spatial Prisoner's Dilemma with b={b}. "
            "Cooperators survive via clustering despite being locally exploitable."
        ),
        colors=["#4ecdc4", "#ff6b6b"],
    )
