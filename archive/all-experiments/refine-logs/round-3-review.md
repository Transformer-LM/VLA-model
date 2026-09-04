# Round-3 Method Review

<details open>
<summary>Full raw reviewer response</summary>

**CALIBRATION: none. Same-family provisional.**

Problem Anchor PRESERVED; drift NONE; dominant contribution SHARPER; simplicity TIGHT.

| Dimension | Score |
|---|---:|
| Problem Fidelity | 10.0 |
| Method Specificity | 8.7 |
| Contribution Quality | 8.0 |
| Frontier Leverage | 9.0 |
| Feasibility | 8.0 |
| Validation Focus | 8.4 |
| Venue Readiness | 6.5 |
| **Weighted composite** | **8.6/10** |

**Verdict: REVISE.**

The deployment route closes Round-2's main blocker: Stage 2 uses only rollout-available A/B adapter outputs and DINO remains offline. Fold roles and horizon-aware accounting are improved.

## Remaining blockers

1. Define the learned basis as an actual projector: Pi_pred=B_pred B_pred^T and v_pred=W^+ Pi_pred W(bar_delta-mu). W+ is only the linear pseudoinverse and never restores the mean. Add a numerical nuisance-annihilation gate for the learned P and Q.
2. A nonsignificant Q permutation test does not establish equivalence. On locked fold 4 require P incremental R2 point >=.02 with episode-bootstrap lower bound >0, and Q episode-bootstrap upper bound <=.005. Permutation tests are supporting only.
3. Every selected seed must independently produce frozen artifacts and pass its specified gates; no seed drop/replacement. Every D_post fold needs at least one episode from each task. Distinguish Stage-1 eligibility from Stage-2 eligibility.
4. Use u_roll=1.10*(max(t_fail,t_screen_max)+t_wrap)/3600 so wrapper overhead is always added, including a separately forced full-horizon trace.

The remaining venue risk is inherent PFD overlap and narrow scope; do not add architecture or benchmarks.

</details>

