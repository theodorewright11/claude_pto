"""
main.py — Interactive CLI for the Epistemic Propagation Engine.

Run with:
    python belief_engine/main.py

Or run a specific scenario directly:
    python belief_engine/main.py --scenario cascade
    python belief_engine/main.py --all
"""

from __future__ import annotations
import sys
import os
import argparse
import time

# Make sure parent dir is in path when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Force UTF-8 output on Windows so box-drawing characters work
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
import io
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Prompt
from rich.text import Text
from rich.rule import Rule
from rich import box

from belief_engine import dynamics, visualize
from belief_engine.scenarios import SCENARIOS
from belief_engine.network import BeliefNetwork

console = Console(force_terminal=True, highlight=False)

HEADER = """
+-------------------------------------------------------+
|         E P I S T E M I C   E N G I N E              |
|    A simulation of how beliefs spread and change      |
+-------------------------------------------------------+
"""


def render_header():
    console.print(Text(HEADER, style="bold blue"))
    console.print(
        "Modeling belief propagation through social networks.\n"
        "Each agent holds a belief in [0, 1] and updates based\n"
        "on neighbors, weighted by homophily and resistance.\n",
        style="dim"
    )


def render_scenario_menu() -> str:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("Key", style="bold yellow", width=16)
    table.add_column("Scenario", style="bold white", width=22)
    table.add_column("Question", style="dim white")

    for key, info in SCENARIOS.items():
        table.add_row(key, info["name"], info["question"])

    console.print(table)
    console.print()

    choice = Prompt.ask(
        "[cyan]Select scenario[/cyan]",
        choices=list(SCENARIOS.keys()) + ["all", "quit"],
        default="long_slide",
    )
    return choice


def render_summary(network: BeliefNetwork, scenario_name: str):
    s = network.summary()
    console.print(Rule(f"[bold white]{scenario_name}[/bold white] — Final State", style="blue"))

    table = Table(box=box.SIMPLE_HEAD, show_header=False)
    table.add_column("Metric", style="dim cyan", width=26)
    table.add_column("Value", style="bold white")

    table.add_row("Steps simulated", str(s["steps"]))
    table.add_row("Agents", str(s["agents"]))
    table.add_row("Connections", str(s["edges"]))
    table.add_row("Overall mean belief", f"{s['overall_mean']:.4f}")
    table.add_row(
        "Polarization",
        f"{s['polarization']:.4f}  " + _bar(s["polarization"]),
    )
    table.add_row(
        "Echo chamber score",
        f"{s['echo_chamber_score']:.4f}  " + _bar(s["echo_chamber_score"]),
    )

    for comm, mean in s["community_means"].items():
        table.add_row(f"  [{comm}] mean belief", f"{mean:.4f}  " + _bar(mean))

    console.print(table)


def _bar(value: float, width: int = 20) -> str:
    filled = int(round(value * width))
    empty = width - filled
    return f"[blue]{'#' * filled}[/blue][dim]{'.' * empty}[/dim]"


def run_scenario(key: str, verbose: bool = True) -> dict:
    info = SCENARIOS[key]
    fn = info["fn"]

    if verbose:
        console.print()
        console.print(Panel(
            f"[bold]{info['name']}[/bold]\n\n"
            f"[dim]{info['description']}[/dim]\n\n"
            f"[italic cyan]Question: {info['question']}[/italic cyan]",
            border_style="blue",
        ))
        console.print()

    network, run_config = fn()

    steps = run_config.pop("steps")
    phase2_step = run_config.pop("_phase2_step", None)
    phase2_edges = run_config.pop("_phase2_edges", None)

    slug = key.replace(" ", "_")

    # Save initial network snapshot
    if verbose:
        console.print(f"[dim]Saving initial network snapshot...[/dim]")
    init_path = visualize.plot_network(
        network, title=info["name"], filename=f"{slug}_network_initial.png", step=0
    )

    # Run simulation
    def make_callback(phase2_step, phase2_edges, applied):
        def callback(net, step_idx):
            if phase2_step and step_idx == phase2_step - 1 and not applied[0]:
                applied[0] = True
                # Add new connections for The Reconstruction
                for edge in phase2_edges:
                    u, v, w = edge
                    net.graph.add_edge(u, v, weight=w)
                if verbose:
                    console.print(
                        f"  [yellow]-> Step {step_idx + 1}: New connections formed.[/yellow]"
                    )
        return callback

    applied = [False]
    callback = make_callback(phase2_step, phase2_edges, applied) if phase2_step else None

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"Running {info['name']}...", total=steps)

        def wrapped_callback(net, step_idx):
            if callback:
                callback(net, step_idx)
            progress.update(task, advance=1)

        dynamics.run(network, steps=steps, callback=wrapped_callback, **run_config)

    # Save final snapshots
    if verbose:
        console.print(f"[dim]Saving visualizations...[/dim]")

    final_path = visualize.plot_network(
        network, title=info["name"], filename=f"{slug}_network_final.png"
    )
    before_after_path = visualize.plot_before_after(
        network, title=info["name"], filename=f"{slug}_before_after.png"
    )
    evolution_path = visualize.plot_belief_evolution(
        network, title=f"{info['name']} — Belief Evolution",
        filename=f"{slug}_evolution.png"
    )

    if verbose:
        render_summary(network, info["name"])
        console.print()
        console.print(f"[green]Saved:[/green]")
        for p in [init_path, final_path, before_after_path, evolution_path]:
            console.print(f"  [dim]{p}[/dim]")
        console.print()

    return {
        "network": network,
        "paths": [init_path, final_path, before_after_path, evolution_path],
    }


def run_all():
    console.print(Rule("[bold]Running all scenarios[/bold]", style="blue"))
    results = {}
    for key in SCENARIOS:
        results[key] = run_scenario(key, verbose=True)
        console.print()
    console.print(Rule("[bold green]All scenarios complete[/bold green]", style="green"))
    return results


def main():
    parser = argparse.ArgumentParser(description="Epistemic Propagation Engine")
    parser.add_argument("--scenario", choices=list(SCENARIOS.keys()), help="Run specific scenario")
    parser.add_argument("--all", action="store_true", help="Run all scenarios")
    args = parser.parse_args()

    render_header()

    if args.all:
        run_all()
    elif args.scenario:
        run_scenario(args.scenario)
    else:
        while True:
            choice = render_scenario_menu()
            if choice == "quit":
                console.print("\n[dim]See output/ for saved visualizations.[/dim]")
                break
            elif choice == "all":
                run_all()
            else:
                run_scenario(choice)
                console.print()
                again = Prompt.ask("[cyan]Run another scenario?[/cyan]", choices=["yes", "no"], default="yes")
                if again == "no":
                    console.print("\n[dim]See output/ for saved visualizations.[/dim]")
                    break


if __name__ == "__main__":
    main()
