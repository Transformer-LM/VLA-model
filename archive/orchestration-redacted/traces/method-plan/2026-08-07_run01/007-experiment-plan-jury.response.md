# Experiment-plan jury

**Verdict: NO-GO** for both isolated scientific implementation and the measured <=2 GPUh pilot. Scaffolding-only work is possible, but no result-bearing pilot should start. Full Stage 1 is not assessed or authorized.

## Fatal defects and exact fixes

1. **Circular host-checkpoint ordering.** Cache/head/A-B-C/P-Q are run before the 1k/5k/10k screen selects the frozen host. These artifacts depend on the selected host representation.

   **Fix:** Move R010-R012 immediately after preflight/evaluator validation, lock the winning checkpoint hash, then run R002-R009. Alternatively, add and pass a tensor-level proof that all candidate checkpoints produce identical `h` and action-head outputs.

2. **The frozen implementation specification is incomplete and internally inconsistent.** The state/action branches output 256+128 dimensions, but the concatenated MLP input is not defined as 384. Gate-changing details are also absent: exact losses, nMSE/R2 definitions, bootstrap confidence/resampling seeds, nuisance-ridge cross-fitting, control architectures, C cost scaling/bin-merge/tie rules, `B_N` construction, Q sampling seed/tie rule, preprocessing, normalization statistics, and complete personal-only input paths/hashes.

   **Fix:** Freeze one machine-readable config plus input manifest defining all these items, including source/environment lock, Qwen/DINO/data/action-stat/evaluator paths and hashes. Resolve the decoder explicitly, e.g. `256 + 128 -> 384 -> 256 -> 64`.

3. **Outcome ordering does not fully prevent leakage.** R007/R008 expose seed-0 treatment and P/Q diagnostics before checkpoint/seed-count decisions; the complete ordered training-seed list is not preregistered. "Freeze before remaining outcomes" does not protect against already-visible seed-0 outcomes.

   **Fix:** Freeze checkpoint first, preregister the complete ordered seed list before R007, and make R013 an automatic timing-only decision over a sealed ledger. Quarantine treatment/P-Q metric files until checkpoint and seed-count artifacts are hashed.

4. **The 2.0/7.2/8.0 GPUh ledger is not yet deterministic.** The 500-rollout term is correct and 7.2->8.0 provides a sensible margin, but R008 seed-0 P/Q appears in `H_spent` while `n*u_PQ` may charge it again. Fold-4/parity traces and the conditional 520-step timing trace are not assigned unambiguously, and a hard 2 GPUh cap lacks a pre-launch worst-case admission rule.

   **Fix:** Define disjoint ledger terms. If R008 is the final seed-0 P/Q build, use `(n-1)*u_PQ`; if discarded, retain `n*u_PQ` and label/hash it pilot-only. Include fold-4, reserved traces, loads/retries, and the conditional full-horizon trace. Before every pilot launch require `spent + worst_case(next) <= 2.0`; R013 must compute the frozen <=7.2 projection automatically. Actual execution must still stop at 8.0.

5. **Personal-only/GPU safety is not executable as literally written.** "All reads/writes strictly under `<PERSONAL_RESEARCH_ROOT>`" conflicts with required read-only GPU/process/OS/runtime inspection. R000 alone also cannot enforce the per-launch GPU rule.

   **Fix:** Clarify that all project/data/artifact filesystem I/O is confined to `<PERSONAL_RESEARCH_ROOT>`, while read-only OS/device/runtime inspection is allowed; writes to system/shared/team paths remain forbidden. Use a mandatory launch guard that logs physical UUID/occupancy immediately before every launch: use idle GPU 2/3 first; GPU 0/1 only from one fresh snapshot in which all four GPUs are idle, with 2/3 allocated first. Never kill or attach to unrelated processes.

The model-policy-environment evidence is sufficient for the proposal's narrow claim ceiling after these fixes. The <=2 GPUh pilot alone can establish only implementation feasibility, C0 predictive validity, optimizer/P-Q feasibility, and timing--not C1 controlled environment effect or C2 reliance. The round-4 READY verdict was a method review and does not resolve these execution blockers.
