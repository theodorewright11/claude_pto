"""
dynamics.py — Update rules for belief propagation.

The core update rule is a weighted average of social influence:

    b_i' = b_i + (1 - resistance_i) * (social_target - b_i) + noise

where social_target is the weighted mean belief of i's neighbors, and the
edge weights are adjusted by homophily:

    w_ij_eff = w_ij * (1 - homophily + homophily * similarity(b_i, b_j))

Homophily means you weight the opinions of people who already agree with
you more highly. At homophily=1, you only really hear from people like you.
At homophily=0, all neighbors are weighted equally.

There is also an optional "anchor" force — a true external signal that
pushes all agents (or a subset) toward some ground truth. This models
evidence entering a system.
"""

from __future__ import annotations
import numpy as np
from .network import BeliefNetwork


def _effective_weight(base: float, b_self: float, b_other: float, homophily: float) -> float:
    """Scale edge weight by belief similarity when homophily > 0."""
    similarity = 1.0 - abs(b_self - b_other)
    return base * (1.0 - homophily + homophily * similarity)


def step(
    network: BeliefNetwork,
    noise_scale: float = 0.005,
    anchor: float | None = None,
    anchor_strength: float = 0.05,
    anchor_agents: set[int] | None = None,
) -> None:
    """
    Advance the simulation by one step. Updates are computed synchronously
    (all agents read the previous state, then all write).

    Parameters
    ----------
    network : BeliefNetwork
    noise_scale : float
        Std dev of Gaussian noise added to each update. Small noise prevents
        the system from freezing at unstable equilibria.
    anchor : float or None
        If provided, a gentle force pulling agents toward this "true" belief.
        Models the effect of evidence or ground truth entering the system.
    anchor_strength : float
        How strongly the anchor pulls (per step). 0.05 = 5% of the gap.
    anchor_agents : set[int] or None
        Which agents are exposed to the anchor. None = all agents.
    """
    new_beliefs: dict[int, float] = {}

    for agent_id, agent in network.agents.items():
        neighbors = list(network.graph.neighbors(agent_id))

        if neighbors:
            total_weight = 0.0
            weighted_sum = 0.0

            for nb_id in neighbors:
                nb_agent = network.agents[nb_id]
                base_w = network.graph[agent_id][nb_id].get("weight", 1.0)
                eff_w = _effective_weight(base_w, agent.belief, nb_agent.belief, network.homophily)
                weighted_sum += eff_w * nb_agent.belief
                total_weight += eff_w

            social_target = weighted_sum / total_weight if total_weight > 0 else agent.belief
        else:
            social_target = agent.belief

        delta = (1.0 - agent.resistance) * (social_target - agent.belief)
        delta += np.random.normal(0, noise_scale)

        # Apply anchor (external evidence)
        if anchor is not None:
            if anchor_agents is None or agent_id in anchor_agents:
                delta += anchor_strength * (anchor - agent.belief)

        new_beliefs[agent_id] = float(np.clip(agent.belief + delta, 0.0, 1.0))

    for agent_id, new_belief in new_beliefs.items():
        network.agents[agent_id].update(new_belief)

    network.step_count += 1


def run(
    network: BeliefNetwork,
    steps: int,
    noise_scale: float = 0.005,
    anchor: float | None = None,
    anchor_strength: float = 0.05,
    anchor_start_step: int = 0,
    anchor_agents: set[int] | None = None,
    callback=None,
) -> None:
    """
    Run the simulation for a given number of steps.

    callback: optional callable(network, step_index) called after each step.
    """
    for i in range(steps):
        active_anchor = anchor if i >= anchor_start_step else None
        step(
            network,
            noise_scale=noise_scale,
            anchor=active_anchor,
            anchor_strength=anchor_strength,
            anchor_agents=anchor_agents,
        )
        if callback:
            callback(network, i)
