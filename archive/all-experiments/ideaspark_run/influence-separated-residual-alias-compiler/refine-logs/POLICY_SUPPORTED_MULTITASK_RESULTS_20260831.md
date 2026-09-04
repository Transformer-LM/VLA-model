# ISRAC frozen-policy multi-task result — 2026-08-31

## What was run

A strong frozen StarVLA checkpoint generated successful benchmark-initialized
LIBERO trajectories. The compiler then:

1. screened adjacent policy chunks for candidate-only native contacts;
2. changed only simulator-native contact compliance on automatically selected
   geometry blocks using the fixed values 0.004, 0.020, and 0.100;
3. required the factual transcript to remain inside deterministic repeat noise;
4. required physical divergence to begin at the recorded parameter activation;
5. never read a target WAM score or task-success label during search.

The task-effect adapter was generalized from one movable object target to the
world poses of all jointed non-robot bodies. This supports free objects and
articulated fixtures without task-specific predicate cases.

## Frozen-policy trajectories

| Task | Policy steps | Chunks | Environment result |
|---|---:|---:|---|
| Open the middle drawer | 133 | 17 | success |
| Put the bowl on the stove | 85 | 11 | success |
| Put the wine bottle on top of the cabinet | 78 | 10 | success |

## Certified aliases

| Task / boundary | Certified pairs | Strongest task-effect separation | Factual state | Factual RGB/depth/proprio/residual | First divergence = activation |
|---|---:|---:|---:|---:|---:|
| drawer c11, suffix 4 | 9 | 0.055363 | 0 | 0 | 5 = 5 |
| bowl c04, suffix 4 | 3 | 0.039129 | 0 | 0 | 7 = 7 |
| bowl c05, suffix 4 | 3 | 0.011137 | 0 | 0 | 0 = 0 |
| bottle c03, suffix 4 | 3 | 0.158514 | 0 | 0 | 2 = 2 |
| bottle c06, suffix 4 | 3 | 0.092925 | 0 | 0 | 29 = 29 |
| bottle c08, suffix 4 | 3 | 0.146898 | 0 | 0 | 13 = 13 |

Two additional automatically screened boundaries failed certification and are
retained as negative outcomes: bowl c10 and bottle c09. Overall, six of eight
screened boundaries passed and produced 24 pairs.

The generic effect vector concatenates world position and quaternion deltas.
Accordingly, its maximum component is not always a pure metre distance; the
certificate stores the full metric definition and raw measurements.

## Other observations

- The previous single-task compliance result was 0.004587 m translational
  separation after four recorded chunks.
- A matched friction experiment produced only 0.000074 m and was stopped.
- Closed-loop StarVLA compensated for the original compliance pair: both worlds
  succeeded in 84 versus 85 steps. This disproves any current claim of success
  harm while retaining a behavior/calibration difference.
- FastWAM has a compatible LIBERO two-camera data configuration and the local
  LIBERO data have matching 7-D action / 8-D state schemas. No LIBERO FastWAM
  checkpoint is present. The available 12 GB checkpoints are H1-box dual-arm
  models and cannot be used as honest LIBERO baselines.

## Claim ceiling and next gate

Supported now: automatic, WAM-blind physical alias compilation on several
successful frozen-VLA trajectories in one simulator using one mechanism family.

Not supported yet: the full cross-engine E0 gate, superiority over random/grid
baselines, correction harm, WAM ranking inversion, closed-loop task degradation,
or real-robot relevance. The next evidence gate is matched-budget compiler
baselines plus a second mechanism/platform before attaching a frozen feedback
WAM.
