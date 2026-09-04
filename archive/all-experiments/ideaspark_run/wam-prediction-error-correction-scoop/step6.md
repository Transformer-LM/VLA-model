# Step 6 — Comparison

Timestamp: 2026-08-31 Asia/Shanghai

- Proposed work
  - Problem: online correction of WAM future errors from executed observations.
  - Mechanism: feedback/residual state injected into subsequent action-conditioned predictions.
  - Insight: execution reveals free prediction-error supervision.
  - Domain: WAM-guided VLA/manipulation.
- Feedback World Model
  - Matches all four axes. Level 1 — Full Overlap.
- ReDRAW
  - Matches problem, residual mechanism, and broad insight; differs in offline sim-to-real MBRL domain/regime. Level 2 — High Overlap.
- Say, Dream, and Act
  - Matches problem/domain/real-observation correction insight; mechanism corrects action rather than WM. Level 2 — High Overlap.
- When to Trust Imagination
  - Matches problem/domain/feedback insight; mechanism verifies and replans. Level 2 — High Overlap.
- CheckVLA
  - Matches problem/domain/action-conditioned discrepancy; mechanism repairs suffix and re-anchors. Level 2 — High Overlap.
- DreamX-Phi 1.0
  - Matches error problem and WAM domain; uses training-time geometry/object constraints. Level 3 — Medium Overlap.
- tau0-WM
  - Matches WAM/VLA domain and action rectification use; no realized-error feedback correction. Level 3 — Medium Overlap.

Worst case: Feedback World Model, 4/4 axes, Level 1.
