# Experiment Log

## 2026-08-29/30 — Interaction-fingerprint belief pilot, v5

- Environment: MuJoCo 2.3.7; PyTorch 2.7.1+cu126; NVIDIA A100; personal user directory only.
- Main data: 12,000 episodes, SHA-256 `5484a9923229b306beafbf72f4e2123ed79f66ba46b797d314a3182bed1fbfb7`.
- Runs: shared and GT-property oracle, seeds 11/22/33, 80 epochs and 2,000 optimizer steps each.
- Result: shared 95.5322%, oracle 96.1150% on `hard_id`; gain 0.5828pp.
- Gate: **KILL** because gain <5pp and seed 11 gain <0.
- Follow-up: M1b was not run.
- Evaluation type: simulation-only with simulator-provided ground truth and privileged oracle state.
- Integrity: core KILL supported; overall historical audit FAIL due stale tracker/incomplete audit-time archive; scope warning remains.

See `refine-logs/EXPERIMENT_RESULTS_20260830_001250.md` for the qualified result and `EXPERIMENT_AUDIT.md` for the integrity verdict.
