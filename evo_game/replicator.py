"""
evo_game/replicator.py — Replicator dynamics.

The replicator equation describes how strategy frequencies change in a
well-mixed population under natural selection:

    dx_i/dt = x_i * (f_i(x) - f̄(x))

where:
    x_i    = frequency of strategy i  (x lives on the simplex: x_i ≥ 0, Σx_i = 1)
    f_i(x) = Σ_j A[i,j] * x_j        (expected payoff against the current population)
    f̄(x)  = Σ_i x_i * f_i(x)        (mean population payoff)

Strategies that outperform the mean grow; those that underperform shrink.
The simplex is invariant: if you start with valid frequencies, you stay there.
"""

from typing import List, Tuple

import numpy as np
from scipy.integrate import solve_ivp

from evo_game.games import Game


def _rhs(t: float, x: np.ndarray, A: np.ndarray) -> np.ndarray:
    """Replicator equation right-hand side."""
    f = A @ x            # fitness of each strategy
    f_bar = float(x @ f) # mean fitness
    return x * (f - f_bar)


def simulate(
    game: Game,
    x0: np.ndarray,
    t_end: float = 60.0,
    n_points: int = 600,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Integrate the replicator equation from initial state x0.

    Returns:
        t  — shape (n_points,)
        x  — shape (n_points, n_strategies)
    """
    t_eval = np.linspace(0.0, t_end, n_points)
    sol = solve_ivp(
        _rhs,
        (0.0, t_end),
        x0,
        args=(game.payoff,),
        t_eval=t_eval,
        method="RK45",
        rtol=1e-9,
        atol=1e-11,
    )
    x = sol.y.T
    x = np.clip(x, 0.0, 1.0)
    # Re-normalise to prevent numerical drift off the simplex
    sums = x.sum(axis=1, keepdims=True)
    sums[sums == 0] = 1.0
    x /= sums
    return sol.t, x


def multi_simulate(
    game: Game,
    initial_conditions: List[np.ndarray],
    **kwargs,
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Simulate from multiple initial conditions. Returns list of (t, x) pairs."""
    return [simulate(game, x0, **kwargs) for x0 in initial_conditions]


# ── Initial condition grids ───────────────────────────────────────────────────

def grid_2strategy(n: int = 9) -> List[np.ndarray]:
    """
    Evenly spaced initial conditions for a 2-strategy game.
    Returns n conditions from (ε, 1-ε) to (1-ε, ε), excluding the endpoints.
    """
    eps = 0.02
    ps = np.linspace(eps, 1 - eps, n)
    return [np.array([p, 1 - p]) for p in ps]


def grid_simplex_3strategy(n_per_edge: int = 7) -> List[np.ndarray]:
    """
    Grid of initial conditions on the 3-strategy simplex.
    Avoids corners and edges — interior points only.
    """
    ics = []
    eps = 0.05
    for i in range(1, n_per_edge):
        for j in range(1, n_per_edge - i):
            k = n_per_edge - i - j
            if k > 0:
                x = np.array([i, j, k], dtype=float)
                x /= x.sum()
                # Keep away from simplex boundary
                if all(xi > eps for xi in x):
                    ics.append(x)
    return ics


# ── Ternary plot coordinates ──────────────────────────────────────────────────

def to_ternary(x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert barycentric coordinates (3-strategy population state) to 2D.

    Vertex layout (standard ternary):
        strategy 0  →  bottom-left  (0, 0)
        strategy 1  →  bottom-right (1, 0)
        strategy 2  →  top          (0.5, √3/2)

    x shape: (..., 3)  with x[..., 0] + x[..., 1] + x[..., 2] = 1
    """
    x0 = x[..., 0]
    x1 = x[..., 1]
    x2 = x[..., 2]
    px = x1 + 0.5 * x2
    py = (np.sqrt(3) / 2.0) * x2
    return px, py
