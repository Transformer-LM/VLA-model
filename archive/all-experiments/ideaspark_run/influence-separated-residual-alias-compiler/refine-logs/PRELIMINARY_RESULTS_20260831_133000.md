# ISRAC preliminary results — 2026-08-31 13:30 +08:00

## Scope

These are M0 engineering results only. They validate the certificate and one
native MuJoCo physics mechanism with scripted controls. They do **not** yet
support automatic compiler yield, frozen-policy top-K support, WAM correction
harm, VLA improvement, cross-engine transfer, or the final paper claim.

## Completed checks

1. Local and remote certificate unit tests: 4/4 passed.
   - a valid physical alias is accepted;
   - action-indexed physics is rejected;
   - target-WAM leakage into the compiler objective is rejected;
   - a candidate outside top-K is rejected.
2. Existing personal LIBERO substrate was audited and reused:
   - deterministic snapshot restore and action replay had already recorded
     exact state/trace replay on the registered environment;
   - all new results remain below `<PERSONAL_RESEARCH_ROOT>`.
3. A real LIBERO/MuJoCo target-friction pair was executed.

## Run outcomes

| Remote artifact | Outcome | Factual RGB/depth/proprio | Factual state max diff | Candidate task-effect separation | Interpretation |
|---|---:|---:|---:|---:|---|
| `R001_libero_native_friction_m0_v1.json` | FAIL | 0 / 0 / 0 | `1.9762e-12` | `1.0819e-3 m` | Correctly exposed an over-strict zero tolerance. Preserved as failure evidence. |
| `R002_libero_native_friction_m0_v2.json` | PASS | 0 / 0 / 0 | `1.9762e-12` | `1.0819e-3 m` | Passed the pre-existing MuJoCo `1e-10` numerical floor. First divergence and friction/slip activation were both frame 0. |
| `R003_libero_friction_extreme_steps32.json` | PASS | 0 / 0 / 0 | `2.3207e-12` | `1.8047e-2 m` | Stronger bounded friction contrast and longer chunk produced an 18.05 mm physical effect separation without factual visual/proprio drift. |
| `R004_libero_on_relation_steps32.json` | FAIL before certificate | n/a | n/a | n/a | The inherited pre-state constructor could not create a stable bowl-on-plate state; this is a task-adapter limitation, not positive evidence. |

In both passing runs the target WAM was absent from the search objective. The
first candidate divergence coincided with the registered native-friction slip
activation frame.

## Current decision

- M0 certificate logic: **PASS**.
- LIBERO one-mechanism feasibility: **PASS, preliminary**.
- Cross-task automation: **not yet passed**.
- RoboTwin/SAPIEN: **not ready**; the personal checkout is source-only and the
  installed personal environments do not contain SAPIEN/assets.
- GPU gate: **not opened**. Four A100s were idle at the audit instant, but the
  novelty claim still depends on automatic multi-task/multi-engine compiler
  yield, so no large GPU job was launched.

## Next falsification steps

1. Replace the single hard-coded friction block by enumerated native parameter
   blocks and automatic influence-zero screening.
2. Replace scripted candidate controls by frozen π0.5 top-8 chunks.
3. Compare certified-pair yield against random/grid/CMA-ES at matched simulator
   calls.
4. Repair the second LIBERO relation adapter without per-instance tuning.
5. Stage a complete personal SAPIEN/RoboTwin environment offline, then repeat
   the same certificate protocol.

## Code provenance

- `implementation/israc/certificate.py`: `3f349d845fd17e3512436883fba787cd4479659ddb33d4baa90b067c791a8f0c`
- `implementation/libero_m0_alias.py`: `3cb275fcaf5dc017995379c4780237f7368abb2c6cabf80ffdec39db76c77279`
- `implementation/smoke_libero_env.py`: `0a23144007011dec2e280ab577877fc92a4f7122358fed2ab59616a60967d8d2`
