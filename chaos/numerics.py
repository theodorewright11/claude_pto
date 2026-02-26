"""
Numerical methods.

- rk4: single Runge-Kutta 4th-order step
- integrate: produce full trajectory for a continuous attractor
- iterate_map: produce full trajectory for a 2D iterated map
- logistic_bifurcation: sweep r, return (r_vals, x_vals) for the
  bifurcation diagram of x_{n+1} = r·x·(1−x)
"""

import numpy as np


def rk4(f, state: np.ndarray, dt: float) -> np.ndarray:
    k1 = f(state)
    k2 = f(state + 0.5 * dt * k1)
    k3 = f(state + 0.5 * dt * k2)
    k4 = f(state + dt * k3)
    return state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)


def integrate(attractor, state0: np.ndarray, n_steps: int, dt: float) -> np.ndarray:
    """Integrate a continuous attractor with RK4."""
    dim = len(state0)
    states = np.empty((n_steps, dim))
    states[0] = state0
    for i in range(1, n_steps):
        states[i] = rk4(attractor.derivatives, states[i - 1], dt)
    return states


def iterate_map(attractor, x0: float, y0: float, n_iter: int):
    """
    Iterate a 2D map attractor.

    Returns (x, y) as flat numpy arrays of length n_iter.
    Uses pre-allocated arrays and a Python loop — unavoidable since
    each step depends on the previous.
    """
    x = np.empty(n_iter)
    y = np.empty(n_iter)
    x[0], y[0] = x0, y0
    for i in range(1, n_iter):
        x[i], y[i] = attractor.step(x[i - 1], y[i - 1])
    return x, y


def logistic_bifurcation(
    r_min: float = 2.5,
    r_max: float = 4.0,
    n_r: int = 3000,
    n_iter: int = 300,
    n_transient: int = 500,
):
    """
    Bifurcation diagram of the logistic map x_{n+1} = r·x·(1−x).

    For each value of r, iterate past the transient, then record
    n_iter values of x.  Returns (r_out, x_out) as flat arrays.
    """
    r_vals = np.linspace(r_min, r_max, n_r)
    r_out = np.empty(n_r * n_iter)
    x_out = np.empty(n_r * n_iter)

    for idx, r in enumerate(r_vals):
        x = 0.5
        for _ in range(n_transient):
            x = r * x * (1.0 - x)
        for j in range(n_iter):
            x = r * x * (1.0 - x)
            r_out[idx * n_iter + j] = r
            x_out[idx * n_iter + j] = x

    return r_out, x_out
