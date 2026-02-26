"""
chaos/main.py — Deterministic Chaos Explorer

Generates all visualizations and saves them to output/chaos/.

Usage:
    python chaos/main.py
    python chaos/main.py --all          (same as default)
    python chaos/main.py --lorenz       (Lorenz attractor only)
    python chaos/main.py --rossler      (Rössler attractor only)
    python chaos/main.py --clifford     (Clifford attractors only)
    python chaos/main.py --logistic     (logistic map only)
"""

import argparse
import os
import sys
import time

import numpy as np

from chaos.attractors import (
    LorenzParams, RosslerParams,
    CLIFFORD_PRESETS, DEJONG_PRESETS,
)
from chaos.numerics import integrate, iterate_map, logistic_bifurcation
from chaos.visualize import (
    plot_lorenz_3d,
    plot_2d_projection,
    plot_sensitivity,
    plot_density,
    plot_bifurcation,
    save_figure,
)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    from rich import print as rprint
    RICH = True
except ImportError:
    RICH = False


OUTPUT_DIR = os.path.join("output", "chaos")

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


def run_lorenz():
    header("Lorenz attractor")
    lorenz = LorenzParams()

    # Main trajectory — long run
    status("integrating trajectory  (100 000 steps, dt=0.01) …")
    t0 = time.time()
    states = integrate(lorenz, np.array([1.0, 1.0, 1.5]), n_steps=100_000, dt=0.01)
    status(f"integration complete  ({time.time()-t0:.1f}s)")

    t0 = time.time()
    fig = plot_lorenz_3d(states, title="Lorenz Attractor  (σ=10, ρ=28, β=8/3)")
    path = save_figure(fig, "lorenz_3d.png", OUTPUT_DIR)
    done(path, time.time() - t0)

    t0 = time.time()
    fig = plot_2d_projection(states, title="Lorenz — X/Z Projection",
                             xi=0, yi=2, xlabel="X", ylabel="Z")
    path = save_figure(fig, "lorenz_xz.png", OUTPUT_DIR)
    done(path, time.time() - t0)

    t0 = time.time()
    fig = plot_2d_projection(states, title="Lorenz — X/Y Projection",
                             xi=0, yi=1, xlabel="X", ylabel="Y")
    path = save_figure(fig, "lorenz_xy.png", OUTPUT_DIR)
    done(path, time.time() - t0)

    # Sensitivity to initial conditions
    status("running sensitivity demo (two trajectories, ε = 10⁻⁸) …")
    t0 = time.time()
    s0a = np.array([1.0, 1.0, 1.5])
    s0b = np.array([1.0 + 1e-8, 1.0, 1.5])
    traj_a = integrate(lorenz, s0a, n_steps=8_000, dt=0.01)
    traj_b = integrate(lorenz, s0b, n_steps=8_000, dt=0.01)
    fig = plot_sensitivity(traj_a, traj_b, title="Butterfly Effect — Lorenz Attractor")
    path = save_figure(fig, "lorenz_sensitivity.png", OUTPUT_DIR)
    done(path, time.time() - t0)


def run_rossler():
    header("Rössler attractor")
    rossler = RosslerParams()

    status("integrating trajectory (80 000 steps, dt=0.05) …")
    t0 = time.time()
    states = integrate(rossler, np.array([1.0, 1.0, 1.0]), n_steps=80_000, dt=0.05)
    status(f"integration complete  ({time.time()-t0:.1f}s)")

    for (xi, yi, xl, yl, suffix) in [
        (0, 1, "X", "Y", "xy"),
        (0, 2, "X", "Z", "xz"),
    ]:
        t0 = time.time()
        fig = plot_2d_projection(
            states,
            title=f"Rössler Attractor — {xl}/{yl} Projection  (a=0.2, b=0.2, c=5.7)",
            xi=xi, yi=yi, xlabel=xl, ylabel=yl,
        )
        path = save_figure(fig, f"rossler_{suffix}.png", OUTPUT_DIR)
        done(path, time.time() - t0)


def run_clifford():
    header("Clifford attractors  (density maps, 2 M points each)")
    N = 2_000_000
    for preset in CLIFFORD_PRESETS:
        status(f"iterating '{preset.name}'  (a={preset.a}, b={preset.b}, "
               f"c={preset.c}, d={preset.d}) …")
        t0 = time.time()
        x, y = iterate_map(preset, 0.0, 0.0, N)
        fig = plot_density(
            x, y,
            title=(f"Clifford Attractor — {preset.name}\n"
                   f"a={preset.a}  b={preset.b}  c={preset.c}  d={preset.d}"),
            cmap=preset.cmap,
        )
        fname = f"clifford_{preset.name.lower()}.png"
        path = save_figure(fig, fname, OUTPUT_DIR)
        done(path, time.time() - t0)


def run_logistic():
    header("Logistic map — route to chaos")
    status("sweeping r ∈ [2.5, 4.0], 3 000 values, 300 iterates each …")
    t0 = time.time()
    r_vals, x_vals = logistic_bifurcation(
        r_min=2.5, r_max=4.0, n_r=3000, n_iter=300, n_transient=500
    )
    fig = plot_bifurcation(r_vals, x_vals,
                           title="Logistic Map — Bifurcation Diagram (route to chaos)")
    path = save_figure(fig, "logistic_bifurcation.png", OUTPUT_DIR)
    done(path, time.time() - t0)


def main():
    parser = argparse.ArgumentParser(description="Deterministic chaos visualizer")
    parser.add_argument("--all",      action="store_true")
    parser.add_argument("--lorenz",   action="store_true")
    parser.add_argument("--rossler",  action="store_true")
    parser.add_argument("--clifford", action="store_true")
    parser.add_argument("--logistic", action="store_true")
    args = parser.parse_args()

    run_all = args.all or not any([
        args.lorenz, args.rossler, args.clifford, args.logistic
    ])

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if RICH:
        console.print(Panel.fit(
            "[bold white]Deterministic Chaos Explorer[/bold white]\n"
            "[dim]Strange attractors  ·  sensitivity analysis  ·  route to chaos[/dim]",
            border_style="dim cyan",
        ))
    else:
        print("=== Deterministic Chaos Explorer ===")

    total_start = time.time()

    if run_all or args.lorenz:
        run_lorenz()
    if run_all or args.rossler:
        run_rossler()
    if run_all or args.clifford:
        run_clifford()
    if run_all or args.logistic:
        run_logistic()

    elapsed = time.time() - total_start
    if RICH:
        console.print(f"\n[bold green]All done.[/bold green]  "
                      f"Outputs saved to [cyan]{OUTPUT_DIR}[/cyan]  "
                      f"[dim]({elapsed:.1f}s total)[/dim]\n")
    else:
        print(f"\nAll done. Outputs saved to {OUTPUT_DIR}  ({elapsed:.1f}s total)\n")


if __name__ == "__main__":
    main()
