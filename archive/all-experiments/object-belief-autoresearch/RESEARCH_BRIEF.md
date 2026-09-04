# Research Brief — Object-addressed action-updated belief for VLA

**Status:** authorized for autonomous idea discovery, method planning, implementation, and offline/simulation experiments  
**Paper writing:** disabled

## Starting observation

OA-WAM separates persistent object address from dynamic content and pose, improving language-to-object binding. EvoScene-VLA maintains an action-updated scene belief across action chunks so that state changes need not be reconstructed only from the latest image.

Neither component alone establishes reliable long-horizon execution. The research question is whether their conjunction exposes a defensible, testable gap beyond object binding and generic memory.

## Required scientific question

Find a non-duplicative mechanism in which object identity/address and action-updated object belief jointly improve long-horizon VLA execution under object ambiguity, occlusion, action-induced scene changes, false completion, or failed substeps. The method must support belief verification or correction; simply concatenating object slots and memory tokens is not sufficient.

## Candidate contribution shapes to test, not assume

- address-conditioned action-effect belief updates;
- identity uncertainty propagated through predicted object-state change;
- contradiction-triggered belief invalidation after observation returns;
- relation/progress events attached to persistent object addresses;
- selective re-observation or recovery when belief support is weak.

## Required comparisons

- frozen or matched VLA without external belief;
- global latent/history memory with the same capacity and context;
- object-address-only model;
- action-updated belief without stable object address;
- combined method;
- an observation-only tracker or direct success/progress scorer where applicable.

## Cheap falsification gates

1. Construct controlled object-swap, occlusion, and failed-action interventions.
2. Show an oracle object-addressed updated belief has measurable headroom over latest-frame/history baselines.
3. Show the learned belief improves object identity, state/progress correctness, and closed-loop decisions—not only slot prediction loss.
4. Stop if a matched ordinary memory transformer or direct verifier reaches the same result.

## Execution authority and restrictions

- Idea discussion does not require another checkpoint; the top candidate may advance automatically only after novelty and falsification gates pass.
- Experiments are authorized on the configured remote server using idle A100 GPUs.
- Use only SSH user `liu_meng` and only `<PERSONAL_RESEARCH_ROOT>` (canonical `<PERSONAL_RESEARCH_ROOT_ALIAS>`) for reading and writing.
- Do not use root, sudo, su, shared datasets/models/projects/checkpoints, `.bashrc` edits, global Conda, system CUDA changes, paid compute, private-data uploads, or live robot actions.
- Recheck GPU occupancy before every launch. Prefer physical GPUs 2 and 3; GPUs 0 and 1 may be used only if individually idle. Never preempt or share.
- The administrative pilot ceiling is 32 GPU-hours and total ceiling 400 GPU-hours; these are safety stops for unattended execution, not the old 2/8 GPU-hour scientific assumption.
- Preserve all negative results, raw logs, configurations, and actual GPU-hour accounting.
