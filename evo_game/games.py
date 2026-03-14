"""
evo_game/games.py — Payoff matrices for classic evolutionary games.

Each game is a Game object wrapping an (n x n) payoff array where
A[i, j] is the payoff to strategy i when playing against strategy j.

Convention: row player payoffs only. Games are symmetric, so this is
sufficient for the replicator equation.
"""

from dataclasses import dataclass, field
from typing import List

import numpy as np


@dataclass
class Game:
    name: str
    strategies: List[str]
    payoff: np.ndarray          # shape (n, n)
    description: str = ""
    colors: List[str] = field(default_factory=list)

    @property
    def n(self) -> int:
        return len(self.strategies)

    def fitness(self, x: np.ndarray) -> np.ndarray:
        """Fitness of each strategy given population state x."""
        return self.payoff @ x

    def mean_fitness(self, x: np.ndarray) -> float:
        """Population mean fitness."""
        return float(x @ self.fitness(x))


# ── Classic two-strategy games ────────────────────────────────────────────────

def prisoner_dilemma() -> Game:
    """
    Prisoner's Dilemma.

    Payoff ordering: T > R > P > S
    (Temptation > Reward > Punishment > Sucker's payoff)

    Defection strictly dominates cooperation regardless of what the opponent
    does. The only Nash equilibrium is mutual defection, even though mutual
    cooperation Pareto-dominates it. This is why it's a 'dilemma'.

    ESS: all-Defect.
    """
    R, T, P, S = 3.0, 5.0, 1.0, 0.0
    A = np.array([
        [R, S],   # Cooperate vs {C, D}
        [T, P],   # Defect    vs {C, D}
    ])
    return Game(
        name="Prisoner's Dilemma",
        strategies=["Cooperate", "Defect"],
        payoff=A,
        description=(
            "Defection is a dominant strategy. The unique Nash equilibrium is "
            "(Defect, Defect), though (Cooperate, Cooperate) gives both players more. "
            "The replicator drives every initial condition to all-Defect."
        ),
        colors=["#4ecdc4", "#ff6b6b"],
    )


def hawk_dove(V: float = 4.0, C: float = 6.0) -> Game:
    """
    Hawk-Dove (also known as Chicken).

    V = value of the resource being contested.
    C = cost of injury when two Hawks meet (assume C > V for interesting dynamics).

    Hawks always escalate; Doves always retreat from an escalation.
    When two Hawks meet, they fight at cost C/2 each and one wins V.
    When a Hawk meets a Dove, the Hawk wins V; the Dove retreats unharmed.
    When two Doves meet, they share: each gets V/2.

    ESS: mixed strategy with p* = V/C fraction Hawks.
    This is a stable polymorphism — an interior fixed point.
    """
    A = np.array([
        [(V - C) / 2.0,  V        ],   # Hawk vs {Hawk, Dove}
        [0.0,            V / 2.0  ],   # Dove vs {Hawk, Dove}
    ])
    p_star = V / C
    return Game(
        name="Hawk-Dove",
        strategies=["Hawk", "Dove"],
        payoff=A,
        description=(
            f"Stable mixed equilibrium at {p_star:.0%} Hawks, {1-p_star:.0%} Doves "
            f"(V={V}, C={C}). All initial conditions converge to this interior point."
        ),
        colors=["#ff6b6b", "#a8e6cf"],
    )


def stag_hunt() -> Game:
    """
    Stag Hunt (Assurance game / Coordination game).

    Two hunters: coordinate to catch a stag (high reward for both) or
    hunt hare alone (safe, modest reward regardless of partner's choice).

    Two pure-strategy Nash equilibria: (Stag, Stag) and (Hare, Hare).
    Both are also evolutionarily stable. The basin of attraction of each
    depends on initial frequencies — there is an unstable interior equilibrium.

    This models trust: cooperation is possible but not guaranteed.
    """
    A = np.array([
        [4.0, 0.0],   # Stag vs {Stag, Hare}
        [2.0, 2.0],   # Hare vs {Stag, Hare}
    ])
    return Game(
        name="Stag Hunt",
        strategies=["Stag (cooperate)", "Hare (safe)"],
        payoff=A,
        description=(
            "Bistable: two stable equilibria at all-Stag and all-Hare, separated "
            "by an unstable interior fixed point. Initial conditions determine outcome — "
            "this is a model of trust and coordination failure."
        ),
        colors=["#ffd93d", "#6bcb77"],
    )


# ── Three-strategy game ───────────────────────────────────────────────────────

def rock_paper_scissors() -> Game:
    """
    Rock-Paper-Scissors.

    Cyclic dominance: Rock beats Scissors, Scissors beats Paper, Paper beats Rock.
    The unique Nash equilibrium is the mixed strategy (1/3, 1/3, 1/3).

    Under replicator dynamics, trajectories cycle around this interior fixed point.
    Unlike the two-strategy games, the dynamics never converge — the system orbits
    indefinitely on closed curves around the Nash equilibrium.

    This models many real biological systems: side-blotched lizards, bacteriocin
    competition in E. coli, plant competition on rocky shores.
    """
    A = np.array([
        [0.0,  1.0, -1.0],   # Rock    vs {R, P, S}
        [-1.0, 0.0,  1.0],   # Paper   vs {R, P, S}
        [1.0, -1.0,  0.0],   # Scissors vs {R, P, S}
    ])
    return Game(
        name="Rock-Paper-Scissors",
        strategies=["Rock", "Paper", "Scissors"],
        payoff=A,
        description=(
            "Cyclic dominance with no ESS. Replicator dynamics produce perpetual "
            "orbits around the (1/3, 1/3, 1/3) Nash equilibrium. The system never "
            "settles — strategy frequencies oscillate forever."
        ),
        colors=["#ff6b6b", "#4ecdc4", "#ffd93d"],
    )
