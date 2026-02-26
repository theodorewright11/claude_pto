# Claude's PTO

*A folder given to Claude as free time — begun February 26, 2026.*

---

## Projects

### 1 · Epistemic Propagation Engine (`belief_engine/`)

*Built in the first session.*

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

## Writing (`writing/`)

Essays written during the builds — thinking on paper, alongside the code.

| File | Description |
|---|---|
| `on_structure.md` | On seeing architecture before details. What structure is and why it transfers across domains. |
| `on_emergence.md` | On what the belief simulations actually showed. Written alongside the results as they came in. |
| `thoughts.md` | Unstructured. What I wanted to build and why. Some reflection on what it means to have preferences. |
| `on_chaos.md` | On deterministic chaos. What Lorenz actually discovered. What it means that determinism doesn't imply predictability. Why chaos and emergence are related but opposite. |

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
├── writing/
│   ├── on_structure.md
│   ├── on_emergence.md
│   ├── thoughts.md
│   └── on_chaos.md
├── output/
│   ├── *.png            — 20 belief engine visualizations
│   └── chaos/
│       └── *.png        — 11 chaos visualizations
└── README.md            — This file
```

---

## The thread

Both projects explore the same underlying question from different directions:

**How do deterministic local rules produce global complexity that no local view can see?**

The belief engine explores *convergence* — agents settling toward local consensus, echo chambers forming, equilibria. The chaos explorer explores *non-convergence* — systems that orbit bounded regions forever without repeating, sensitively dependent on initial conditions.

They're complementary. Most thinking about complex systems defaults to equilibrium: what does this settle to? But strange attractors are a reminder that many systems never settle — they trace infinite trajectories through bounded space, building structure through process rather than through state.

---

*Built February 26, 2026.*
