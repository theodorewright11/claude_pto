"""
visualize.py — Matplotlib visualizations for belief networks.

Two primary outputs:
1. Network graph: nodes colored by belief, communities visible.
2. Belief evolution: per-community mean belief over time, with spread.

Both save to output/ and return the figure path.
"""

from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend (safe for all environments)
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx
from .network import BeliefNetwork

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Belief colormap: blue (disbelief=0) → gray (uncertain=0.5) → red (belief=1)
BELIEF_CMAP = mcolors.LinearSegmentedColormap.from_list(
    "belief",
    [(0.0, "#2166ac"),   # strong blue
     (0.35, "#92c5de"),  # light blue
     (0.5,  "#d9d9d9"),  # neutral gray
     (0.65, "#f4a582"),  # light red
     (1.0,  "#d6604d")], # strong red
)

# Community palette (up to 8 communities)
COMMUNITY_COLORS = [
    "#4477aa", "#ee6677", "#228833", "#ccbb44",
    "#66ccee", "#aa3377", "#bbbbbb", "#994455",
]


def _belief_to_color(belief: float) -> str:
    rgba = BELIEF_CMAP(float(belief))
    return mcolors.to_hex(rgba)


def _layout(network: BeliefNetwork):
    """
    Use spring layout, but seed it so results are reproducible.
    For multi-community networks, perturb initial positions to separate communities.
    """
    communities = network.communities()
    if len(communities) <= 1:
        return nx.spring_layout(network.graph, seed=42, k=1.5)

    # Give each community a different center to help initial separation
    centers = {}
    for i, comm in enumerate(communities):
        angle = 2 * np.pi * i / len(communities)
        centers[comm] = (np.cos(angle) * 2.0, np.sin(angle) * 2.0)

    pos = {}
    for agent in network.agents.values():
        cx, cy = centers[agent.community]
        pos[agent.id] = (
            cx + np.random.default_rng(agent.id).normal(0, 0.4),
            cy + np.random.default_rng(agent.id + 1000).normal(0, 0.4),
        )

    return nx.spring_layout(network.graph, pos=pos, seed=42, k=0.8, iterations=60)


def plot_network(network: BeliefNetwork, title: str, filename: str, step: int | None = None) -> str:
    """
    Draw the belief network. Nodes colored by belief value.
    Returns the saved file path.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")

    pos = _layout(network)

    node_colors = [_belief_to_color(network.agents[n].belief) for n in network.graph.nodes()]
    node_sizes = []
    for n in network.graph.nodes():
        deg = network.graph.degree(n)
        node_sizes.append(max(60, min(400, 60 + deg * 12)))

    # Draw edges
    nx.draw_networkx_edges(
        network.graph, pos, ax=ax,
        edge_color="#ffffff", alpha=0.06, width=0.5,
    )

    # Draw nodes
    nx.draw_networkx_nodes(
        network.graph, pos, ax=ax,
        node_color=node_colors, node_size=node_sizes,
        edgecolors="#ffffff", linewidths=0.3,
    )

    # Label key agents
    labeled = network.labeled_agents()
    if labeled:
        label_dict = {a.id: a.label for a in labeled}
        label_pos = {aid: (pos[aid][0], pos[aid][1] + 0.08) for aid in label_dict}
        nx.draw_networkx_labels(
            network.graph, label_pos, labels=label_dict, ax=ax,
            font_size=7, font_color="#ffffff", font_weight="bold",
        )

    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=BELIEF_CMAP, norm=plt.Normalize(0, 1))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, shrink=0.6, pad=0.02)
    cbar.set_label("Belief", color="#cccccc", fontsize=10)
    cbar.ax.yaxis.set_tick_params(color="#cccccc")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#cccccc")
    cbar.ax.set_facecolor("#1a1a2e")

    step_str = f" — step {step}" if step is not None else f" — step {network.step_count}"
    ax.set_title(f"{title}{step_str}", color="#ffffff", fontsize=13, pad=12)
    ax.axis("off")

    # Metrics annotation
    pol = network.polarization()
    ecs = network.echo_chamber_score()
    means = network.community_means()
    means_str = "  ".join(f"{c}: {v:.2f}" for c, v in means.items())
    annotation = f"polarization={pol:.3f}  echo={ecs:.3f}  |  {means_str}"
    ax.text(
        0.5, 0.01, annotation, transform=ax.transAxes,
        ha="center", va="bottom", color="#aaaaaa", fontsize=7,
    )

    path = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


def plot_belief_evolution(network: BeliefNetwork, title: str, filename: str) -> str:
    """
    Plot per-community mean belief over time, with ±1 std shading.
    Returns the saved file path.
    """
    fig, (ax_main, ax_metrics) = plt.subplots(
        2, 1, figsize=(11, 7), gridspec_kw={"height_ratios": [3, 1]}
    )
    fig.patch.set_facecolor("#1a1a2e")
    for ax in (ax_main, ax_metrics):
        ax.set_facecolor("#111128")
        ax.tick_params(colors="#cccccc")
        for spine in ax.spines.values():
            spine.set_edgecolor("#444466")

    communities = network.communities()
    community_history = network.community_history()

    # Also compute per-community std over time
    max_steps = max(len(v) for v in community_history.values())
    steps_range = list(range(max_steps))

    for i, comm in enumerate(communities):
        color = COMMUNITY_COLORS[i % len(COMMUNITY_COLORS)]
        means = community_history[comm]

        # Compute std at each step
        stds = []
        for s in steps_range:
            beliefs_at_s = [
                a.history[s] if s < len(a.history) else a.history[-1]
                for a in network.agents.values()
                if a.community == comm
            ]
            stds.append(float(np.std(beliefs_at_s)))

        means_arr = np.array(means)
        stds_arr = np.array(stds)

        ax_main.plot(steps_range, means_arr, color=color, linewidth=2, label=comm, alpha=0.95)
        ax_main.fill_between(
            steps_range,
            np.clip(means_arr - stds_arr, 0, 1),
            np.clip(means_arr + stds_arr, 0, 1),
            color=color, alpha=0.15,
        )

    ax_main.set_xlim(0, max_steps - 1)
    ax_main.set_ylim(-0.02, 1.02)
    ax_main.set_ylabel("Mean belief", color="#cccccc", fontsize=10)
    ax_main.set_title(title, color="#ffffff", fontsize=13)
    ax_main.axhline(0.5, color="#ffffff", alpha=0.2, linestyle="--", linewidth=1)
    ax_main.legend(
        loc="best", facecolor="#1a1a2e", edgecolor="#444466",
        labelcolor="#cccccc", fontsize=9,
    )
    ax_main.grid(True, color="#333355", linewidth=0.5, alpha=0.5)

    # Bottom panel: polarization and echo chamber score over time
    pol_over_time = []
    ecs_over_time = []
    for s in steps_range:
        beliefs = [
            (a.history[s] if s < len(a.history) else a.history[-1])
            for a in network.agents.values()
        ]
        beliefs_arr = np.array(beliefs)
        # Polarization
        deviations = (beliefs_arr - 0.5) ** 2
        pol_over_time.append(float(np.mean(deviations) * 4))

        # Echo chamber score
        diffs = []
        for uid, vid in network.graph.edges():
            bu = (network.agents[uid].history[s] if s < len(network.agents[uid].history)
                  else network.agents[uid].history[-1])
            bv = (network.agents[vid].history[s] if s < len(network.agents[vid].history)
                  else network.agents[vid].history[-1])
            diffs.append(abs(bu - bv))
        ecs_over_time.append(1.0 - float(np.mean(diffs)) if diffs else 0.0)

    ax_metrics.plot(steps_range, pol_over_time, color="#e88c30", linewidth=1.5, label="polarization")
    ax_metrics.plot(steps_range, ecs_over_time, color="#7ec8e3", linewidth=1.5, label="echo chamber score")
    ax_metrics.set_xlim(0, max_steps - 1)
    ax_metrics.set_ylim(0, 1.05)
    ax_metrics.set_xlabel("Step", color="#cccccc", fontsize=10)
    ax_metrics.set_ylabel("Score", color="#cccccc", fontsize=10)
    ax_metrics.legend(
        loc="best", facecolor="#1a1a2e", edgecolor="#444466",
        labelcolor="#cccccc", fontsize=8,
    )
    ax_metrics.grid(True, color="#333355", linewidth=0.5, alpha=0.5)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


def plot_before_after(
    network: BeliefNetwork,
    title: str,
    filename: str,
    initial_step: int = 0,
) -> str:
    """
    Side-by-side network snapshots: initial state vs. final state.
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor("#1a1a2e")

    pos = _layout(network)

    for ax, step, label in [(axes[0], initial_step, "Initial"), (axes[1], network.step_count - 1, "Final")]:
        ax.set_facecolor("#1a1a2e")

        beliefs_at_step = network.belief_at_step(step)
        node_colors = [_belief_to_color(beliefs_at_step[n]) for n in network.graph.nodes()]
        node_sizes = [max(60, min(300, 60 + network.graph.degree(n) * 10)) for n in network.graph.nodes()]

        nx.draw_networkx_edges(
            network.graph, pos, ax=ax,
            edge_color="#ffffff", alpha=0.05, width=0.5,
        )
        nx.draw_networkx_nodes(
            network.graph, pos, ax=ax,
            node_color=node_colors, node_size=node_sizes,
            edgecolors="#ffffff", linewidths=0.3,
        )

        # Label key agents
        labeled = network.labeled_agents()
        if labeled:
            label_dict = {a.id: a.label for a in labeled}
            label_pos = {aid: (pos[aid][0], pos[aid][1] + 0.1) for aid in label_dict}
            nx.draw_networkx_labels(
                network.graph, label_pos, labels=label_dict, ax=ax,
                font_size=7, font_color="#ffffff", font_weight="bold",
            )

        actual_step = step if step < network.step_count else network.step_count - 1
        ax.set_title(f"{label} (step {actual_step})", color="#ffffff", fontsize=11)
        ax.axis("off")

    fig.suptitle(title, color="#ffffff", fontsize=14, y=1.02)

    # Shared colorbar
    sm = plt.cm.ScalarMappable(cmap=BELIEF_CMAP, norm=plt.Normalize(0, 1))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=axes, shrink=0.7, pad=0.02)
    cbar.set_label("Belief", color="#cccccc", fontsize=10)
    cbar.ax.yaxis.set_tick_params(color="#cccccc")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#cccccc")

    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return path
