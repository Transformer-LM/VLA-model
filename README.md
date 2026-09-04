# VLA/WAM research snapshot

This snapshot contains the current embodied-autoresearch skill, research notes,
all major historical experiment runs, and source code for the VLA/WAM research
program. Read `RESEARCH_HANDOFF_FOR_NEXT_GPT.md` first when continuing from a
different GPT account.

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
- `archive/all-experiments/`: complete text/source/JSON snapshot of the major
  experiment directories, including PointMap, Object-Belief, pi0.5 progress,
  functional geometry, novelty runs, ideaspark runs, and ISRAC.
- `archive/project-context/`: top-level briefs, configurations, manifests, and
  previous account-handoff materials.
- `RESEARCH_HANDOFF_FOR_NEXT_GPT.md`: experiment-by-experiment status,
  supported/unsupported claims, navigation guide, and safe reproduction rules.

The one-off remote launcher is intentionally not included because it contains
machine-specific process IDs, scheduler paths, and deployment details; it is
not a reusable experiment component.

## Reproducibility notes

The experiment code expects the personal research environment and model/data
assets to be supplied separately. `run_wam_e1_inference.py` and
`wam_downstream_e1.py` accept the `VLA_WAM_PERSONAL_ROOT` environment variable
instead of embedding a machine-specific home path. Dataset files, model
weights, checkpoints, generated videos/NPZ files, Python bytecode, and private
runtime traces are not included in this repository; textual logs and JSON
result summaries are kept in the archive for provenance.

## Privacy and safety

This public repository intentionally excludes SSH keys, credentials, server
addresses, personal absolute paths, model weights, datasets, and real-robot
control commands. The experiment is simulation/offline only; no real-robot
motion is launched by the included snapshot.
