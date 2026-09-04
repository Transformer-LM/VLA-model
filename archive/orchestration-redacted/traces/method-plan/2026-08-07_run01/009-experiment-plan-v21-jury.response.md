# PGR-Audit v2.1 renewed execution jury

**Overall verdict: CONDITIONAL-GO**

Bound exclusively to freeze-manifest raw-byte SHA256:

`21267bf7a0b34d1f101398963011697ea451a6a4a5869dd97317319bd637ea6f`

**Reviewer:** fresh `gpt-5.6-sol`, `xhigh`; same-family provisional; no human calibration.  
**Mode:** local read-only; no file modification, remote connection, or scientific execution.

## Hash verification

All eight files were independently read and hashed as raw bytes. Every hash matches the manifest. All are valid UTF-8 without BOM; applicable JSON parses.

| Artifact | SHA256 |
|---|---|
| Protocol | `a5de33299f74db4118e075f8db05cc9196f0816a014121a3b8d807b959662752` |
| Active config | `c70f5361352f449800ba4e5af9dc408eb1d706c0f26549b393cbfe4fe788008c` |
| Input manifest | `03a90ce95b29eb70fbbb73c59f7e795f0d5336663c7f0d5c012d71940953e510` |
| Final proposal | `d429c9fcc95b8e8c67e07b8388e7a3e70b6f0e317a66037428b6253edb04d9f7` |
| Experiment plan | `06b1118f3c02270955580eddf1cccf657675e8ccab862205a5351e5d5152bc38` |
| Experiment tracker | `91536e2152f414421e91ecb6c9feb4c7740bb8544c8e76e7c62e7327b56c0847` |
| Research contract | `f43c47c7da1984a91ac09ea24b070d6ffd2eb93f9f60301c4d0d3e201e9bf935` |
| Preregistration lock | `77ff495b74a9102bd2948d22c0b202b1311b96ade26d4b8f623ad91657ec09d8` |
| Freeze manifest | `21267bf7a0b34d1f101398963011697ea451a6a4a5869dd97317319bd637ea6f` |
| Prior jury response, independently verified | `7ea5a1c062e68214cf39a902bb5cb8dd9ac7d6d36a327a7c80c9427469c20910` |

A final `response_sha256` must be computed from the persisted response bytes; no self-referential hash is asserted.

## Repair verification

All three prior inconsistencies are fully repaired, with no new bundle inconsistency found:

1. `PREREGISTRATION_LOCK.json → future_state_outputs.selected_task_set.may_be_created_only_after` now requires all 150 sealed treatment-blind records, automatic checkpoint/task selection, and atomic freeze before detail reveal, cache, or C0.
2. `EXPERIMENT_PLAN.md → S4/Stop conditions` and `research_contract.md → Scientific and technical failure` now permanently fail the affected claim gate after the single allowed technical retry. Audit explanation is permitted; waiver, imputation, replacement, or claim restoration is forbidden.
3. `research_contract.md → Real-robot contract` now requires either calibrated force/torque telemetry or controller joint-torque/force-estimate telemetry. If neither exists, motion is forbidden, matching `PGR_AUDIT_PROTOCOL.json → validation_lanes.real_robot.required_before_live_action`.

## Scope verdicts

| Scope | Verdict | Authorization |
|---|---|---|
| **A — isolated personal implementation** | **GO** | Authorized from the pinned clean bundle, solely under the logical personal root resolving beneath the canonical personal root. RobotAdapter remains default-off; no scientific outcomes. |
| **B — engineering-only canary** | **CONDITIONAL-GO** | After A, passing CPU/static tests, fresh code review, runtime re-verification of every used digest and checkpoint’s exact 730-key allowlist, and a fresh filesystem/GPU reservation guard. Engineering telemetry only; no scientific targets, success evaluation, cache/head fitting, treatment outcomes, or comparison reveal. |
| **C — all-ten treatment-blind screen** | **CONDITIONAL-GO** | After A and B pass. Run exactly 150 sealed records; the automatic selector must atomically hash the checkpoint and primary-task manifests before any screen-detail reveal, cache, or C0 access. |
| **D — Stage 1 and conditional Stage 2** | **CONDITIONAL-GO** | After C qualifies and the frozen C0, C-map, twenty-seed, parity, fold4, and eligibility gates pass. Stage 1 is exactly 6000 sealed rollouts. Stage 2 is exactly 4000 and additionally requires passed Stage 1 plus every Stage-2 eligibility row. No seed replacement, adaptive reduction, scientific retry, or missing-record waiver. |
| **E — offline robot-contract preparation** | **GO** | Offline preparation only under the personal root, with zero robot connectivity, probing, command transmission, or motion. |
| **F — live robot** | **NO-GO** | No connectivity or motion is authorized by this bundle. |

Thus the repaired bundle authorizes **A–E as scoped above**. **F remains NO-GO.**

## Full execution assessment

The bundle remains scientifically identifiable through the sequential C0 control/derangement gate, A/B/fixed-C controlled training, and fold-separated P/Q removal test with narrow claim ceilings. Leakage controls, treatment-blind selection, strict-test/fold4 one-open semantics, cohort quarantine, restricted pre-reveal telemetry, and immutable failed-attempt retention are coherent.

Splits, RNG roles, paired seed-task-state estimands, sign/effect gates, and bootstrap units are deterministic. The full personal LIBERO-10 tree and all ten tasks are pinned; both fixed cohorts `0..9` and `10..19` are mandatory. Cardinalities agree at 150 screen, 6000 Stage 1, and conditional 4000 Stage 2.

Personal-only path containment, zero Internet egress, clean-source isolation, atomic fresh per-UUID reservations, second snapshots, UUID/PID/PGID verification, GPU 2/3 preference, independently conditional GPU 0/1 use, and no preset GPU-hour cap are consistent. The real-robot lane remains independent of simulation but live-locked.

## Remaining blocker

Only F is blocked:

- File/keys: `refine-logs/PGR_AUDIT_PROTOCOL.json → host_environment.robot_endpoint_allowlist_now`, `validation_lanes.real_robot.required_before_live_action`, and `real_robot_safety.live_action_authorized_now/blocker/unlock`.
- Current state: empty endpoint allowlist and `live_action_authorized_now=false`.
- Smallest valid resolution: create and hash a **separate** exact endpoint/interface/embodiment/domain/task/data/control/safety/E-stop/operator/approval contract, verify the compatible RobotAdapter implementation, then obtain a separate hash-bound safety/scientific jury. This is not an in-place repair to the present bundle.
