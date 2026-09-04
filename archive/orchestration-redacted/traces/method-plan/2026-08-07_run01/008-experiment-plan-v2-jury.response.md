# PGR-Audit v2 execution jury

**Overall verdict: CONDITIONAL-GO**

This verdict is bound exclusively to freeze-manifest SHA256 `0bae1d7bb2e2be50ae60ef6d75f7f30c50db4e63221e399930dbf61e9d84eae1`. Any byte change to a listed input invalidates it and requires a new manifest and renewed jury.

**Reviewer:** fresh `gpt-5.6-sol`, `xhigh`; same-family provisional; no human calibration.  
**Review mode:** local, read-only; no remote connection, filesystem mutation, or scientific execution.

## Byte and hash verification

All eight listed files were read fully as raw bytes. Every declared SHA256 matched; all are valid UTF-8 without BOM, and all applicable JSON files parse.

| Artifact | SHA256 |
|---|---|
| Protocol | `a5de33299f74db4118e075f8db05cc9196f0816a014121a3b8d807b959662752` |
| Active config | `c70f5361352f449800ba4e5af9dc408eb1d706c0f26549b393cbfe4fe788008c` |
| Input manifest | `03a90ce95b29eb70fbbb73c59f7e795f0d5336663c7f0d5c012d71940953e510` |
| Final proposal | `d429c9fcc95b8e8c67e07b8388e7a3e70b6f0e317a66037428b6253edb04d9f7` |
| Experiment plan | `bdfab405a8ef69352830d061545b832e90870425bbfa9bfd50ba2db6d157fb87` |
| Experiment tracker | `91536e2152f414421e91ecb6c9feb4c7740bb8544c8e76e7c62e7327b56c0847` |
| Research contract | `045b46f24897e62e63e920ab754b7c58d4bd7a667568f358097e260af9fe4b1d` |
| Preregistration lock | `ceaeac2f514eae9645301b016ad5973e1627ce6b9a61f427b14a9aa1c5073750` |
| Freeze/bundle manifest | `0bae1d7bb2e2be50ae60ef6d75f7f30c50db4e63221e399930dbf61e9d84eae1` |

A `response_sha256` should be computed over the final persisted response bytes by the persisting executor; no unverifiable self-hash is asserted here.

## Scope verdicts

| Scope | Verdict | Exact authorization |
|---|---|---|
| **A — isolated implementation** | **GO** | May create the isolated runtime only under logical `<PERSONAL_RESEARCH_ROOT>`, resolving under `<PERSONAL_RESEARCH_ROOT_ALIAS>`, from the pinned clean bundle/commit. Enforce `umask 077`, UUID outputs, realpath/symlink guards, personal caches/logs/tmp, no shared/team I/O, no egress, no dirty-source runtime, no privilege/global-environment changes, and no scientific outcomes. |
| **B — engineering canary** | **CONDITIONAL-GO** | Only after A, CPU/static tests, fresh implementation review, and runtime re-verification of every used digest and checkpoint’s exact 730-key allowlist. It may test CUDA/model load, determinism, synthetic engineering parity, sealing, memory, and throughput only. It may not read future targets, fit scientific caches/heads, produce task success, train treatments, or expose scientific comparisons. Each launch requires the frozen GPU guard. |
| **C — all-ten treatment-blind screen** | **NO-GO on this bundle** | Blocked by the preregistration timing contradiction below. Future authorization requires repair, new hashes/manifest, renewed jury, and A/B completion. Then the 150 records must remain sealed until `selected_checkpoint.json` and `primary_task_set.json` are atomically persisted and hashed before detail reveal or C0/cache work. |
| **D — simulation Stage 1 / conditional Stage 2** | **NO-GO on this bundle** | Requires a newly frozen, re-juried bundle; a qualifying all-ten screen; frozen primary tasks; passing C0; fixed-C gates; all 20 mandatory seeds and eligibility rows; one-time fold4; then exactly 6000 sealed Stage-1 rollouts. Stage 2 additionally requires passed Stage 1 and all Stage-2 eligibility rows, then exactly 4000 sealed rollouts. No seed replacement, adaptive reduction, scientific retry, or missing-record waiver. |
| **E — real-contract preparation** | **GO** | Offline specification work only, under the personal root. Exact endpoint/interface/domain/task/data/safety/E-stop material may be collected and frozen, but there may be **zero robot connectivity, observe-only probing, command transmission, or motion** under this scope. |
| **F — live robot connectivity/motion** | **NO-GO** | The endpoint allowlist is empty and `live_action_authorized_now=false`. F remains blocked pending a separately frozen exact endpoint/interface/embodiment/domain/task/data/control/safety/E-stop/operator/approval contract, compatible RobotAdapter review, and a separate hash-bound safety/scientific jury. Receipt of prose or endpoint facts does not unlock connectivity or motion automatically. |

## Scientific and execution assessment

- **Identifiability:** Strong and appropriately narrow. C0 isolates held-out action-conditioned association; A/B/C separates valid-target training from action-only exposure and a fixed matched placebo; C2 uses preregistered nuisance removal, P/Q matching, fold separation, parity, and support gates. Claims remain task-local and prohibit causal-mediation, SOTA, and broad generality language.
- **Leakage and sealing:** The protocol itself has strong deterministic partitions, treatment-blind checkpoint/task selection, strict-test/fold4 one-open semantics, cohort quarantine, restricted pre-reveal telemetry, and preservation of failed attempts. The preregistration conflict below currently breaks bundle-level agreement.
- **Retry policy:** The protocol’s single unchanged-hash retry for enumerated pre-outcome infrastructure failures is adequate. Scientific failures, nonfinite seeds, post-action failures, and terminal missing records cannot be retried, replaced, imputed, or waived.
- **Splits and estimands:** Episode-level task-stratified allocation, role-separated seeds, 20 fixed seeds in cohorts `0..9` and `10..19`, paired seed-task-state records, cohort-specific estimands, exact sign gates, effect floors, and bootstrap units are sufficiently deterministic.
- **Feasibility:** Computationally heavy but finite. Qwen/DINO plus the adapter/projector path is plausible on the pinned A100-40GB environment. Runtime, memory, and simulator throughput remain engineering facts to establish in B. There is intentionally no GPU-hour admission cap.
- **Input provenance:** The complete personal LIBERO-10 tree, all ten task metadata, source/runtime trees, Qwen/DINO artifacts, candidate checkpoints, normalization data, environments, and relevant clean-source blobs are hash-pinned and require runtime re-verification.
- **Paths/network:** Personal-root containment, read-only OS/device exceptions, `liu_meng` SSH identity, existing SSH control path only, no Internet egress, and no team/shared data are explicit and executable.
- **GPU reservation:** The two-snapshot atomic per-UUID reservation contract is adequate. Physical GPUs 2/3 are preferred; 0/1 may be used independently only when that candidate is freshly idle. All-four idleness is not required. Post-bind UUID/PID/PGID verification and no-preemption/no-sharing rules are mandatory.
- **Budget:** `gpu_hour_cap=null`; pilot and total caps are null; GPU time is telemetry/provenance and hung-job control only, never admission or seed-count control.

The prior v1 NO-GO remains historical and is not inherited as a pass. V2 substantively repairs all five v1 defects: checkpoint ordering, specification completeness, seed/outcome leakage, budget-ledger coupling, and executable personal/GPU safety. The current blockers are new frozen-bundle inconsistencies.

## Blocking defects and smallest repairs

1. **Circular primary-task freeze**

   - File/key: `refine-logs/PREREGISTRATION_LOCK.json` → `future_state_outputs.selected_task_set.may_be_created_only_after`
   - Current value: after the C0 gate.
   - Conflict: protocol `checkpoint_screen.selector_output`, `detail_reveal`, `scored_tasks`, and `task_eligibility` require the treatment-blind primary set to be produced by the baseline screen and frozen before screen-detail reveal and before C0.
   - Smallest repair: replace the value with “after all 150 sealed screen records validate and the automatic selector fixes the checkpoint/task eligibility, before detail reveal and before any cache or C0 access.” Then regenerate the preregistration and bundle hashes and renew the jury.

2. **Terminal-missing-record waiver ambiguity**

   - Files: `refine-logs/EXPERIMENT_PLAN.md`, S4 final paragraph; `idea-stage/docs/research_contract.md`, “Scientific and technical failure.”
   - Current summaries say a claim may wait for an accepted/resolved missingness disposition.
   - Conflict: protocol `failure_and_retry.incomplete_sealed_batch` permanently fails the affected stage claim and explicitly forbids audit waiver, imputation, or conversion into a claim.
   - Smallest repair: state verbatim-equivalent permanent claim-gate failure after the one allowed technical retry; audit may explain missingness only.

3. **Robot force/torque requirement understated**

   - File/section: `idea-stage/docs/research_contract.md` → “Real-robot contract,” which calls force-torque identity optional.
   - Conflict: protocol `validation_lanes.real_robot.required_before_live_action` requires a calibrated force/torque sensor or controller joint-torque/force-estimate source; without either, motion is forbidden.
   - Smallest repair: make one of those telemetry sources mandatory and preserve the zero-motion fallback.

Because repairing any listed file changes the frozen bundle, conditions 1–3 do not automatically unlock C, D, or F: they require a new manifest and renewed hash-bound jury.
