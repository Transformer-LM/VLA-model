# E1 evidence audit (provisional)

## Scope

This audit covers the paired raw JSON outputs under
`<PERSONAL_RESEARCH_ROOT>/results/policy-relevant-imagined-state-repair/e1/`.
It does not validate the physical realism of the WAM itself.

## Deterministic checks

- Six anchored-evaluator JSON files were found.
- All 18 scene keys contain exactly four modes: `baseline`, `raw`,
  `anchored`, and `oracle`.
- Every recorded finite numeric field (`steps`, rewards, and action L2
  values) is finite; no NaN or infinity was found.
- All reported success counts are read from the raw `done` fields, not inferred
  from imagined rollouts.
- The WAM prediction files and paired input metadata exist for each reported
  batch; the 8-step sampling check is kept separate from the main 2-step table.

## Integrity limitations

1. Baseline and oracle use a saved simulator future image, while later normal
   policy queries use live simulator observations. The policy is deterministic,
   but one-step simulator/image alignment can differ by one control step.
2. The current action-conditioned WAM is a 500-step trainable-interface
   checkpoint with final-frame PSNR around 9.5--10.0. It is a deliberately weak
   probe, so the experiment establishes causal downstream sensitivity and harm,
   not a production-quality WAM benchmark.
3. Anchored repair is a diagnostic baseline (`25%` imagined frame + `75%`
   current frame), not the proposed geometry-conditioned repair.
4. The data are simulation-only and contain no real-robot safety evidence.

## Claim adjudication

- **Supported (narrow):** feeding an action-conditioned WAM imagined frame to a
  frozen VLA changes its next action and can turn a baseline-success episode
  into a failure on repeated seeds.
- **Partially supported:** conservative image anchoring lowers next-action L2
  on the paired scenes and rescues one of three harmful pairs, but is not
  uniformly successful.
- **Unsupported:** a learned physical hallucination detector or a general
  geometry-conditioned state-repair method improves task success.

The current evidence therefore routes to a structural method experiment only
after a stronger WAM checkpoint or an explicitly synthetic physical-corruption
benchmark is available. Continuing to tune pixel blending would not be an
informative experiment.
