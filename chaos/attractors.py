"""
Attractor definitions.

Each attractor is a dataclass holding its parameters and a method
that returns derivatives (for continuous systems) or the next state
(for discrete iterated maps).
"""

from dataclasses import dataclass
from math import sin, cos
import numpy as np


# ──────────────────────────────────────────────
#  Continuous attractors  (dx/dt = f(x))
# ──────────────────────────────────────────────

@dataclass
class LorenzParams:
    """
    Lorenz (1963).  The canonical strange attractor.

    dx/dt = σ(y − x)
    dy/dt = x(ρ − z) − y
    dz/dt = xy − βz

    Standard parameters: σ=10, ρ=28, β=8/3.
    These place the system in the chaotic regime — two unstable fixed
    points that the trajectory orbits forever without repeating.
    """
    sigma: float = 10.0
    rho:   float = 28.0
    beta:  float = 8.0 / 3.0

    def derivatives(self, state: np.ndarray) -> np.ndarray:
        x, y, z = state
        return np.array([
            self.sigma * (y - x),
            x * (self.rho - z) - y,
            x * y - self.beta * z,
        ])


@dataclass
class RosslerParams:
    """
    Rössler (1976).  Simpler equations than Lorenz; single scroll.

    dx/dt = −y − z
    dy/dt = x + ay
    dz/dt = b + z(x − c)

    Standard parameters: a=0.2, b=0.2, c=5.7.
    """
    a: float = 0.2
    b: float = 0.2
    c: float = 5.7

    def derivatives(self, state: np.ndarray) -> np.ndarray:
        x, y, z = state
        return np.array([
            -y - z,
            x + self.a * y,
            self.b + z * (x - self.c),
        ])


# ──────────────────────────────────────────────
#  Discrete iterated maps  (x_{n+1} = f(x_n))
# ──────────────────────────────────────────────

@dataclass
class CliffordParams:
    """
    Clifford attractor (Pickover, 1988).

    x_{n+1} = sin(a·y) + c·cos(a·x)
    y_{n+1} = sin(b·x) + d·cos(b·y)

    Four real-valued parameters produce radically different attractors.
    The system is always bounded but never repeats.
    """
    a: float
    b: float
    c: float
    d: float
    name: str = ""
    cmap: str = "inferno"

    def step(self, x: float, y: float):
        xn = sin(self.a * y) + self.c * cos(self.a * x)
        yn = sin(self.b * x) + self.d * cos(self.b * y)
        return xn, yn


@dataclass
class DeJongParams:
    """
    Peter de Jong attractor.

    x_{n+1} = sin(a·y) − cos(b·x)
    y_{n+1} = sin(c·x) − cos(d·y)
    """
    a: float
    b: float
    c: float
    d: float
    name: str = ""
    cmap: str = "plasma"

    def step(self, x: float, y: float):
        xn = sin(self.a * y) - cos(self.b * x)
        yn = sin(self.c * x) - cos(self.d * y)
        return xn, yn


# ──────────────────────────────────────────────
#  Curated parameter presets
# ──────────────────────────────────────────────

CLIFFORD_PRESETS = [
    CliffordParams(-1.7,  1.8, -1.9, -0.4, name="Wings",   cmap="inferno"),
    CliffordParams(-1.4,  1.6,  1.0,  0.7, name="Spiral",  cmap="plasma"),
    CliffordParams( 1.5, -1.8,  1.6,  0.9, name="Vortex",  cmap="magma"),
    CliffordParams(-2.0, -2.0, -1.2,  2.0, name="Split",   cmap="cividis"),
]

DEJONG_PRESETS = [
    DeJongParams(-2.0,  -2.0,  -1.2,   2.0,  name="Classic", cmap="plasma"),
    DeJongParams( 2.01,  -2.53, 1.61, -0.33, name="Folds",   cmap="inferno"),
]
