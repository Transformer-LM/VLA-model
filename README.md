# VLA/WAM research snapshot

This snapshot contains the current embodied-autoresearch skill, research notes,
and source code for the policy-relevant imagined-state repair experiment.

## Included

- `skills/embodied-autoresearch/`: the reusable autonomous research workflow,
  including its references, templates, scripts, and agent metadata.
- `research/current-policy-repair/`: the current E1 experiment status, audit,
  results summary, and execution milestone.
- `research/active-israc/`: selected planning, novelty, literature, and result
  documents for the active influence-separated-residual-alias-compiler line.
- `experiments/policy-relevant-imagined-state-repair/`: portable Python source
  for preparing inputs, running FastWAM inference, evaluating StarVLA
  downstream effects, and aggregating results.

The one-off remote launcher is intentionally not included because it contains
machine-specific process IDs, scheduler paths, and deployment details; it is
not a reusable experiment component.

## Reproducibility notes

The experiment code expects the personal research environment and model/data
assets to be supplied separately. `run_wam_e1_inference.py` and
`wam_downstream_e1.py` accept the `VLA_WAM_PERSONAL_ROOT` environment variable
instead of embedding a machine-specific home path. Dataset files, model
weights, checkpoints, generated videos/NPZ files, and runtime logs are not
included in this repository.

## Privacy and safety

This public repository intentionally excludes SSH keys, credentials, server
addresses, personal absolute paths, model weights, datasets, and real-robot
control commands. The experiment is simulation/offline only; no real-robot
motion is launched by the included snapshot.
