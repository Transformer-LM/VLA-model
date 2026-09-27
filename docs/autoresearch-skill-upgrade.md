# VLA/WAM research skill upgrade

Base: `research-sync-20260904`, commit `80e39e898943d11a0d3b075c9bbc1180ea6480d6`.

## Changes

- Preserve the existing eight-phase research workflow and WAM taxonomy.
- Enforce phase-specific artifacts, hash freshness, archived revisions and dedicated
  audit/review adjudication. Old states remain readable; unverified completions reopen.
- Add resource reservation and idempotent settlement, including failed jobs.
- Record immutable experiment nodes with hypothesis/parent IDs and protocol binding.
- Add deterministic execution diagnosis and visual-rollout diagnostic guidance.
- Resolve metrics by JSON key path, bind current audits, and distinguish pilot/main
  scope. Enforce configured training-seed minimums for main claims.
- Replace axis-count novelty scoring and empty-search novelty with explicit coverage
  and unresolved outcomes. Route idea generation through the selected provider and
  the actual project compute budget.
- Select WAM evidence per claim; preserve statistical uncertainty and negative results.
- Add scoped lessons and a skill-update proposal procedure. Existing skills remain the
  execution interface; no external autoresearch framework is installed.
- Synchronize both distributed copies of embodied-autoresearch. Historical archive
  files and completed research results are untouched.

## Validation

Run on Python 3.12 with no GPU, API key or model calls:

```text
python -X utf8 skills/embodied-autoresearch/tests/test_contracts.py
```

24 behavioral regression tests cover a complete negative-result dossier, bogus
artifacts, failed literature coverage, changed evaluator/raw results, stale revisions,
metric-key mismatch, insufficient main seeds, reservations, duplicate settlements,
overruns, nonfinite usage, reopening, legacy states and phase-local skill resolution.
Skill frontmatter is checked with skill-creator's quick_validate.py in UTF-8 mode.

### Follow-up audit (2026-09-27)

- Fixed omission of settled failed/cancelled jobs from experiment registration.
- Bound direct claim metrics to cited completed experiments. Separate aggregates
  now declare contributors and a versioned, hash-bound analysis script.
- Recompute budget status after configuration changes while retaining actual usage
  and active reservations; this does not grant permission to raise compute limits.
- Added four regression cases including rejection and recovery paths for these fixes.
- Confirmed origin is `Transformer-LM/VLA-model`, based on `research-sync-20260904`.
  GitHub connector identity is `qsgg686-coder`, with `push: false` at this audit;
  local commits must not be described as uploaded.

## Operational limits

- This is a skills/runtime-contract upgrade, not a completed VLA training experiment.
- The ledger records and validates reservations; the runner/scheduler must actually
  enforce process timeouts, editable file scope and execution permissions.
- Hashes and JSON linkage prove consistency, not scientific truth or that an external
  process honestly generated the data. Reviewers still inspect raw execution evidence.
- Model-family provenance is recorded metadata, not an attestation service.
- Aggregate lineage is declared metadata; the checker does not rerun statistics.
- Main-claim seed gating currently targets training studies; frozen-policy episode
  replication needs a separately reviewed acceptance design.
- Real-robot execution still requires a separate explicitly authorized adapter.
- Some ARIS dependencies are not bundled in this sanitized snapshot. Preflight reports
  their absence at the phase that needs them; it does not silently install archives.
- New experimental protocols use new runs, with baseline re-evaluation where needed.
- Scoped lesson promotion is a documented workflow, not automatic self-modification.

Source-level design references and exact artifact schemas are in
[`execution-contracts.md`](../skills/embodied-autoresearch/references/execution-contracts.md).
