# Diagnose embodied experimental failures

Read for failed training, unexpected rollout behavior or no-signal pilots.
Classify execution correctness before judging the scientific hypothesis.

| Evidence | Classification | Next discriminating action |
|---|---|---|
| Wrong action units, camera order, normalization or timing | interface error | trace one batch and controlled rollout |
| OOM, missing dependency, incomplete job | execution failure | repair runtime; keep hypothesis unadjudicated |
| Matched baseline fails to reproduce | baseline uncertainty | diagnose baseline before attributing method effects |
| Wide interval includes meaningful benefit and harm | inconclusive | follow precision protocol; do not force a pivot |
| Shuffled actions have the same predictions | possible action insensitivity | counterfactual action test with independent targets |
| Imagined returns rise without environment returns | possible model exploitation | test on current policy trajectories and oracle dynamics |
| Long action chunks degrade contact behavior | possible timing mismatch | compare frequency and aligned actions |
| Adequately precise negative mechanism test | scientific refutation | narrow, revise or terminate hypothesis |

## Visual evidence

Use fixed task/initial-state sampling rules. Save successful and failed episodes,
videos, timestamps, state/action traces and matching baseline cases. A renderer
failure does not imply policy failure. Sparse frames can miss transient contact;
inspect event-centered frames or the full sequence when necessary.

Save `rollout_diagnosis.json` as an optional experiment artifact:

```json
{
  "episodes": [{
    "episode_id": "ep001", "task_id": "task01", "initial_state_id": "init03",
    "environment_success": false, "video_path": "runs/E1/videos/ep001.mp4",
    "observed_behavior": "gripper opens before object reaches target",
    "suspected_failure": "action timing mismatch; not yet established",
    "supporting_telemetry": ["runs/E1/traces/ep001.json"],
    "next_discriminating_test": "replay aligned gripper commands on the same initial state"
  }]
}
```

Visual interpretations are diagnostic hypotheses. Verify against telemetry and
environment outcomes. Do not substitute plausibility for success, or label
world-model predictions as observed environment frames.
