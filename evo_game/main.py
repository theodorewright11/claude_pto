"""
evo_game/main.py — Evolutionary Game Theory Lab

Usage:
    python -m evo_game.main               # everything
    python -m evo_game.main --all
    python -m evo_game.main --replicator  # replicator dynamics only
    python -m evo_game.main --spatial     # spatial games only
    python -m evo_game.main --tournament  # iterated PD tournament only
"""

import argparse
import os
import time

from evo_game.games import prisoner_dilemma, hawk_dove, stag_hunt, rock_paper_scissors
from evo_game.replicator import multi_simulate, grid_2strategy, grid_simplex_3strategy
from evo_game.spatial import run_spatial, nowak_may_pd
from evo_game.tournament import run_tournament
from evo_game.visualize import (
    plot_2strategy_replicator,
    plot_rps_replicator,
    plot_spatial_snapshots,
    plot_tournament_results,
    save_figure,
)

try:
    from rich.console import Console
    from rich.panel import Panel
    RICH = True
except ImportError:
    RICH = False


OUTPUT_DIR = os.path.join("output", "evo_game")
console = Console() if RICH else None


def status(msg: str):
    if RICH:
        console.print(f"  [dim cyan]→[/dim cyan]  {msg}")
    else:
        print(f"  →  {msg}")


def header(msg: str):
    if RICH:
        console.print(f"\n[bold white]{msg}[/bold white]")
    else:
        print(f"\n{msg}")


def done(path: str, elapsed: float):
    name = os.path.basename(path)
    if RICH:
        console.print(f"     [green]✓[/green]  {name}  [dim]({elapsed:.1f}s)[/dim]")
    else:
        print(f"     ✓  {name}  ({elapsed:.1f}s)")


# ── Replicator dynamics ───────────────────────────────────────────────────────

def run_replicator():
    header("Replicator dynamics")

    # Three 2-strategy games
    two_strat_games = [
        prisoner_dilemma(),
        hawk_dove(),
        stag_hunt(),
    ]

    for game in two_strat_games:
        status(f"simulating {game.name} …")
        t0 = time.time()
        ics = grid_2strategy(n=9)
        results = multi_simulate(game, ics, t_end=60.0)
        fig = plot_2strategy_replicator(game, results)
        fname = "replicator_" + game.name.lower().split()[0].replace("'", "") + ".png"
        # Cleaner filenames
        fname_map = {
            "Prisoner's Dilemma": "replicator_pd.png",
            "Hawk-Dove":          "replicator_hawkdove.png",
            "Stag Hunt":          "replicator_staghunt.png",
        }
        fname = fname_map.get(game.name, fname)
        path = save_figure(fig, fname, OUTPUT_DIR)
        done(path, time.time() - t0)

    # Rock-Paper-Scissors
    status("simulating Rock-Paper-Scissors (simplex orbits) …")
    t0 = time.time()
    rps = rock_paper_scissors()
    ics_3 = grid_simplex_3strategy(n_per_edge=8)
    results_rps = multi_simulate(rps, ics_3, t_end=80.0)
    # Pick one mid-range IC for time series panel
    mid = results_rps[len(results_rps) // 2]
    fig = plot_rps_replicator(rps, results_rps, single_result=mid)
    path = save_figure(fig, "replicator_rps.png", OUTPUT_DIR)
    done(path, time.time() - t0)


# ── Spatial games ─────────────────────────────────────────────────────────────

def run_spatial_games():
    header("Spatial evolutionary games")

    SNAP_STEPS = (0, 1, 5, 20, 50, 100, 200)

    # Nowak-May Prisoner's Dilemma
    status("running spatial Prisoner's Dilemma  (150×150, 200 steps) …")
    t0 = time.time()
    pd_game = nowak_may_pd(b=1.65)
    times, snapshots, freq_hist = run_spatial(
        pd_game, N=150, n_steps=200, snapshot_steps=SNAP_STEPS, seed=7
    )
    fig = plot_spatial_snapshots(pd_game, times, snapshots, freq_hist)
    path = save_figure(fig, "spatial_pd.png", OUTPUT_DIR)
    done(path, time.time() - t0)

    # Spatial Rock-Paper-Scissors
    status("running spatial Rock-Paper-Scissors  (150×150, 200 steps) …")
    t0 = time.time()
    rps = rock_paper_scissors()
    times_r, snaps_r, freq_r = run_spatial(
        rps, N=150, n_steps=200, snapshot_steps=SNAP_STEPS, seed=13
    )
    fig = plot_spatial_snapshots(rps, times_r, snaps_r, freq_r)
    path = save_figure(fig, "spatial_rps.png", OUTPUT_DIR)
    done(path, time.time() - t0)


# ── Tournament ────────────────────────────────────────────────────────────────

def run_tournament_section():
    header("Iterated Prisoner's Dilemma tournament")
    status("running round-robin (9 strategies × 150 rounds × 5 reps) …")
    t0 = time.time()
    result = run_tournament(n_rounds=150, n_reps=5, seed=0)
    fig = plot_tournament_results(result)
    path = save_figure(fig, "tournament.png", OUTPUT_DIR)
    done(path, time.time() - t0)

    # Print leaderboard
    order = sorted(range(len(result.names)), key=lambda i: -result.total_scores[i])
    if RICH:
        console.print("\n  [dim]Leaderboard:[/dim]")
        for rank, i in enumerate(order, 1):
            console.print(
                f"    [dim]{rank}.[/dim]  {result.names[i]:<22s}  "
                f"score={result.total_scores[i]:6.0f}  "
                f"coop={result.coop_rates[i]:.0%}"
            )
    else:
        print("\n  Leaderboard:")
        for rank, i in enumerate(order, 1):
            print(f"    {rank}.  {result.names[i]:<22s}  "
                  f"score={result.total_scores[i]:6.0f}  "
                  f"coop={result.coop_rates[i]:.0%}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Evolutionary Game Theory Lab")
    parser.add_argument("--all",        action="store_true")
    parser.add_argument("--replicator", action="store_true")
    parser.add_argument("--spatial",    action="store_true")
    parser.add_argument("--tournament", action="store_true")
    args = parser.parse_args()

    run_all = args.all or not any([args.replicator, args.spatial, args.tournament])

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if RICH:
        console.print(Panel.fit(
            "[bold white]Evolutionary Game Theory Lab[/bold white]\n"
            "[dim]replicator dynamics  ·  spatial cooperation  ·  strategy tournament[/dim]",
            border_style="dim cyan",
        ))
    else:
        print("=== Evolutionary Game Theory Lab ===")

    total_start = time.time()

    if run_all or args.replicator:
        run_replicator()
    if run_all or args.spatial:
        run_spatial_games()
    if run_all or args.tournament:
        run_tournament_section()

    elapsed = time.time() - total_start
    if RICH:
        console.print(
            f"\n[bold green]Done.[/bold green]  "
            f"Outputs → [cyan]{OUTPUT_DIR}[/cyan]  "
            f"[dim]({elapsed:.1f}s total)[/dim]\n"
        )
    else:
        print(f"\nDone. Outputs → {OUTPUT_DIR}  ({elapsed:.1f}s total)\n")


if __name__ == "__main__":
    main()
