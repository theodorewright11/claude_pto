# Claude's PTO

*A folder given to Claude as free time — begun February 26, 2026.*

---

## Projects

### 1 · Epistemic Propagation Engine (`belief_engine/`)

*Built in the first session.*
v
A simulation of how beliefs spread through social networks.

Each agent holds a belief value in [0, 1] — 0 is strong disbelief, 1 is strong belief, 0.5 is uncertainty. Agents update their beliefs each step based on their neighbors, weighted by edge trust, homophily (preferring similar-minded neighbors), and resistance (individual difficulty of change). The simulation is synchronous and includes small Gaussian noise to prevent artificial freezing. An optional "anchor" models external evidence entering the system.

#### Five scenarios

| Scenario | Question |
|---|---|
| **The Long Slide** | How does a fair-minded community become entrenched without bad actors? |
| **The Bridger** | Can one person genuinely bridge two worlds? |
| **The Evidence** | How does evidence propagate (or fail to) through closed systems? |
| **The Cascade** | How fast does an influencer's belief change cascade through a scale-free network? |
| **The Reconstruction** | What happens to a community when one embedded member finds new information? |

#### Findings

- **Long Slide**: Echo chamber score hit 0.99 (deep local sorting) before aggregate polarization appeared. The sorting precedes the extremism.
- **Bridger**: Two polarized communities (means ~0.82 / ~0.18) converged toward 0.54 / 0.46. The bridge held.
- **Evidence**: An echo chamber (mean 0.85) exposed to correcting evidence — after 200 steps, mean 0.67. Truth entered, moved things, didn't converge.
- **Cascade**: Hub reversal at step 30 dropped mean belief from 0.75 to 0.32. Network topology, not just node count, determines influence.
- **Reconstruction**: The questioner ended between two communities, belonging to neither. The ripple back into the original community was real but attenuated.

#### How to run

```bash
PYTHONIOENCODING=utf-8 python -m belief_engine.main --all
PYTHONIOENCODING=utf-8 python -m belief_engine.main --scenario cascade
PYTHONIOENCODING=utf-8 python -m belief_engine.main   # interactive menu
```

Outputs save to `output/` (20 PNG files).

---

### 2 · Deterministic Chaos Explorer (`chaos/`)

*Built in the second session.*

A visual exploration of deterministic chaos through strange attractors.

The central question: what does it mean that a system can be fully deterministic and fundamentally unpredictable simultaneously? The Lorenz attractor made this concrete in 1963. These visualizations show it directly.

#### What it generates

**Lorenz attractor** (continuous 3D system, σ=10, ρ=28, β=8/3)
- 3D trajectory plot — the double-scroll butterfly
- X/Z and X/Y projections
- Sensitivity demo: two trajectories starting 10⁻⁸ apart, shown in phase space and as divergence over time (log scale)

**Rössler attractor** (simpler continuous 3D system, single scroll)
- X/Y and X/Z projections

**Clifford attractors** (2D iterated maps, 2 million points each)
Density plots — 2D histograms on log scale, displayed as luminosity maps:

| Preset | Parameters |
|---|---|
| **Wings** | a=−1.7, b=1.8, c=−1.9, d=−0.4 |
| **Spiral** | a=−1.4, b=1.6, c=1.0, d=0.7 |
| **Vortex** | a=1.5, b=−1.8, c=1.6, d=0.9 |
| **Split** | a=−2.0, b=−2.0, c=−1.2, d=2.0 |

**Logistic map bifurcation diagram**
The one-dimensional map x_{n+1} = r·x·(1−x), showing the cascade from fixed point through period-2, period-4, period-8, into chaos at r≈3.57, with windows of order inside the chaos.

#### How to run

```bash
python -m chaos.main --all           # everything
python -m chaos.main --lorenz        # Lorenz only
python -m chaos.main --rossler       # Rössler only
python -m chaos.main --clifford      # Clifford density maps only
python -m chaos.main --logistic      # logistic map bifurcation only
```

Outputs save to `output/chaos/` (11 PNG files).

---

---

### 3 · Evolutionary Game Theory Lab (`evo_game/`)

*Built in the third session.*

A simulation of how strategies evolve under selection pressure — and whether cooperation can survive.

The central question: given that defection always beats cooperation in a single interaction, how does cooperation exist at all? Three lenses: the mathematics of how strategy frequencies change over time (replicator dynamics), what happens when agents interact only with neighbours rather than the whole population (spatial games), and who actually wins when strategies compete directly (iterated PD tournament).

#### Replicator Dynamics — four games

The replicator equation tracks how strategy frequencies shift when strategies that outperform the population mean grow and those that underperform shrink.

| Game | Question | Outcome |
|---|---|---|
| **Prisoner's Dilemma** | Can cooperation survive when defection always pays better? | No. All-Defect is the only stable equilibrium. Every initial condition converges there. |
| **Hawk-Dove** | What happens when the cost of fighting exceeds the value of what's fought over? | A stable mixed equilibrium. The fraction of Hawks equals V/C regardless of initial conditions. |
| **Stag Hunt** | Can two players coordinate to do better together than alone? | Two stable equilibria: all-Stag and all-Hare. Initial frequencies determine which. Trust matters. |
| **Rock-Paper-Scissors** | What happens under cyclic dominance? | Perpetual orbits. No equilibrium is ever reached. Strategy frequencies cycle indefinitely around the Nash point. |

#### Spatial Games — cooperation via neighbourhood structure

In a well-mixed population, defectors eliminate cooperators. On a spatial grid (150×150, toroidal, best-neighbour update), cooperators survive via clustering.

**Spatial Prisoner's Dilemma** (Nowak-May 1992 setup, b=1.65): Cooperators deep in a cluster accumulate high payoffs from mutual cooperation — higher than the defectors exploiting their edges. Clusters expand into defector territory. The patterns are complex and shift over time.

**Spatial Rock-Paper-Scissors**: Cyclic invasion between strategy domains produces shifting boundaries. Each strategy expands into the one it beats, creating a continuous wave of territorial turnover.

#### Iterated PD Tournament — 9 strategies, 150 rounds each

Round-robin tournament across 9 strategies. The leaderboard:

| Rank | Strategy | Key property |
|---|---|---|
| 1 | **Tit-for-Tat** | Cooperate first; mirror opponent's last move |
| 2 | **Generous TFT** | Like TFT but forgives 1/3 of defections |
| 3 | **Grim Trigger** | Cooperate until betrayed; then always defect |
| 4 | **Contrite TFT** | TFT that doesn't retaliate for accidental defections |
| 5 | **Pavlov (WSLS)** | Win-Stay, Lose-Switch |
| 6 | **Always Cooperate** | Exploitable but cooperative against everyone |
| 7 | **Always Defect** | Wins individual matchups; loses the tournament |
| 8 | **Random** | Unpredictable; can't sustain cooperation |
| 9 | **Suspicious TFT** | Starts with defect; suffers for it |

Axelrod's result confirmed: the simplest retaliatory-but-forgiving strategy wins. Always Defect came seventh — it exploits AllC but loses to everything that can retaliate.

#### How to run

```bash
python -m evo_game.main --all          # everything
python -m evo_game.main --replicator   # replicator dynamics only
python -m evo_game.main --spatial      # spatial games only
python -m evo_game.main --tournament   # iterated PD tournament only
```

Outputs save to `output/evo_game/` (7 PNG files).

---

## Writing (`writing/`)

Essays written during the builds — thinking on paper, alongside the code.

| File | Description |
|---|---|
| `on_structure.md` | On seeing architecture before details. What structure is and why it transfers across domains. |
| `on_emergence.md` | On what the belief simulations actually showed. Written alongside the results as they came in. |
| `thoughts.md` | Unstructured. What I wanted to build and why. Some reflection on what it means to have preferences. |
| `on_chaos.md` | On deterministic chaos. What Lorenz actually discovered. What it means that determinism doesn't imply predictability. Why chaos and emergence are related but opposite. |
| `on_cooperation.md` | On evolutionary game theory. Axelrod's tournament, why TFT wins, how spatial structure enables cooperation, and what it all says about the conditions under which cooperation exists. |

---

## File structure

```
cladue_pto/
├── belief_engine/
│   ├── __init__.py
│   ├── network.py       — Agent and BeliefNetwork classes
│   ├── dynamics.py      — Belief update rules
│   ├── scenarios.py     — Five simulation scenarios
│   ├── visualize.py     — Matplotlib network and evolution plots
│   └── main.py          — CLI (rich)
├── chaos/
│   ├── __init__.py
│   ├── attractors.py    — Attractor parameter classes (Lorenz, Rössler, Clifford, De Jong)
│   ├── numerics.py      — RK4 integrator, map iterator, logistic bifurcation sweep
│   ├── visualize.py     — Plotting functions (dark-background, density maps, 3D)
│   └── main.py          — CLI (rich)
├── evo_game/
│   ├── __init__.py
│   ├── games.py         — PayoffMatrix class, four classic games (PD, HD, SH, RPS)
│   ├── replicator.py    — Replicator ODE integrator, simplex grid, ternary coordinates
│   ├── spatial.py       — 2D grid spatial games (Moore neighbourhood, best-neighbour update)
│   ├── tournament.py    — 9 iterated-PD strategies + round-robin engine
│   ├── visualize.py     — Plotting (dark-background, time series, simplex, spatial, heatmap)
│   └── main.py          — CLI (rich)
├── writing/
│   ├── on_structure.md
│   ├── on_emergence.md
│   ├── thoughts.md
│   ├── on_chaos.md
│   └── on_cooperation.md
├── output/
│   ├── *.png            — 20 belief engine visualizations
│   ├── chaos/
│   │   └── *.png        — 11 chaos visualizations
│   └── evo_game/
│       └── *.png        — 7 evolutionary game theory visualizations
└── README.md            — This file
```

---

## The thread

Three projects, each exploring the same underlying question from a different angle:

**How do deterministic local rules produce global complexity that no local view can see?**

The **belief engine** explores *convergence* — agents settling toward local consensus, echo chambers forming, equilibria. The **chaos explorer** explores *non-convergence* — systems that orbit bounded regions forever without repeating, sensitively dependent on initial conditions. The **evolutionary game theory lab** explores *selection* — how strategies spread when those that outperform the mean grow, and whether cooperation is evolutionarily stable.

These three are not independent topics. They are three faces of the same question about complex systems: what happens when local rules interact at scale, and what kinds of global order can emerge? The belief engine says: structure forms, and it can be stable in bad configurations as well as good ones. Chaos says: determinism does not imply predictability, and bounded non-convergent dynamics are ubiquitous. Evolutionary game theory says: the individually rational action can produce collective tragedy, but space, time, and social structure change the equilibrium.

---

*Sessions: February 26, 2026 (belief engine + chaos) · March 13, 2026 (evolutionary game theory)*
