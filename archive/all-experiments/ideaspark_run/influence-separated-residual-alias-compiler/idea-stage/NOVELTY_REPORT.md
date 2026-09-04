# ISRAC Fresh Novelty Decision

- Review route: fresh `gpt-5.6-sol` reviewer, same-family; acceptance is **provisional**.
- Full trace: `.aris/traces/novelty-check/2026-08-31_run03/`.
- Closest overall work: **Metamorphic Testing of Vision–Language Action–Enabled Robots**.
- Closest feedback interface: **Feedback World Model Enables Precise Guidance of Diffusion Policy**.
- Closest general failure theory: **Imperfect World Models are Exploitable**.
- Closest search baselines: Bayesian-optimization controller falsification, BEACON, constraint-supported metamorphic testing.

## Verdict

- Before a matched-call advantage: **6.6/10 (6.1–7.2), not yet >7**.
- After a robust ≥2× matched-call yield advantage across multiple mechanisms/tasks and ideally a second simulator: **7.4/10 (7.0–7.9), conditionally defensible**.

The 24 current LIBERO pairs support feasibility only. They do not establish method novelty or WAM correction harm.

## Fatal condition

Kill or downgrade the method if the strongest matched-call random/grid/CMA-ES/BO baseline has equivalent or better certified-pair yield, or if the result requires task-specific/action-indexed switches, target-WAM leakage, unsupported candidates, or relaxed equality thresholds.
