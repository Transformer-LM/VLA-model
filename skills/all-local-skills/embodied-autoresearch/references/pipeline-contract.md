# Pipeline Contract

## Contents

1. Phase graph
2. Gate semantics
3. Phase contracts
4. Artifact and lineage rules
5. Resume and pivot rules

## Phase graph

Run exactly one active phase at a time:

```text
contract
  -> evidence-map
  -> [macro-direction checkpoint when exploration_level=field]
  -> idea-discovery
  -> method-plan
  -> implementation-experiments
  -> evidence-audit
  -> review-improvement
  -> research-synthesis
```

The state helper stores the active run under
`.aris/autoresearch/runs/<run-id>/state.json` and a pointer under
`.aris/autoresearch/active_run.json`.

The macro-direction checkpoint is a deliberate human decision gate, not a ninth
research phase. In field mode, `evidence-map` completes with a direction
landscape, then `idea-discovery` is marked blocked until
`research.selected_macro_direction` is populated and the phase is resumed.

## Gate semantics

`status` describes execution; `gate` describes evidence quality; `acceptance`
describes who or what established the gate.

| Field | Values | Meaning |
|---|---|---|
| status | pending, running, completed, blocked, failed, skipped | Execution state |
| gate | pending, pass, warn, fail, blocked | Phase evidence state |
| acceptance | none, deterministic, provisional, independent, human | Assurance source |

Rules:

- A phase advances only when `status=completed` and `gate` is `pass` or an
  explicitly permitted `warn`.
- Same-family reviewer output uses `acceptance=provisional`.
- File existence, job exit status, schema checks, and evidence-path verification
  may use `deterministic`.
- A different model family may use `independent` only when it reads raw artifacts
  rather than an executor summary.
- Human acceptance records the decision, not proof that a scientific claim is
  true.
- `skipped` is legal only for a genuinely non-applicable optional phase. None of
  the eight default phases is optional for a research-complete run.

## Phase contracts

### contract

- Inputs: `RESEARCH_BRIEF.md`, `AUTORESEARCH_CONFIG.json`.
- Actions in field mode: define the searchable parent field, discovery axes,
  inclusion criteria, and non-assumptions.
- Required artifact in field mode:
  `research-stage/FIELD_DISCOVERY_CONTRACT.md`.
- Actions after a macro direction is selected: classify WAM route; identify open
  choices; state a falsifiable question.
- Required artifact after direction selection:
  `research-stage/WAM_ROUTE_CARD.md`.
- Gate: the parent field or selected direction is searchable and the applicable
  route axes are explicit.
- Permitted open items: exact codebase, compute host, and dataset may wait until
  method preflight.

### evidence-map

- Inputs: brief plus field-discovery contract or route card.
- Actions: current search, deep reading, source verification, research-wiki
  ingest.
- Required artifacts in field mode: `research-stage/LITERATURE_MAP.md` and
  `research-stage/DIRECTION_LANDSCAPE.md`.
- `DIRECTION_LANDSCAPE.md` must contain a field taxonomy, search coverage and
  blind spots, five to eight macro directions, comparable scorecards, nearest
  clusters, decisive validation evidence, resource/risk estimates, and a
  recommendation that remains explicitly unselected.
- Gate: load-bearing claims have identifiers and source links; nearest work and
  contradictory evidence are represented; search date and queries are recorded;
  in field mode, the direction set is broad enough to expose real alternatives.

### idea-discovery

- Inputs: evidence map, a user-selected macro direction, and its route card.
- Actions: robotics ideation, WAM classification, novelty check, cheap pilot
  design, structural pivots as needed.
- Required artifacts: `idea-stage/IDEA_REPORT.md`,
  `idea-stage/WAM_ROUTE_CARDS.md`, and a persisted novelty report or trace.
- Gate: selected idea has no known direct collision, has a mechanism and
  refutation test, is benchmarkable, and has a matched baseline.
- Blocking condition in field mode: no persisted
  `research.selected_macro_direction`. A ranking or recommendation is not user
  selection.

### method-plan

- Inputs: selected idea and nearest prior work.
- Actions: refine method and generate claim-driven experiment plan.
- Required artifacts: `refine-logs/FINAL_PROPOSAL.md`,
  `refine-logs/EXPERIMENT_PLAN.md`, `refine-logs/PREFLIGHT_REPORT.md`.
- Gate: primary claim maps to an endpoint; confounds are controlled; run order,
  seeds, budgets, failure thresholds, and resource requirements are explicit.

### implementation-experiments

- Inputs: accepted plan and configured resources.
- Actions: implement, code-review, sanity-test, run, monitor, and collect raw
  results.
- Required artifacts: `refine-logs/EXPERIMENT_TRACKER.md`,
  `refine-logs/EXPERIMENT_RESULTS.md`, code/config/log/checkpoint paths, and a
  usage ledger in state.
- Gate: jobs actually completed; raw outputs exist; failed and excluded runs are
  enumerated; usage is within authority and budget.
- Blocking conditions: compute backend unconfigured, missing license or data,
  requested real-robot use, external spend not authorized, or sanity failure
  after bounded repair.

### evidence-audit

- Inputs: code, configs, logs, raw metrics, and intended claims.
- Actions: statistical analysis, integrity audit, result-to-claim adjudication.
- Required artifacts: analysis report, experiment audit, and claim verdict.
- Gate: no phantom evidence or integrity failure; every reported number resolves
  to raw evidence; the working claim is `yes` or honestly narrowed `partial`.
- A `no` verdict is a valid research result but does not pass the positive claim
  gate. Route to a structural pivot or synthesize it explicitly as a negative
  result when the research question is itself answered by the null result.

### review-improvement

- Inputs: all prior artifacts.
- Actions: adversarial review, bounded fixes, necessary reruns, refreshed audits.
- Required artifacts: `review-stage/AUTO_REVIEW.md`,
  `review-stage/REVIEW_STATE.json`, and fresh audit/claim artifacts for changed
  evidence.
- Gate: critical objections are resolved, scoped out with justification, or
  recorded as limitations. Same-family success remains provisional.

### research-synthesis

- Inputs: accepted or provisional research evidence.
- Actions: targeted ablations and final dossier.
- Required artifacts: `research-stage/RESEARCH_DOSSIER.md` and
  `AUTORESEARCH_STATUS.md`.
- Gate: every supported claim links to evidence; unsupported claims and negative
  results remain visible; the dossier is sufficient for reproduction or a clear
  next experiment.

## Artifact and lineage rules

For every experiment record:

- run id and parent idea/claim id;
- code commit or, outside Git, a source snapshot/hash and changed-file list;
- exact command, configuration, random seed, dataset version, environment
  version, and benchmark split;
- checkpoint and raw stdout/stderr paths;
- raw metric path and the analysis script/version that consumed it;
- start/end timestamps, exit status, GPU-hours, paid cost, and robot trials;
- exclusions or post-hoc decisions with reasons.

Summaries are indexes, not evidence. Never delete or overwrite raw artifacts to
make a later summary cleaner.

## Resume and pivot rules

- On resume, read state plus all artifacts recorded for the active phase.
- A `running` phase from a dead session becomes `failed` with the observed
  reason, then may be resumed.
- Do not resume `blocked` until its recorded external condition changed.
- A retry must cite new evidence or a concrete change. Three equivalent attempts
  are the maximum.
- Two consecutive no-signal iterations require a structural pivot: change the
  objective, data, representation, benchmark, world-model role, or policy/world-
  model coupling. Hyperparameter-only changes do not count.
- Re-run novelty after an idea pivot and re-run integrity/claim gates after code
  or evidence changes.
