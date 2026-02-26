"""
network.py — Core data structures for the epistemic propagation engine.

An Agent holds a belief (a float in [0, 1]) and a history of that belief
over time. A BeliefNetwork wraps a networkx graph and gives you the
semantic operations you actually care about: community-level averages,
belief distributions, polarization metrics.
"""

from __future__ import annotations
import numpy as np
import networkx as nx
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Agent:
    id: int
    belief: float           # 0 = strong disbelief, 1 = strong belief, 0.5 = uncertain
    resistance: float       # [0, 1] — how hard it is to move this agent
    community: str          # label for grouping / visualization
    label: Optional[str] = None  # human-readable name for key agents
    history: list = field(default_factory=list)

    def __post_init__(self):
        self.belief = float(np.clip(self.belief, 0.0, 1.0))
        self.history.append(self.belief)

    def update(self, new_belief: float):
        self.belief = float(np.clip(new_belief, 0.0, 1.0))
        self.history.append(self.belief)

    @property
    def stance(self) -> str:
        if self.belief < 0.2:
            return "strong disbelief"
        elif self.belief < 0.4:
            return "skeptical"
        elif self.belief < 0.6:
            return "uncertain"
        elif self.belief < 0.8:
            return "inclined"
        else:
            return "strong belief"


class BeliefNetwork:
    """
    A social network where each node is an Agent with a belief value.

    homophily: float in [0, 1]
        How much agents weight the opinions of those who agree with them.
        0 = purely structural (weights only), 1 = fully homophilic.

    The graph stores edge weights as 'weight' (default 1.0).
    """

    def __init__(self, agents: list[Agent], edges: list[tuple], homophily: float = 0.5):
        self.agents = {a.id: a for a in agents}
        self.homophily = homophily
        self.step_count = 0

        self.graph = nx.Graph()
        for agent in agents:
            self.graph.add_node(agent.id)
        for edge in edges:
            if len(edge) == 3:
                u, v, w = edge
            else:
                u, v = edge
                w = 1.0
            self.graph.add_edge(u, v, weight=w)

    # ------------------------------------------------------------------
    # Belief queries
    # ------------------------------------------------------------------

    def belief(self, agent_id: int) -> float:
        return self.agents[agent_id].belief

    def all_beliefs(self) -> list[float]:
        return [a.belief for a in self.agents.values()]

    def community_beliefs(self) -> dict[str, list[float]]:
        result: dict[str, list[float]] = {}
        for agent in self.agents.values():
            result.setdefault(agent.community, []).append(agent.belief)
        return result

    def community_means(self) -> dict[str, float]:
        return {c: float(np.mean(beliefs)) for c, beliefs in self.community_beliefs().items()}

    def community_stds(self) -> dict[str, float]:
        return {c: float(np.std(beliefs)) for c, beliefs in self.community_beliefs().items()}

    # ------------------------------------------------------------------
    # Network metrics
    # ------------------------------------------------------------------

    def polarization(self) -> float:
        """
        Bimodality coefficient — how polarized is the belief distribution?
        Returns a value in roughly [0, 1]. High values = more polarized.
        Based on the variance of beliefs relative to a uniform distribution.
        """
        beliefs = np.array(self.all_beliefs())
        if len(beliefs) < 2:
            return 0.0
        # Coefficient of variation of squared deviation from 0.5
        deviations = (beliefs - 0.5) ** 2
        return float(np.mean(deviations) * 4)  # scaled so uniform=0, fully polarized=1

    def echo_chamber_score(self) -> float:
        """
        Mean absolute belief difference across edges, subtracted from 1.
        High score = agents are mostly connected to like-minded others.
        """
        if self.graph.number_of_edges() == 0:
            return 0.0
        diffs = []
        for u, v in self.graph.edges():
            diffs.append(abs(self.agents[u].belief - self.agents[v].belief))
        return 1.0 - float(np.mean(diffs))

    def belief_at_step(self, step: int) -> dict[int, float]:
        """Return each agent's belief at a given historical step."""
        result = {}
        for aid, agent in self.agents.items():
            if step < len(agent.history):
                result[aid] = agent.history[step]
            else:
                result[aid] = agent.history[-1]
        return result

    def community_history(self) -> dict[str, list[float]]:
        """Per-community mean belief at each recorded step."""
        communities = {a.community for a in self.agents.values()}
        history: dict[str, list[float]] = {c: [] for c in communities}

        max_steps = max(len(a.history) for a in self.agents.values())
        for step in range(max_steps):
            by_community: dict[str, list[float]] = {c: [] for c in communities}
            for agent in self.agents.values():
                b = agent.history[step] if step < len(agent.history) else agent.history[-1]
                by_community[agent.community].append(b)
            for c in communities:
                history[c].append(float(np.mean(by_community[c])))
        return history

    def communities(self) -> list[str]:
        return sorted({a.community for a in self.agents.values()})

    def agents_in_community(self, community: str) -> list[Agent]:
        return [a for a in self.agents.values() if a.community == community]

    def labeled_agents(self) -> list[Agent]:
        return [a for a in self.agents.values() if a.label is not None]

    def summary(self) -> dict:
        means = self.community_means()
        return {
            "steps": self.step_count,
            "agents": len(self.agents),
            "edges": self.graph.number_of_edges(),
            "overall_mean": float(np.mean(self.all_beliefs())),
            "polarization": self.polarization(),
            "echo_chamber_score": self.echo_chamber_score(),
            "community_means": means,
        }
