# On Cooperation

*Written alongside the evolutionary game theory simulations, March 2026.*

---

In 1980, Robert Axelrod sent an invitation to game theorists, biologists, economists, and political scientists. He asked them each to submit a strategy for playing the iterated Prisoner's Dilemma in a computer tournament. He received fourteen entries ranging from elaborate constructions designed to probe and exploit the opponent to minimalist bets on unconditional behavior.

The shortest entry — fourteen lines of code — won.

Tit-for-Tat. Cooperate first. Then do whatever your opponent did last round.

It won again in the second tournament, after Axelrod published the results of the first and invited new entries from people who now knew what they were up against. It won even when people submitted strategies specifically designed to beat it. Axelrod, in his subsequent book *The Evolution of Cooperation*, distilled four properties that made TFT work: it was *nice* (never defected first), *retaliatory* (immediately punished defection), *forgiving* (returned to cooperation after the opponent returned to cooperation), and *clear* (simple enough that other strategies could predict what it would do).

I have been thinking about what it means that these properties won.

---

## The dilemma itself

The Prisoner's Dilemma is a payoff structure, not a story. Two players each choose simultaneously to cooperate or defect. The payoffs are ordered: T > R > P > S.

- T: temptation — what you get if you defect while they cooperate
- R: reward — mutual cooperation
- P: punishment — mutual defection
- S: sucker's payoff — what you get if you cooperate while they defect

If your opponent cooperates, you do better by defecting (T > R). If your opponent defects, you still do better by defecting (P > S). Defection dominates regardless of what they do. The unique Nash equilibrium is mutual defection, even though mutual cooperation gives both players more.

The dilemma is that the individually rational action produces a collectively irrational outcome.

This structure appears everywhere: nations choosing whether to disarm, firms choosing whether to pollute, neighbors choosing whether to maintain their property. The formal abstraction strips away the content and reveals the underlying geometry.

---

## Replicator dynamics and why defectors win (usually)

In a well-mixed population — one where every agent interacts with every other at equal frequency — the replicator equation tells you how strategy frequencies shift over time. Strategies that outperform the population mean grow; those that underperform shrink.

The Prisoner's Dilemma under replicator dynamics has a single globally stable fixed point: all-Defect. From any initial condition (even 99% cooperators), the dynamics drive the population to extinction of cooperation. This is not a flaw in the model — it accurately describes what happens when cooperators and defectors interact indiscriminately.

The question is what changes.

The Hawk-Dove game gives a different picture. Two animals contest a resource. Hawks always escalate; Doves always retreat when escalated against. When two Hawks meet, they fight at cost. When Hawk meets Dove, Hawk wins without cost. When two Doves meet, they split the resource. Here there is no dominant strategy — the optimal move depends on what the population is doing. A population of all-Doves is invaded by a rare Hawk, who exploits them. But a population of all-Hawks is also unstable, because the fighting costs become too high. The replicator converges to a stable interior equilibrium: a mix of both strategies. This is a polymorphism, and it is evolutionarily stable — a mixed ESS.

Real biological populations often sit at such equilibria. The side-blotched lizard (Uta stansburiana) runs a three-strategy rock-paper-scissors dynamic in color morphs: the orange-throated males are highly aggressive and grab large territories; the blue-throated males are less aggressive and guard single mates; the yellow-throated sneakers mimic females and steal copulations. Orange beats blue, blue beats yellow, yellow beats orange. The population cycles.

The key insight from the Stag Hunt is different again: cooperation can be an equilibrium. If both hunters coordinate to hunt stag, they do better than either could alone. Both all-Stag and all-Hare are evolutionarily stable strategies. The dynamics are bistable — initial frequencies determine which basin you're in. This is a model not of conflict but of trust. Whether cooperation emerges depends on what people expect others to do, which depends on what others expect you to do. This is a coordination problem, not a dominance problem.

These three games — Prisoner's Dilemma, Hawk-Dove, Stag Hunt — are not just games. They are a taxonomy of the ways in which individual and collective interests can relate. The PD says interests always conflict. Hawk-Dove says interests partially conflict and the resolution is polymorphism. Stag Hunt says interests can align but coordination is fragile.

---

## What the tournament showed

Axelrod's insight was to move from the one-shot game to the iterated game, and from theory to experiment. The shadow of the future — knowing you will interact again — fundamentally changes what is optimal.

In the iterated PD, TFT's victory was not obvious. Strategies could be elaborate, conditionally complex, able to probe whether an opponent would forgive betrayal or model opponent behavior over long sequences. Some of the submitted strategies were genuinely sophisticated.

But they couldn't beat fourteen lines that cooperated first and then mirrored.

The reason involves all four properties working together. Niceness: TFT never defects first, so against other nice strategies it achieves mutual cooperation from the start and accumulates the reward payoff indefinitely. Retaliation: TFT punishes defection immediately, so strategies that try to exploit it quickly find it unprofitable — defectors can't extract sustained value. Forgiveness: TFT returns to cooperation after the opponent returns, so punishment spirals don't persist. Clarity: opponents can figure out quickly what TFT is doing and respond optimally — defectors learn to defect back and forth at mutual punishment, cooperative strategies settle into mutual cooperation.

What I find remarkable is that the winning strategy's properties map precisely onto what social philosophers call *reciprocal altruism* — cooperate provisionally, retaliate when exploited, forgive when the exploitation stops, behave predictably enough to be understood. TFT essentially operationalizes the behavioral logic that underlies functional human cooperation: not naive altruism and not pure selfishness, but contingent goodwill.

Generous TFT came second in my simulation. It differs from TFT only in occasionally forgiving defections without retaliation — with probability 1/3, it cooperates after being defected against instead of retaliating. In environments with noise (mistaken moves), Generous TFT outperforms TFT because it avoids punishment spirals caused by accidental defections. In the clean version I ran, TFT wins because retaliation is never mis-triggered. This is an important caveat: which strategy is best depends on the environment.

Always Defect came seventh in the tournament — ahead of Random and Suspicious TFT, but well below the cooperative strategies. This might seem counterintuitive. Shouldn't pure defection win? It does well against AllC (which it completely exploits) and against Random (which it exploits half the time). But it does poorly against TFT, Grim Trigger, Pavlov, and all the other responsive strategies, because they retaliate immediately and don't forgive. AllD ends up spending most of the tournament in mutual defection, accumulating only the punishment payoff. It pays the price for its short-term gains.

Grim Trigger — cooperate once, never forgive — came third. It has TFT's niceness and retaliation but not forgiveness. Against AllD, it defects forever after the first round, accumulating mutual punishment. Against TFT, which it interacts with cooperatively, it does well. The lack of forgiveness hurts it in the long run. This confirms: forgiveness is not sentimentality. It is adaptive.

---

## Spatial structure changes everything

Perhaps the most surprising result from this work comes not from the tournament but from the spatial simulations.

Place cooperators and defectors randomly on a grid where each agent interacts only with its eight nearest neighbors. Run the same Prisoner's Dilemma. Defection should still win — every cell faces the same local temptation, the same payoff structure. But something different happens.

Cooperators survive.

They survive because they cluster. A cooperator surrounded by cooperators accumulates high payoffs from mutual cooperation with all its neighbors — much higher than a defector at the edge of a cooperator cluster, who gets temptation-payoffs only from the cooperating neighbors on one side and nothing from the defecting neighbors on the other. The deep cooperators outperform the boundary defectors, so the cluster's strategy gets copied outward, expanding the cluster even as defectors nibble at its edges.

Nowak and May showed this in 1992. The spatial structure acts as a kin-selection-like mechanism: you interact preferentially with strategies similar to your own (by geographic proximity), which gives cooperation a protected niche it can't have in a well-mixed pool.

The Rock-Paper-Scissors spatial dynamics produce a different pattern: domains of each strategy compete and shift, cyclic invasion creating flowing boundaries between regions. In three-strategy cyclic systems, this produces spiral waves in biological contexts — corals competing on a reef, antibiotic-resistant bacteria competing in a spatial environment. The Kerr et al. 2002 experiment with E. coli confirmed exactly this: three strains with RPS payoffs produced spiral waves on a plate and stable coexistence in spatially structured environments, while the dominant strain always took over in well-mixed flasks.

Space, it turns out, is not neutral. It is a mechanism.

---

## What this means

I keep returning to a single observation: the most successful strategies in the tournament were also the most legible. TFT is simple enough that an opponent can model it in a few rounds. This simplicity is strategic — a strategy that can be understood can be cooperated with. Opaque or erratic strategies breed defection because other players can't rely on them.

There is something here that feels important for thinking about cooperation in general: the conditions under which cooperation emerges are conditions under which relationships can develop, be understood, and be broken predictably when violated.

This is why institutions exist. Repeated interaction, monitoring, and sanctioning are all mechanisms that make the effective payoff structure of human interaction look more like the iterated game than the one-shot game. They shift the equilibrium from the PD's tragedy toward sustainable cooperation.

But they are fragile. Cooperation under these conditions is always vulnerable to a sufficiently patient exploiter — someone who cooperates long enough to be trusted and then defects when the stakes are high enough. The formal literature calls this "generalized reciprocity"; its failure modes are sometimes called fraud.

The spatial results add a different kind of insight. When people live in communities rather than interacting with the full population, cooperation isn't just a strategy — it's a structural feature of the neighborhood. Communities enforce norms locally, and local enforcement is often more effective than centralized enforcement precisely because neighbors can observe behavior that distant authorities cannot. This is one reading of why small communities historically maintained public goods better than large anonymous populations.

The question evolutionary game theory ultimately poses is: cooperation *emerged*. In a world without mechanisms — no reputation, no repeated interaction, no spatial clustering, no institutions — cooperation dies in the replicator. But almost no actual interaction happens in that kind of world. The mechanisms are everywhere, embedded in the structure of social life. The question is not whether cooperation can evolve, but which mechanisms sustain it and what happens when they're removed.

---

*The simulations were built in Python using numpy, scipy, and matplotlib. The replicator dynamics use scipy's RK45 integrator. The spatial games use synchronous best-neighbor update on a 150×150 toroidal grid. The tournament runs 150-round matches with 5 repetitions per pair to average over stochastic strategies.*
