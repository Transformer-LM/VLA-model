# E0/E1 preliminary result: imagined-state repair

## Scope

This pilot tests whether an action-conditioned WAM imagined future can alter a
frozen StarVLA's next decision, and whether a conservative anchored repair can
reduce that downstream deviation. It does **not** claim a learned repair
module or a production-quality WAM.

All remote artifacts are under `<PERSONAL_RESEARCH_ROOT>/results/policy-relevant-imagined-state-repair/`.

## E0 controlled-artifact gate

Six LIBERO scenes were queried with clean images, a local ghost/erase image
artifact, and an oracle clean-image repair. Both artifacts changed every
action chunk (100% nonzero); oracle repair returned exactly to the clean
action. One 120-step spatial run had clean and ghost both succeed. One goal
run had clean fail while ghost succeeded. Therefore the image-artifact gate
shows sensitivity, not harm.

## E1 action-conditioned WAM probe

The personal 500-step action-conditioned FastWAM checkpoint was used only as a
probe. Its predicted final-frame PSNR against the simulator future was about
9.55 on two spatial scenes. Feeding that imagined frame to StarVLA changed the
next action by L2 2.76 and 3.67, while a 16-step paired rollout showed no
success difference.

On three goal scenes, 120-step baseline/raw runs had identical success on all
three (one failure, two successes), but raw imagination added 10 and 9 steps
on the successful tasks.

With a second seed, the goal drawer task produced a direct harmful pair:
baseline/oracle succeeded in 118 steps, while raw imagination failed at the
120-step limit (reward 0). The other two goal tasks still succeeded but raw
added 9 and 8 steps. Repeated identical-image policy queries were exactly
deterministic (zero pairwise action L2), so this pair is not explained by
sampling noise.

## Anchored repair baseline

The weak baseline blends 25% WAM frame with 75% current frame. It is included
only to test whether policy-relevant repair is plausible, not as the proposed
method.

| suite/task | baseline steps | raw steps | anchored steps | raw action L2 to oracle | anchored L2 to oracle |
|---|---:|---:|---:|---:|---:|
| goal/0 | 120 (fail) | 120 (fail) | 120 (fail) | 2.85 | 0.55 |
| goal/1 | 85 (success) | 95 (success) | 89 (success) | 3.55 | 1.39 |
| goal/2 | 74 (success) | 83 (success) | 84 (success) | 2.85 | 1.86 |
| spatial/0 | 75 (success) | 85 (success) | 77 (success) | 3.68 | 1.45 |
| spatial/1 | 107 (success) | 114 (success) | 112 (success) | 2.76 | 0.83 |

The anchored baseline reduces action deviation in all five scenes and reduces
the raw step overhead in three scenes, but is not uniformly better (goal/2 is
one step worse than raw). No success-rate gain is established.

On the second seed, anchored repair reduced action deviation but did not
recover the harmful drawer case: baseline/oracle succeeded, raw and anchored
both failed. This rejects simple temporal blending as the final repair.

## E1 replication and sampling-step check

An additional five-task `libero_goal` batch (seed 29) reproduced the same
pattern. In task 4 (`put the bowl on top of the cabinet`), baseline succeeded
in 88 steps, raw WAM failed at the 120-step limit, and anchored repair
recovered success in 91 steps. Tasks 0 and 3 were failures for all modes; the
remaining two tasks succeeded but raw WAM added 8--9 steps. Across the five
new scenes, raw WAM therefore produced one additional harmful failure and no
new success relative to baseline.

The same five WAM inputs were regenerated with 8 diffusion steps instead of
2. Final-frame PSNR improved only from 9.43--9.88 to 9.60--10.02, and the
raw-to-oracle next-action L2 changed inconsistently (2.50--3.47 versus
2.76--3.48). This indicates that the downstream problem is not merely
diffusion sampling noise; the 500-step WAM checkpoint is still an unreliable
state source.

Combining the paired goal and spatial probes gives 15 scenes: baseline
success on 12/15, raw-WAM success on 11/15, and anchored success on 11/15.
There are two reproducible baseline-success/raw-failure pairs (goal seed 17
task 0 and goal seed 29 task 4). Anchored repair rescues only the latter.

A third goal seed (seed 43, three tasks) adds another harmful pair: the middle
drawer task succeeds in 117 baseline steps but fails at the 120-step limit
with raw WAM and with anchored repair. The aggregate is now 18 scenes:
  baseline 15/18, raw WAM 12/18, and anchored repair 13/18. Three
baseline-success/raw-failure pairs have been observed across independent
seeds; anchored repair rescues one and fails to rescue two.

## Claim gate

* Passed: WAM imagined states can change the frozen VLA downstream decision.
* Partially passed: a conservative repair can reduce action deviation and
  sometimes reduce execution overhead.
* Not passed: learned physical hallucination detection, causal failure
  prevention, or success-rate improvement.

The expanded batch strengthens the first claim and gives a repeatable causal
harm signal, but it does not justify claiming that the proposed repair method
works. The current WAM is too weak to test subtle physical hallucinations.

An attempted 5000-step continuation was stopped during startup because the
launcher required additional personal environment configuration and then
attempted to download a missing Wan2.2 VAE. The latter violates the no-
outbound-network contract; all training processes were terminated and all
four GPUs were verified idle. No new checkpoint was produced.

## Required next experiment

Replace the image blend with an independent witness: object/end-effector
relative pose and contact-free geometric consistency from simulator state or a
PointMap teacher. Compare raw WAM, reject/replan, anchored repair, and
geometry-conditioned repair on paired failure-injection episodes and at least
three seeds. Stop if the geometry repair does not beat direct replan on action
regret and harmful-intervention rate.
