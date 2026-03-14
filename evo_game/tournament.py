"""
evo_game/tournament.py — Iterated Prisoner's Dilemma tournament.

Axelrod's 1980 computer tournaments asked: what strategy does best in the
iterated Prisoner's Dilemma? He invited game theorists, economists, and
biologists to submit strategies. Tit-for-Tat — the simplest strategy submitted
— won both rounds.

This module reproduces that experiment with 9 strategies and round-robin
competition. Each pair plays 150 rounds; results are averaged across many
random orderings to reduce noise.

Payoffs:  R=3 (mutual C), T=5 (defect against cooperator), P=1 (mutual D),
          S=0 (cooperate against defector)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np

# Standard iterated PD payoffs
R, T, P, S = 3, 5, 1, 0

PAYOFF_MATRIX = {
    (True,  True ): (R, R),  # both cooperate
    (True,  False): (S, T),  # self cooperates, opp defects
    (False, True ): (T, S),  # self defects, opp cooperates
    (False, False): (P, P),  # both defect
}


# ── Strategy implementations ──────────────────────────────────────────────────

class Strategy:
    """Base class. Subclasses override `move` and optionally `reset`."""
    name: str = "Strategy"
    color: str = "#888888"

    def reset(self):
        """Called before each match to clear state."""
        pass

    def move(self, my_history: List[bool], opp_history: List[bool]) -> bool:
        """Return True to cooperate, False to defect."""
        raise NotImplementedError


class AllC(Strategy):
    name = "Always Cooperate"
    color = "#4ecdc4"

    def move(self, my_history, opp_history):
        return True


class AllD(Strategy):
    name = "Always Defect"
    color = "#ff6b6b"

    def move(self, my_history, opp_history):
        return False


class TFT(Strategy):
    """Tit-for-Tat — Axelrod's winner. Cooperate first, then mirror."""
    name = "Tit-for-Tat"
    color = "#ffd93d"

    def move(self, my_history, opp_history):
        if not opp_history:
            return True
        return opp_history[-1]


class Pavlov(Strategy):
    """
    Win-Stay, Lose-Shift (Pavlov).
    If last round was CC or DD, repeat. If CD or DC, switch.
    """
    name = "Pavlov (WSLS)"
    color = "#a8e6cf"

    def move(self, my_history, opp_history):
        if not my_history:
            return True
        last_mine = my_history[-1]
        last_opp  = opp_history[-1]
        # 'win' = got R or T; 'lose' = got S or P
        # Win iff same move as last time produced ≥ R: CC (win) or DC (win)
        # Equivalently: win iff my_move=C&opp=C, or my_move=D&opp=C → my got T
        # Simpler: win iff payoff ≥ R → last_mine=True&last_opp=True OR last_mine=False&last_opp=True (T)
        # Actually: win-stay = if I was satisfied (got R or T) stay; lose-shift = if I got P or S, switch
        # I got T if I defected and opp cooperated → satisfied. I got R if both cooperated → satisfied.
        won = (last_mine == True and last_opp == True) or \
              (last_mine == False and last_opp == True)
        if won:
            return last_mine
        else:
            return not last_mine


class Grim(Strategy):
    """
    Grim Trigger (Grudger).
    Cooperate until the opponent defects once, then always defect.
    """
    name = "Grim Trigger"
    color = "#c77dff"

    def reset(self):
        self._triggered = False

    def move(self, my_history, opp_history):
        if opp_history and not opp_history[-1]:
            self._triggered = True
        return not self._triggered


class Random(Strategy):
    """Random — cooperates with probability 0.5."""
    name = "Random"
    color = "#888888"

    def move(self, my_history, opp_history):
        return np.random.random() < 0.5


class GenerousTFT(Strategy):
    """
    Generous TFT.
    Like TFT but forgives defections with probability 1/3.
    Avoids punishment spirals caused by noise.
    """
    name = "Generous TFT"
    color = "#f4a261"

    def move(self, my_history, opp_history):
        if not opp_history:
            return True
        if opp_history[-1]:   # opponent cooperated → cooperate
            return True
        return np.random.random() < 1.0 / 3.0   # forgive with p=1/3


class STFT(Strategy):
    """
    Suspicious TFT.
    Like TFT but starts with Defect instead of Cooperate.
    """
    name = "Suspicious TFT"
    color = "#e76f51"

    def move(self, my_history, opp_history):
        if not opp_history:
            return False   # start with defection
        return opp_history[-1]


class ContriteTFT(Strategy):
    """
    Contrite TFT.
    If I defected last round (making me 'contrite'), I cooperate regardless.
    This prevents extended punishment cycles after accidental defections.
    """
    name = "Contrite TFT"
    color = "#2a9d8f"

    def reset(self):
        self._contrite = False

    def move(self, my_history, opp_history):
        if not opp_history:
            return True
        # If I defected last round, I am contrite → cooperate unconditionally
        if my_history and not my_history[-1]:
            self._contrite = True
        if self._contrite:
            self._contrite = False
            return True
        return opp_history[-1]


# ── Tournament engine ─────────────────────────────────────────────────────────

ALL_STRATEGIES = [AllC, AllD, TFT, Pavlov, Grim, Random, GenerousTFT, STFT, ContriteTFT]


def play_match(
    strat_a: Strategy,
    strat_b: Strategy,
    n_rounds: int = 150,
) -> Tuple[float, float, float, float]:
    """
    Play a single match between two strategies.

    Returns:
        score_a, score_b   — total payoffs
        coop_rate_a, coop_rate_b — fraction of rounds each cooperated
    """
    strat_a.reset()
    strat_b.reset()

    hist_a: List[bool] = []
    hist_b: List[bool] = []
    score_a = 0.0
    score_b = 0.0

    for _ in range(n_rounds):
        move_a = strat_a.move(hist_a, hist_b)
        move_b = strat_b.move(hist_b, hist_a)
        pa, pb = PAYOFF_MATRIX[(move_a, move_b)]
        score_a += pa
        score_b += pb
        hist_a.append(move_a)
        hist_b.append(move_b)

    coop_a = sum(hist_a) / n_rounds
    coop_b = sum(hist_b) / n_rounds
    return score_a, score_b, coop_a, coop_b


@dataclass
class TournamentResult:
    names: List[str]
    colors: List[str]
    total_scores: np.ndarray          # (n,)  — total payoff across all matches
    avg_scores: np.ndarray            # (n,)  — per-match average
    coop_rates: np.ndarray            # (n,)  — overall cooperation rate
    match_scores: np.ndarray          # (n, n) — avg score per match vs each opponent
    match_coop: np.ndarray            # (n, n) — cooperation rate vs each opponent
    n_rounds: int


def run_tournament(
    strategies: List[type] = None,
    n_rounds: int = 150,
    n_reps: int = 5,        # repeat each match to average over Random's noise
    seed: int = 0,
) -> TournamentResult:
    """
    Round-robin tournament: every pair plays n_rounds × n_reps rounds.

    strategies: list of Strategy subclasses (not instances)
    """
    if strategies is None:
        strategies = ALL_STRATEGIES

    np.random.seed(seed)
    instances = [cls() for cls in strategies]
    n = len(instances)
    names  = [s.name  for s in instances]
    colors = [s.color for s in instances]

    match_scores = np.zeros((n, n), dtype=float)
    match_coop   = np.zeros((n, n), dtype=float)
    n_matches    = np.zeros((n, n), dtype=int)

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            total_sa = total_sb = total_ca = total_cb = 0.0
            for _ in range(n_reps):
                sa, sb, ca, cb = play_match(instances[i], instances[j], n_rounds)
                total_sa += sa
                total_ca += ca
            # Average over reps
            match_scores[i, j] = total_sa / n_reps
            match_coop[i, j]   = total_ca / n_reps
            n_matches[i, j]     = 1

    # Self-play
    for i in range(n):
        total_sa = total_ca = 0.0
        for _ in range(n_reps):
            sa, _, ca, _ = play_match(instances[i], type(instances[i])(), n_rounds)
            total_sa += sa
            total_ca += ca
        match_scores[i, i] = total_sa / n_reps
        match_coop[i, i]   = total_ca / n_reps

    # Overall scores = row sums (total payoff vs all opponents including self)
    total_scores = match_scores.sum(axis=1)
    avg_scores   = total_scores / n
    coop_rates   = match_coop.mean(axis=1)

    return TournamentResult(
        names=names,
        colors=colors,
        total_scores=total_scores,
        avg_scores=avg_scores,
        coop_rates=coop_rates,
        match_scores=match_scores,
        match_coop=match_coop,
        n_rounds=n_rounds,
    )
