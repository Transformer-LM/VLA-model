# P025-v2 endpoint-fidelity gate

Status: **failed / protocol branch killed**

P025-v2 restored the MuJoCo state saved immediately before the preceding
action chunk, replayed that one chunk, and required the resulting state to
match the policy rollout's saved candidate boundary.  All eight previously
identified policy boundaries failed the preregistered eligibility test.

| Boundary | Saved-boundary error | Repeat error | Main failure |
|---|---:|---:|---|
| goal_t0 c11 | 0.026347 | 0.007106 | saved-boundary mismatch |
| goal_t1 c04 | 0.018250 | 0.082773 | mismatch; repeat cap |
| goal_t1 c05 | 0.018142 | 0.023851 | mismatch; repeat cap |
| goal_t1 c10 | 0.605109 | 1.741218 | mismatch; repeat cap; contact instability |
| goal_t2 c03 | 0.007978 | 0.082858 | repeat cap |
| goal_t2 c06 | 0.231282 | 0.231283 | mismatch; repeat cap; contact instability |
| goal_t2 c08 | 0.271909 | 0.271915 | mismatch; repeat cap; contact instability |
| goal_t2 c09 | 8.162394 | 8.155342 | mismatch; repeat cap; contact instability |

The absolute repeat and saved-endpoint caps were both 0.01.  No invalid
boundary entered the witness denominator; all artifacts recorded zero charged
budget and zero witnesses.  Therefore the older P022/P024 witness counts are
not admissible evidence for the ISRAC claim.

Diagnosis: an intermediate MuJoCo state does not include all low-level
controller history.  Restoring it and replaying only the preceding eight-step
chunk does not reproduce the original policy boundary.

One protocol repair is allowed before abandoning ISRAC: restore the episode's
step-zero state and replay the complete action prefix, so controller history is
rebuilt naturally.  This is P025-v3.  If v3 also fails endpoint repeatability,
the current ISRAC implementation route is killed rather than relaxing the
threshold.

Remote evidence:

- `<PERSONAL_RESEARCH_ROOT>/results/israc/P025V2_GATE_*.json`
- `<PERSONAL_RESEARCH_ROOT>/results/israc/P025V2_endpoint_gate.log`
