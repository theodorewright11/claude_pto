"""
scenarios.py — Pre-built simulation scenarios.

Each scenario returns a (BeliefNetwork, run_config) tuple where run_config
is a dict of kwargs to pass to dynamics.run().

The five scenarios are:

1. THE LONG SLIDE — A homogeneous moderate community gradually polarizes.
   Demonstrates how homophily alone, over time, can sort a fair-minded
   population into entrenched camps without any bad actors.

2. THE BRIDGER — Two polarized communities connected by one agent.
   Does the bridge hold? Can one person connect two worlds, or do they
   get pulled toward one side?

3. THE EVIDENCE — An echo chamber encounters external evidence.
   Models how ground truth enters a closed system: slowly, imperfectly,
   and dependent on where in the network it enters.

4. THE CASCADE — An influencer changes their mind.
   In a scale-free network (power law degree distribution), what happens
   when a high-degree hub reverses their position?

5. THE RECONSTRUCTION — An agent finds new information.
   A single agent embedded in a strong-belief community starts questioning.
   They form new connections. Their belief updates. What happens to the
   community around them?
"""

from __future__ import annotations
import numpy as np
import networkx as nx
from .network import Agent, BeliefNetwork


def _make_agents(beliefs, resistances, communities, labels=None):
    agents = []
    for i, (b, r, c) in enumerate(zip(beliefs, resistances, communities)):
        label = labels.get(i) if labels else None
        agents.append(Agent(id=i, belief=b, resistance=r, community=c, label=label))
    return agents


# ------------------------------------------------------------------
# 1. The Long Slide
# ------------------------------------------------------------------

def scenario_long_slide(n=80, homophily=0.7, seed=42) -> tuple[BeliefNetwork, dict]:
    """
    80 agents, small-world topology, starting beliefs near 0.5.
    High homophily causes slow drift toward extremes.
    """
    rng = np.random.default_rng(seed)
    g = nx.watts_strogatz_graph(n, k=6, p=0.15, seed=seed)

    beliefs = rng.normal(0.5, 0.12, n).clip(0.1, 0.9)
    resistances = rng.uniform(0.05, 0.2, n)
    communities = ["community"] * n

    agents = _make_agents(beliefs, resistances, communities)
    edges = [(u, v) for u, v in g.edges()]

    network = BeliefNetwork(agents, edges, homophily=homophily)
    run_config = {
        "steps": 150,
        "noise_scale": 0.008,
    }
    return network, run_config


# ------------------------------------------------------------------
# 2. The Bridger
# ------------------------------------------------------------------

def scenario_bridger(homophily=0.65, seed=42) -> tuple[BeliefNetwork, dict]:
    """
    Two communities of 30 agents each, deeply polarized.
    One agent sits between them — the Bridger.
    """
    rng = np.random.default_rng(seed)
    n_per = 30

    # Community A: believes (high)
    beliefs_a = rng.normal(0.82, 0.06, n_per).clip(0.65, 0.99)
    # Community B: disbelieves (low)
    beliefs_b = rng.normal(0.18, 0.06, n_per).clip(0.01, 0.35)

    all_beliefs = np.concatenate([beliefs_a, beliefs_b, [0.5]])
    resistances = np.concatenate([
        rng.uniform(0.1, 0.25, n_per),
        rng.uniform(0.1, 0.25, n_per),
        [0.05],  # bridger is open-minded (low resistance)
    ])
    communities = ["believers"] * n_per + ["skeptics"] * n_per + ["bridge"]
    labels = {n_per * 2: "The Bridger"}

    agents = _make_agents(all_beliefs, resistances, communities, labels=labels)
    bridger_id = n_per * 2

    # Dense connections within each community
    g_a = nx.watts_strogatz_graph(n_per, k=4, p=0.2, seed=seed)
    g_b = nx.watts_strogatz_graph(n_per, k=4, p=0.2, seed=seed + 1)

    edges = []
    for u, v in g_a.edges():
        edges.append((u, v, 1.0))
    for u, v in g_b.edges():
        edges.append((u + n_per, v + n_per, 1.0))

    # Bridger connects to both communities (equal weight)
    for i in range(5):
        edges.append((bridger_id, i, 0.8))
        edges.append((bridger_id, n_per + i, 0.8))

    network = BeliefNetwork(agents, edges, homophily=homophily)
    run_config = {
        "steps": 120,
        "noise_scale": 0.004,
    }
    return network, run_config


# ------------------------------------------------------------------
# 3. The Evidence
# ------------------------------------------------------------------

def scenario_evidence(homophily=0.6, seed=42) -> tuple[BeliefNetwork, dict]:
    """
    An echo chamber (n=60) with strong shared belief encounters
    external evidence (anchor=0.15, meaning the truth is low-belief).
    Evidence enters through 5 peripheral agents.
    """
    rng = np.random.default_rng(seed)
    n = 60

    # Echo chamber: everyone believes strongly
    beliefs = rng.normal(0.85, 0.05, n).clip(0.7, 0.99)
    resistances = rng.uniform(0.15, 0.35, n)
    communities = ["echo_chamber"] * n

    # Sort by degree in the graph — evidence enters through peripheral nodes
    g = nx.barabasi_albert_graph(n, m=3, seed=seed)
    degrees = dict(g.degree())
    sorted_by_degree = sorted(degrees.items(), key=lambda x: x[1])
    peripheral_agents = {idx for idx, _ in sorted_by_degree[:5]}  # 5 lowest-degree nodes

    labels = {idx: f"evidence_entry_{k}" for k, idx in enumerate(peripheral_agents)}

    agents = _make_agents(beliefs, resistances, communities, labels=labels)
    edges = [(u, v) for u, v in g.edges()]

    network = BeliefNetwork(agents, edges, homophily=homophily)
    run_config = {
        "steps": 200,
        "noise_scale": 0.003,
        "anchor": 0.15,        # true belief is low
        "anchor_strength": 0.04,
        "anchor_start_step": 20,  # evidence arrives after 20 steps
        "anchor_agents": peripheral_agents,
    }
    return network, run_config


# ------------------------------------------------------------------
# 4. The Cascade
# ------------------------------------------------------------------

def scenario_cascade(homophily=0.4, seed=42) -> tuple[BeliefNetwork, dict]:
    """
    Scale-free network. The highest-degree hub (an influencer)
    starts with high belief (0.85) and then flips to low belief (0.15)
    mid-simulation. Watch how fast it cascades.

    We implement the flip by giving the influencer high external anchor
    after step 30.
    """
    rng = np.random.default_rng(seed)
    n = 100

    g = nx.barabasi_albert_graph(n, m=3, seed=seed)
    degrees = dict(g.degree())
    influencer_id = max(degrees, key=lambda x: degrees[x])

    beliefs = rng.normal(0.75, 0.1, n).clip(0.5, 0.99)
    beliefs[influencer_id] = 0.88  # influencer starts as a true believer

    resistances = rng.uniform(0.05, 0.2, n)
    resistances[influencer_id] = 0.05  # influencer is responsive to new info

    communities = ["network"] * n
    labels = {influencer_id: "The Influencer"}

    agents = _make_agents(beliefs, resistances, communities, labels=labels)
    edges = [(u, v) for u, v in g.edges()]

    network = BeliefNetwork(agents, edges, homophily=homophily)

    # The influencer encounters strong contradicting evidence alone
    run_config = {
        "steps": 150,
        "noise_scale": 0.004,
        "anchor": 0.1,             # strong contradicting evidence
        "anchor_strength": 0.25,   # influencer is strongly swayed
        "anchor_start_step": 30,
        "anchor_agents": {influencer_id},
    }
    return network, run_config


# ------------------------------------------------------------------
# 5. The Reconstruction
# ------------------------------------------------------------------

def scenario_reconstruction(homophily=0.55, seed=42) -> tuple[BeliefNetwork, dict]:
    """
    One agent (The Questioner) embedded in a tight belief community.
    Starting at step 0, they begin questioning (low-strength external signal).
    At step 40, they form new connections to a different community.

    This is modeled by splitting into two phases:
    - Phase 1 (steps 0-39): Questioner gets slight evidence signal
    - Phase 2 (steps 40-140): Questioner gains 5 new connections to
      a community with different beliefs

    Returns (network, run_config) for phase 1.
    The scenario runner handles phase 2 directly via a callback.
    """
    rng = np.random.default_rng(seed)
    n_community = 45
    n_outside = 20

    # Tight belief community
    beliefs_comm = rng.normal(0.85, 0.04, n_community).clip(0.72, 0.97)
    resistances_comm = rng.uniform(0.2, 0.35, n_community)

    # The Questioner — starts identical to their community
    questioner_id = 0
    beliefs_comm[questioner_id] = 0.83
    resistances_comm[questioner_id] = 0.08  # very open-minded

    # Outside community (lower belief)
    beliefs_out = rng.normal(0.25, 0.07, n_outside).clip(0.1, 0.45)
    resistances_out = rng.uniform(0.1, 0.25, n_outside)

    all_beliefs = np.concatenate([beliefs_comm, beliefs_out])
    all_resistances = np.concatenate([resistances_comm, resistances_out])
    all_communities = ["tight_community"] * n_community + ["outside"] * n_outside
    labels = {questioner_id: "The Questioner"}

    agents = _make_agents(all_beliefs, all_resistances, all_communities, labels=labels)

    g_comm = nx.watts_strogatz_graph(n_community, k=5, p=0.1, seed=seed)
    g_out = nx.watts_strogatz_graph(n_outside, k=4, p=0.2, seed=seed + 1)

    edges = []
    for u, v in g_comm.edges():
        edges.append((u, v, 1.0))
    for u, v in g_out.edges():
        edges.append((u + n_community, v + n_community, 1.0))
    # No initial cross-community connections

    network = BeliefNetwork(agents, edges, homophily=homophily)

    # The phase transition: at step 40, questioner forms new connections
    new_connections = [(questioner_id, n_community + i, 0.6) for i in range(5)]

    run_config = {
        "steps": 150,
        "noise_scale": 0.004,
        "anchor": 0.2,             # quiet questioning signal
        "anchor_strength": 0.03,
        "anchor_start_step": 0,
        "anchor_agents": {questioner_id},
        "_phase2_step": 40,        # custom key for scenario runner
        "_phase2_edges": new_connections,
    }
    return network, run_config


# ------------------------------------------------------------------
# Registry
# ------------------------------------------------------------------

SCENARIOS = {
    "long_slide": {
        "fn": scenario_long_slide,
        "name": "The Long Slide",
        "description": "A moderate community polarizes slowly through homophily alone.",
        "question": "How does a fair-minded community become entrenched without bad actors?",
    },
    "bridger": {
        "fn": scenario_bridger,
        "name": "The Bridger",
        "description": "Two polarized communities share one connecting agent.",
        "question": "Can one person genuinely bridge two worlds?",
    },
    "evidence": {
        "fn": scenario_evidence,
        "name": "The Evidence",
        "description": "Ground truth enters an echo chamber through peripheral agents.",
        "question": "How does evidence propagate (or fail to propagate) through closed systems?",
    },
    "cascade": {
        "fn": scenario_cascade,
        "name": "The Cascade",
        "description": "A high-degree influencer changes their belief mid-simulation.",
        "question": "How fast does a hub's belief change cascade through a scale-free network?",
    },
    "reconstruction": {
        "fn": scenario_reconstruction,
        "name": "The Reconstruction",
        "description": "An embedded agent begins questioning, then forms new connections.",
        "question": "What happens to a community when one member finds new information?",
    },
}
