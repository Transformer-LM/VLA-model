# Research Findings

## 2026-08-30 — Interaction-fingerprint belief pilot

### What was tested

A privileged-headroom gate tested whether true per-object mass/friction materially improves object identity association after action-conditioned interactions over shared dynamics. Shared and oracle variants used identical v5 data, code, fixed steps and three seeds.

### What failed

- Shared `hard_id` assignment: 95.5322%.
- Oracle assignment: 96.1150%.
- Gain: 0.5828pp versus a preregistered 5pp requirement.
- Seed 11 degrades by 0.8159pp.
- Pose-only reaches 96.39% on the supposedly hard split.
- Because shared is already 95.53%, a perfect oracle could improve by only 4.47pp; the 5pp gate is mathematically unreachable on this realized baseline.

### Interpretation

The current benchmark does not expose usable marginal headroom for mass/friction-based identity fingerprints. This is partly a ceiling/benchmark-design failure, not evidence that physical response is universally useless. The IFB method itself and full-history comparisons remain untested because the registered gate correctly stopped them.

### Constraints for future attempts

- Do not rerun M1b on this dataset.
- Do not lower the 5pp threshold post hoc.
- Do not call random-address assignment error a downstream task failure.
- Do not generalize to RGB perception, long-horizon VLA memory, recovery, or real robots.
- A new pivot must first produce pose-only-unsaturated ambiguity, new dataset seeds, a feasible preregistered oracle ceiling, and per-example prediction archives.
