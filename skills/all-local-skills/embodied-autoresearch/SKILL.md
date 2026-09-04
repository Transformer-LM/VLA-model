---
name: embodied-autoresearch
description: Run a resumable, evidence-gated autonomous research workflow for embodied AI, VLA, World Action Models, latent dynamics, and model-based RL. Use when the user asks to automate research, run research while unattended, go from a broad embodied direction to a validated idea and experiments, resume an interrupted VLA/WAM research run, or coordinate literature search, novelty checking, method refinement, code implementation, GPU experiments, integrity audit, claim validation, and iterative review without entering paper writing.
---

# Embodied AutoResearch

Act as the sole workflow owner for a VLA/WAM research run. Chain the installed
research skills, persist every phase, and stop at a validated research dossier.
Do not invoke the generic `research-pipeline` in parallel with this skill.

## Operating contract

- Default to simulation or offline data. Never operate a real robot without
  explicit approval for the exact experiment.
- Keep paper writing disabled. Stop after evidence synthesis unless the user
  separately requests a writing workflow.
- Treat same-family Codex review as `provisional`, never as independent
  scientific acceptance.
- Never fabricate a paper, citation, dataset, run, metric, checkpoint, log, or
  completed experiment. A missing artifact is a blocker, not an invitation to
  infer a result.
- Do not launch paid compute, exceed the configured GPU-hour ceiling, accept a
  dataset license, upload private data, or contact people without explicit
  authority.
- Preserve negative results and failed ideas. They are evidence and prevent
  repeated dead ends.

Read [references/pipeline-contract.md](references/pipeline-contract.md) before
running or resuming the pipeline. Read
[references/embodied-review-rubric.md](references/embodied-review-rubric.md)
before the evidence audit and review phases. Read
[references/configuration.md](references/configuration.md) only when creating or
changing configuration.

## Broad-field discovery mode

Use broad-field discovery when `research.exploration_level` is `field` or the
user asks to find broad research directions before choosing a specific problem.
In this mode:

- Treat the configured direction as a searchable parent field, not as a fixed
  hypothesis. Do not silently assume a robot embodiment, task family, benchmark,
  world-model representation, control role, or failure mode.
- Treat named topics such as video generation, latent dynamics, or model-based
  RL as seed topics to investigate, not as the only permitted routes.
- Map the field across representation, world-model role, policy/world-model
  coupling, learning regime, embodiment/task, evaluation evidence, and resource
  requirements.
- Produce `research-stage/DIRECTION_LANDSCAPE.md` with five to eight distinct
  macro directions. For each direction, state the core problem, why it matters
  now, method families, nearest-work density, unresolved gap, decisive evidence,
  data/compute needs, major risks, and a scored recommendation.
- Do not turn a recommended macro direction into the selected direction. If
  `automation.require_direction_checkpoint` is true and
  `research.selected_macro_direction` is empty, complete the evidence map, then
  block `idea-discovery` with the reason `awaiting human macro-direction
  selection`. This intentional checkpoint also stops unattended supervisors.
- After the user selects a macro direction, persist it in
  `research.selected_macro_direction`, resume `idea-discovery`, and only then
  formulate concrete ideas, hypotheses, benchmarks, and experiments.

`automation.auto_select_idea` never overrides the macro-direction checkpoint.

## Initialize or resume

1. Resolve a UTF-8 Python launcher in this order:
   - Windows project launcher:
     `.agents/runtime/research-skills/python-utf8.cmd`
   - `python`
   - `python3`
2. Resolve this skill directory from the loaded `SKILL.md`; do not assume a
   global install path.
3. If `.aris/autoresearch/active_run.json` is absent, run
   `scripts/bootstrap.py --root <project> --direction <user direction>`.
   Bootstrap copies the brief and configuration templates only when they are
   absent and initializes a run state.
4. Run `scripts/validate_project.py --root <project> --stage discovery --json`.
   Fix safe local issues automatically. If discovery itself is blocked, write
   the reason into state and stop.
5. If an active run exists, run `scripts/research_state.py --root <project>
   status --json`, inspect its artifacts, and resume the first nonterminal
   phase. Do not redo a phase whose gate already passed.

Use the state helper before and after every phase:

```text
research_state.py --root <project> begin <phase>
research_state.py --root <project> complete <phase> --gate pass \
  --acceptance deterministic --artifact <path>
```

On a genuine external blocker, use `block`; on a recoverable execution error,
use `fail`. Use `resume <phase>` only after the recorded condition changed.

## Execute the phases

Before executing a named dependency, read its complete
`.agents/skills/<name>/SKILL.md`, announce why it is being used, and follow it.
Do not launch two orchestrators for the same phase.

### 1. Contract

- Read `RESEARCH_BRIEF.md` and `AUTORESEARCH_CONFIG.json`.
- In broad-field discovery mode, use `wam-research` to produce
  `research-stage/FIELD_DISCOVERY_CONTRACT.md`: define the parent field, search
  boundaries, discovery axes, inclusion criteria, and explicit non-assumptions.
  A concrete hypothesis is not required yet.
- Otherwise, use `wam-research` to produce
  `research-stage/WAM_ROUTE_CARD.md`: classify prediction representation
  separately from control usage, state a falsifiable hypothesis shape, and
  identify unresolved embodiment, benchmark, data, action, and compute choices.
- Complete when the parent field or chosen direction is specific enough for
  literature discovery. Unknown compute or repository details may remain open
  until preflight.

### 2. Evidence map

- Initialize `research-wiki` if it is not already initialized.
- Use `paper-search` for broad, current discovery and `research-lit` for deep
  synthesis. Prefer primary papers and official repositories.
- Persist queries, dates, identifiers, source URLs, inclusion decisions, and
  unresolved collisions in `research-stage/LITERATURE_MAP.md`.
- In broad-field discovery mode, also write
  `research-stage/DIRECTION_LANDSCAPE.md` using the required macro-direction
  schema above. Cover video-generative WAM, latent dynamics, and model-based RL
  when supported by the evidence, while actively searching for routes outside
  those seeds.
- Complete only when every load-bearing statement is traceable, field coverage
  is explicit, and nearest-work clusters and contradictory evidence are visible.
- Enforce the macro-direction checkpoint before beginning `idea-discovery`.

### 3. Idea discovery

- In broad-field discovery mode, require a persisted selected macro direction;
  never infer one from the ranking in `DIRECTION_LANDSCAPE.md`.
- Run `idea-discovery-robot` with the selected direction, applicable route card,
  evidence map, simulation-first constraint, and only those embodiment or
  benchmark choices justified by the selected direction.
- Reclassify every shortlisted idea with `wam-research` and persist the result in
  `idea-stage/WAM_ROUTE_CARDS.md`.
- Run `novelty-check`; use `scoop-check` for the final concrete novelty claim.
- Auto-select the top idea only when novelty is not directly contradicted, a
  matched baseline exists, a cheap falsification pilot exists, and the idea is
  more than a component swap. Otherwise perform a structural pivot. Stop after
  the configured maximum idea cycles and report the blocker rather than forcing
  a weak idea.

### 4. Method and experiment plan

- Run `research-refine-pipeline` on the selected idea, route card, nearest-work
  collisions, and pilot constraints.
- Require `refine-logs/FINAL_PROPOSAL.md` and
  `refine-logs/EXPERIMENT_PLAN.md`.
- Ensure the plan contains model-, policy-, and environment-level endpoints;
  matched data/compute/interaction budgets; negative controls; oracle bounds
  where available; failure criteria; seeds; uncertainty; and staged run order.
- Write `refine-logs/PREFLIGHT_REPORT.md` identifying the chosen framework only
  after the evidence contract is fixed. Use `openpi`, `openvla-oft`, or
  `cosmos-policy` only when its assumptions match the selected route.

### 5. Implementation and experiments

- Run `validate_project.py --stage experiments --json` first. Block if the
  compute backend is unconfigured, required data or licenses are unavailable,
  or the requested execution exceeds authority or budget.
- Run `experiment-bridge` with code review and sanity-first execution enabled.
  It may use `run-experiment` for small run sets and `experiment-queue` for
  multi-seed or dependent waves.
- Use `weights-and-biases` and `training-check` when configured; otherwise retain
  local configs, stdout/stderr, checkpoints, and raw metric files.
- Never promote a sanity run, two-scene pilot, imagined rollout, or incomplete
  job to a main result.
- Account usage with `research_state.py record-usage` after every completed job.

### 6. Evidence audit and claim gate

- Run `analyze-results` on raw outputs with paired evaluation and uncertainty
  where applicable.
- Run `experiment-audit` before interpreting the results.
- Run `result-to-claim` only after the integrity artifact exists. An integrity
  `FAIL`, missing raw evidence, or phantom result blocks the claim gate.
- For `partial`, narrow the claim and record the missing evidence. For `no`,
  pivot or preserve the negative finding; do not polish it into a positive
  result.

### 7. Review and improvement

- Run `auto-review-loop` in `hard` mode, using
  [references/embodied-review-rubric.md](references/embodied-review-rubric.md)
  as additional reviewer instructions.
- Allow it to implement bounded fixes and rerun necessary experiments, but
  enforce the same compute, data, and real-robot gates on every round.
- Its score threshold is a repair-loop stopping heuristic only. Record base
  Codex verdicts as `provisional`; do not convert `almost` or score `6/10` into
  scientific acceptance.
- After fixes, rerun affected integrity and claim gates. Stale audits never
  cover changed code or new results.

### 8. Synthesis

- Run `ablation-planner` when the claim is `yes` or defensible `partial`, then
  execute only the ablations required by the evidence contract and budget.
- Write `research-stage/RESEARCH_DOSSIER.md` containing the route card, literature
  map, chosen and rejected ideas, hypothesis ledger, exact method, reproducible
  run manifest, raw-result pointers, statistics, integrity verdict, supported
  and unsupported claims, failure boundaries, reviewer status, remaining risks,
  and cheapest next discriminating experiment.
- Write `AUTORESEARCH_STATUS.md` as a short human dashboard.
- Complete the run only when deterministic artifact checks pass. Label the final
  assurance `provisional` unless an independent reviewer or human expert has
  accepted it.

## Failure and stopping policy

- Retry the same implementation failure at most three times and only when the
  next attempt changes something justified by logs.
- After two no-signal idea or experiment iterations, change a structural choice
  such as objective, data, representation, benchmark, or control usage—not just
  a learning rate.
- Stop on exhausted budget, unresolved integrity failure, missing authority,
  unavailable required data, or repeated no-progress. Persist the exact blocker
  and the smallest user decision needed to resume.
- Never use wall-clock repetition to rerun a verdict. Wait for new evidence,
  then invoke the verdict-bearing skill once.

## External unattended launcher

`scripts/run_autoresearch.ps1` is an optional terminal supervisor. It starts or
resumes Codex and retries only after observable state progress. Do not invoke it
recursively from an already-running Codex session. It never enables dangerous
sandbox bypasses and stops on completion, a recorded blocker, or repeated
no-progress.
