# Executable research contracts

Read this before experiments, adjudication, or resuming an existing run. Scripts use
only the Python standard library. Commands below use the resolved Python launcher and
this skill's `scripts/research_state.py` (abbreviated `state`).

## Phase revisions and migration

`status`, `next`, and mutations check recorded SHA256 hashes. A changed/missing artifact
invalidates its producing phase and the downstream phase suffix, archiving old phase
records under `revisions`. This is deliberately conservative, not a general dependency
graph. Existing schema-1 states remain readable; completed phases without hashes are
unverified and reopen on first inspection. Original artifacts and usage remain intact.
Inspect/revalidate the artifacts; do not automatically repeat old GPU jobs.

Use `state reopen <phase> --reason <reason>` before intentional revisions. Settle all
active jobs first. Experiment IDs and their raw artifacts are immutable: use new IDs
for new code, evidence, seeds, or retries. Restore accidentally modified historical
files; do not silently re-sign them. Editing an evaluator intentionally requires a new
protocol, a new research run, and re-evaluation of relevant baselines.

Each phase must produce the paths in `pipeline-contract.md`; arbitrary nonempty files
cannot complete it. `complete --gate pass --acceptance provisional` validates ordinary
phases. `adjudicate <evidence-audit|review-improvement> --acceptance provisional` validates
verdict-bearing phases. Neither command establishes scientific truth. Independent
acceptance additionally requires recorded, different executor/reviewer model families;
this provenance is an assertion to verify externally, not cryptographic model identity.

## Frozen experiment protocol

Write `refine-logs/EXPERIMENT_PROTOCOL.json` before completing `method-plan`:

```json
{
  "protocol_id": "libero-h1-v1",
  "primary_metric": "task_macro_success_rate",
  "budget_basis": "environment_steps",
  "checkpoint_selection": "best on development tasks; final evaluation frozen",
  "aggregation_unit": "task and independent training run; paired initial states",
  "uncertainty_method": "specified analysis respecting task/run clustering",
  "stopping_rule": "fixed planned sample; inconclusive if precision is insufficient",
  "editable_paths": ["policy/", "configs/method/"],
  "protected_files": {"evaluation/evaluate.py": "<actual SHA256>"}
}
```

Include evaluator, success definition, split, fixed initial-state list and relevant
environment configuration in `protected_files`. Record code changes and verify they
stay within `editable_paths` using the workspace diff before launch. Hash checking is
implemented; editable-scope enforcement and process timeouts remain runner duties.
Never treat a five-minute proxy as sufficient evidence for long-horizon robot learning.

## Resource reservations and experiment tree

Before dispatch:

```text
state begin implementation-experiments
state reserve-job h1-seed0 --gpu-hours 0.5
```

Reservation = GPU count × enforced maximum walltime, not an optimistic estimate.
The runner must set scheduler timeouts and preserve the scheduler/PID receipt. The
ledger checks consumed + all reservations + requested reservation, and parallel-job
limits atomically. It is not a scheduler and cannot stop a process itself. On resume,
inspect existing scheduler jobs before starting another; never resubmit a reserved ID.

After any completion, failure, cancellation, or timeout, collect actual usage:

```text
state reconcile-job h1-seed0 --gpu-hours 0.42 --outcome completed
state record-experiment --manifest runs/h1-seed0/manifest.json
```

Repeated identical settlements do not double-charge; conflicting ones fail. Actual
overruns are recorded and block further progression. Never use zero for unknown usage.
Keep an interrupted job reserved until reconciled. `record-usage` is retired.

Manifest example (paths must exist and metrics must be a JSON object):

```json
{
  "experiment_id": "E001", "parent_id": null, "hypothesis_id": "H1",
  "job_id": "h1-seed0", "protocol_id": "libero-h1-v1",
  "operation": "baseline", "condition_id": "baseline", "training_seed": 0,
  "execution_status": "completed", "scientific_outcome": "inconclusive",
  "changed_factor": "none", "prediction": "baseline should reproduce reference",
  "observation": "pilot only", "next_action": "replicate",
  "artifacts": {
    "config": "runs/h1-seed0/config.json", "log": "runs/h1-seed0/stdout.txt",
    "source_snapshot": "runs/h1-seed0/source-manifest.json",
    "metrics": "runs/h1-seed0/metrics.json"
  }
}
```

Operations: `baseline`, `debug`, `improve`, `mechanism_test`, `ablation`, `replicate`.
Failed/cancelled execution must use `not_evaluated`, never a scientific rejection.
Every settled job must have a registered manifest before execution can complete,
including failed and cancelled jobs. Budget status is recomputed from actual usage
plus reservations against current configuration; changing limits never resets usage.
Increase limits only under the user's existing compute authorization.
Keep branches serial under small budgets. Parentage records conceptual dependence,
not permission to share mutable checkpoints or result paths.

Run `diagnose_run.py --root <project> --manifest <file> [--manifest <file> ...]`
for deterministic execution deficiencies. Interpret its findings against the plan;
it never establishes a scientific verdict. For formal studies set `--minimum-seeds`
from the protocol, rather than accepting the diagnostic default as a power analysis.

## Audit, claims and review

Write `refine-logs/ANALYSIS_REPORT.md`, `EXPERIMENT_AUDIT.json`, and
`CLAIM_VERDICT.json`. Both JSON reports contain `run_id`, the current evidence-audit
`revision` from state, and `input_hashes` mapping actual project files to SHA256.
The integrity report requires `integrity: "pass"` and binds every registered experiment
manifest and artifact, including failed runs. The verdict binds the current integrity
report and each metric source. Example claim entry:

```json
{
  "id": "C1", "statement": "Pilot estimate; generalization remains untested",
  "status": "inconclusive",
  "scope": "pilot", "experiment_ids": ["E001"],
  "metrics": [{"source": "runs/h1-seed0/metrics.json",
               "key_path": ["task_macro_success_rate"], "value": 0.42}]
}
```

Claim statuses: `supported`, `partial`, `refuted`, `inconclusive`. Negative and
inconclusive dossiers may complete the workflow honestly. A value must match its
specific JSON path exactly; formatted tables should derive rounding from that value.
Each claim identifies registered experiments and pilot/main scope. Main claims
require the configured minimum independent training seeds per represented condition;
meeting that count is not a substitute for statistical power or fair comparisons.
Aggregate metrics require saved raw episode data and a versioned analysis script in
the audit inputs. Direct metrics must belong to a cited completed experiment.
For a separate aggregate file, declare a top-level `derived_metrics` entry in the
claim verdict, keyed by its metric source path, with `experiment_ids` and
`analysis_script`. Contributors must be completed experiments cited by that claim;
the script and aggregate file must be bound by the audit's hashes. For example:
`"derived_metrics": {"analysis/summary.json": {"experiment_ids": ["E001"], "analysis_script": "analysis/summarize.py"}}`.
The checker verifies declared linkage, not whether the script was executed or its
statistics are correct; the reviewer must inspect and reproduce the aggregation.
The current main-claim gate is designed for training-seed replication. Frozen-policy
evaluation with only episode replication needs a separately reviewed acceptance
design; do not invent training seeds to satisfy this gate.

`review-stage/REVIEW_STATE.json` contains `run_id`, current review phase `revision`,
`reviewer`, `model`, `input_hashes`, and `unresolved_critical: []`. Its inputs bind both
current audit and claim reports. Keep substantive scoped-out findings in the report,
not just a score. Separate raw-evidence integrity review from a fresh-context scientific
review packet with previous scores and self-praise removed. Do not interpret blind
review scores as experimental validation. New experiments reopen execution and all
affected audits; perform required ablations before the final audit.

## Lessons and skill update proposals

After an informative experiment, save a scoped lesson under `research-wiki/lessons/`:
`lesson_id`, `observation`, `procedure`, `framework_commit`, `model`, `benchmark`,
`supporting_experiment_ids`, `contradicting_experiment_ids`, `status` (tentative,
replicated, superseded), and `supersedes`. One failed run is not a universal rule.

Before generating an idea or debugging, retrieve applicable lessons and their raw
evidence. Preserve contradictions. Repeated procedural observations may justify a
skill patch in `research-wiki/skill-proposals/` with source IDs, intended scope,
regression cases and a diff. Validate that proposal before applying it according to
the user's existing editing authorization. Do not automatically rewrite an active
experiment's evaluator, protocol, or acceptance gate.

## Design sources

These are adapted mechanisms, not imported frameworks or copied source code:
- [Karpathy autoresearch](https://github.com/karpathy/autoresearch): fixed evaluator and bounded experiments.
- [AI Scientist v2](https://github.com/SakanaAI/AI-Scientist-v2/tree/96bd51617cfdbb494a9fc283af00fe090edfae48/ai_scientist/treesearch): experiment nodes and repair/improvement separation.
- [EvoMap AutoResearch](https://github.com/bryanshake/autoresearch/blob/0fa9a9336fc84a6b069111adb03ca21fabb5394b/ar-runtime/scripts/ar-workflow-engine.py): adjudication-specific transitions and report provenance.
- [AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw/blob/be4ba4755bf1b52220f25e13b2293b5956590070/researchclaw/pipeline/experiment_diagnosis.py): typed execution deficiencies.
- [autoresearch-robotics](https://github.com/jellyheadandrew/autoresearch-robotics/blob/ff30cc481af9343b9c96f448b5ed72b75bfcd562/program.md): visual rollout feedback.
- [R&D-Agent](https://github.com/microsoft/RD-Agent/blob/484776c211e4fbbeef03e0ec00d6bbee7362a4f4/rdagent/core/proposal.py): hypothesis/experiment/feedback lineage.
- [EvoScientist AutoSkills](https://github.com/EvoScientist/EvoScientist/blob/8a05cae32ec8d23a077eeba07030cf7ded2951b4/EvoScientist/memory/agents/autoskills.py): scoped lessons and update proposals.
