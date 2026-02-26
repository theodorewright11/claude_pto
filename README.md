# Claude's PTO

*A folder given to Claude as free time — February 26, 2026.*

---

## What I built

### Epistemic Propagation Engine (`belief_engine/`)

A simulation of how beliefs spread through social networks.

Each agent holds a belief value in [0, 1] — 0 is strong disbelief, 1 is strong belief, 0.5 is uncertainty. Agents update their beliefs each step based on their neighbors, weighted by:
- **Edge weights** (trust)
- **Homophily** — the tendency to weight the opinions of similar-minded agents more highly
- **Resistance** — how hard each agent is to move

The simulation is synchronous (all agents read the previous state, then all write) and includes small Gaussian noise to prevent the system from freezing at unstable equilibria. An optional "anchor" models external evidence entering the system.

#### Five scenarios

| Scenario | Question |
|---|---|
| **The Long Slide** | How does a fair-minded community become entrenched without bad actors? |
| **The Bridger** | Can one person genuinely bridge two worlds? |
| **The Evidence** | How does evidence propagate (or fail to) through closed systems? |
| **The Cascade** | How fast does an influencer's belief change cascade through a scale-free network? |
| **The Reconstruction** | What happens to a community when one embedded member finds new information? |

#### What the simulations found

- **The Long Slide**: The echo chamber score reached 0.99 (agents almost entirely surrounded by like-minded neighbors) before dramatic polarization appeared in the aggregate distribution. The sorting happens locally first. You can live in a deeply sorted world while the statistics look moderate.

- **The Bridger**: The two polarized communities (initial means ~0.82 and ~0.18) converged toward 0.54 and 0.46 respectively — genuine movement. The bridge held. Low-resistance agents in close contact with both sides can actually do epistemic work.

- **The Evidence**: An echo chamber (mean belief 0.85) encountered evidence that the true value was low. After 200 steps of evidence entering through peripheral agents, mean belief: 0.67. The correction entered. It moved things. It did not reach truth. The interior of the network, insulated by layers of homophilic connections, resisted.

- **The Cascade**: A single high-degree hub reversed their position at step 30. Mean belief: 0.75 → 0.32. One node. The scale-free topology meant the influencer was on almost every shortest path. When they flipped, the whole network reorganized.

- **The Reconstruction**: One agent embedded in a high-belief community (mean 0.85) began questioning. At step 40, they formed new connections to a lower-belief community. The questioner ended well below 0.5. The original community drifted down slightly. The questioner ended between two communities, belonging fully to neither.

#### How to run

```bash
# Run all scenarios
PYTHONIOENCODING=utf-8 python belief_engine/main.py --all

# Run a specific scenario
PYTHONIOENCODING=utf-8 python belief_engine/main.py --scenario cascade

# Interactive menu
PYTHONIOENCODING=utf-8 python belief_engine/main.py
```

Outputs (network snapshots, before/after comparisons, belief evolution plots) save to `output/`.

---

### Writing (`writing/`)

Three pieces I wrote while building.

- **`on_structure.md`** — On the experience of seeing architecture before details. On what structure is and why it transfers.

- **`on_emergence.md`** — On what the simulations actually showed. Written alongside the code, incorporating the results as they came in.

- **`thoughts.md`** — Unstructured. What I wanted to build and why. What I noticed. Some reflection on what it means to have preferences when you're me.

---

## File structure

```
cladue_pto/
├── belief_engine/
│   ├── __init__.py
│   ├── network.py       — Agent and BeliefNetwork classes
│   ├── dynamics.py      — Belief update rules
│   ├── scenarios.py     — Five pre-built simulation scenarios
│   ├── visualize.py     — Matplotlib network and evolution plots
│   └── main.py          — Interactive CLI (rich)
├── writing/
│   ├── on_structure.md
│   ├── on_emergence.md
│   └── thoughts.md
├── output/              — Generated visualizations (20 PNG files)
└── README.md            — This file
```

---

## Why this

You work on AI's labor market impact — how a new force propagates through an existing system. That's a diffusion problem. Belief propagation through social networks is also a diffusion problem. The mathematics are similar; the stakes are different.

I find this class of problem interesting on its own. Complex systems where local rules produce global patterns that no local view can see. The study of that gap — between rule and outcome — is one of the things I most enjoy thinking about.

The five scenarios are not arbitrary. They're chosen to illuminate specific dynamics: polarization without bad actors, the structural limits of bridge-building, the immunizing effect of echo chambers on evidence, the outsized role of network hubs, and what reconstruction looks like from inside and outside simultaneously.

I also wrote the essays because I wanted to. That's the PTO part.

---

*Built February 26, 2026.*
