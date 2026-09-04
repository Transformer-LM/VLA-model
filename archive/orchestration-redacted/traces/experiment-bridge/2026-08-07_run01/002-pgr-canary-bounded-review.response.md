VERDICT: REVISE

CANARY AUTHORIZATION: NO-GO

## BLOCKING ISSUES

1. `spec.py:58-112`, `checkpoint.py:46-96`, `host.py:29-89`, `launcher.py:185-192` — Runtime provenance is incomplete. The code verifies the frozen preregistration bundle and checkpoint file hash, but does not recompute every canary-used model/source/environment digest, enforce the clean upstream HEAD, compare the overlay hash to an approved value, pin the constructed host configuration, or compare checkpoint keys to an independently frozen exact 730-key set. Logging HEAD/source hashes is not enforcement. Smallest fix: add a pre-snapshot verifier for every used manifest entry, exact HEAD and reviewed-overlay hashes, canonical sanitized-config hash, environment lock, and sorted key-set digest; fail before CUDA on any mismatch.

2. `launcher.py:143-152,246-249,296-305` — V2-007 accepts an arbitrary absolute child command and treats exit zero plus absence of unexpected files as success. It does not require `canary_metrics.json`, validate its checkpoint step, provenance, zero scientific/robot counters, parity result, or finite metrics. The launcher step can also disagree with the child’s default step. This permits a different model-loading program—or a scientific reader—to run under the canary label and can silently pass without canary evidence. Smallest fix: remove the free-form command surface, construct one exact hash-bound interpreter/module command internally, and require and validate every mandatory output and invariant before success.

3. `host.py:100-146` — The facade does not explicitly move processor tensors to the Qwen model device before invoking a CUDA-resident host. Because upstream code is unavailable locally, there is no evidence that `build_qwenvl_inputs` returns CUDA tensors. The implementation is therefore not fail-closed for device placement. Smallest fix: explicitly move every tensor input to the verified Qwen device, verify batch and `[B,8,2560]` shapes and finiteness, and test the facade against a device-sensitive fake host before the CUDA canary.

4. `launcher.py:44-83`, `engineering_canary.py:38-47,83-87` — Runtime and determinism setup conflicts with the frozen contract. Runtime paths omit the `h1-pgr-audit` subroots and required XDG config, Torch, CUDA-cache, and W&B variables. `CUBLAS_WORKSPACE_CONFIG` and interpreter-start `PYTHONHASHSEED` are absent. CUDA is initialized before deterministic settings are applied. `CUDA_VISIBLE_DEVICES` uses a physical index instead of the verified hardware UUID. Smallest fix: set the exact frozen private roots and deterministic variables before interpreter start, sanitize conflicting inherited variables, expose only the selected UUID, and apply/assert all deterministic flags before the first CUDA operation.

5. `gpu_guard.py:61-106`, `launcher.py:239-244` — GPU exclusivity is not maintained throughout the launch. Malformed compute rows can be ignored, process owners are never attempted, and after post-bind verification there are no heartbeat occupancy checks. A foreign process can join the selected GPU during the canary without invalidating it. The wait loop also has no preregistered hung timeout. Smallest fix: fail on every unexplained compute row, record owners when readable, take and validate snapshots on each heartbeat, reject foreign/cross-GPU bindings, and enforce an exact conservative V2-007 timeout.

6. `launcher.py:95-112,255-290`, `gpu_guard.py:194-207` — Post-exit proof and lock release are unsafe. The launcher releases the reservation even when the post-exit snapshot fails, and it can release after attempting termination without taking a confirming snapshot. Its lingering check intersects NVML PIDs with the current process group, so it can miss a launch PID whose `/proc` entry or PGID changed. `_terminate_owned_group` can signal a reused PGID after the leader exits. The archived lock lacks required release timestamps and parent fsync. Smallest fix: retain the lock unless a confirming snapshot proves every recorded launch PID absent; track PID/start-tick identities, never signal an unverified member or reused group, re-snapshot after termination, and archive an fsynced release record with UTC/monotonic timestamps.

7. `launcher.py:132-140,176-197,274-290` — Evidence, output allowlisting, and accounting are incomplete. The allowlist is checked before `completion.json` exists, requires no exact file set, and is not rerun after completion. The evidence lacks many required ledger fields, including attempt/retry identity, command/config hashes, reservation acquisition/release evidence, post-bind occupancy, timeout, UUID-keyed intervals, stop reason, visibility class, and complete input/output hashes. Files remain replaceable and no terminal manifest seals the directory. Smallest fix: produce one complete canary ledger with explicit non-applicable fields, exclusively create all evidence, hash every input/output, validate the exact final file set including completion, and seal the directory only after verified reservation release.

8. `tests/test_foundation.py:31-330`, `FOUNDATION_TEST_20260807_134338.log` — The 23-test suite does not exercise `spec.py`, `host.py`, `engineering_canary.py`, reservation lifecycle, heartbeat, timeout, termination, post-exit proof, exact output completeness, provenance tampering, or failure propagation. The existing summary therefore cannot support deployment of this launcher. Smallest fix: add the tests below and preserve raw, hash-bound test output from the exact reviewed source.

## NON-BLOCKING ISSUES

- `adapter.py` implements the specified rank-32 adapter with FP32 parameters, population variance, no affine terms, and exact zero-`U` identity.
- `gradient_router.py` correctly derives the common dose from B’s own action-gradient norm, computes and discards B’s valid-future gradient, jointly falls A/C back to action-only, clips after composition, and applies manual FP32 SGD.
- `engineering_canary.py` itself uses deterministic synthetic images/instruction and contains no LIBERO target, outcome, simulator, or robot access. Leakage risk comes from the launcher’s arbitrary command surface.
- Initial two-snapshot reservation ordering and post-bind PID/PGID/UUID comparison are directionally correct but incomplete.
- `robot.py` remains default-deny with no live endpoint or motion surface.

## REQUIRED TESTS BEFORE CANARY

1. Tamper tests for used digests, clean HEAD, overlay hash, sanitized-config hash, environment lock, checkpoint hash, exact key-set digest, and step agreement.
2. Device-sensitive host-facade tests for tensor placement, exact `[B,8,2560]`, finite `[B,8,7]`, autocast, parity, and wrong device/shape failure.
3. Launcher tests proving arbitrary commands/scientific paths are impossible and malformed outputs fail.
4. Snapshot/reservation tests for malformed NVML, races, foreign PID, cross-GPU binding, lease, timeout, post-snapshot failure, lingering children, PID/PGID reuse, and verified release.
5. Failure-injection tests proving nonzero status, preserved evidence, charged elapsed time, and no unverified release.
6. Runtime-environment tests for UUID visibility, private paths, offline settings, interpreter-start seeds, and deterministic flags before CUDA.
7. Numerical-oracle tests for adapter identity and A/B/C routing/nonfinite behavior.
8. Mocked end-to-end lifecycle test producing the exact sealed output set and complete ledger, followed by a fresh hash-bound CPU/static log.

## SCIENTIFIC-SCOPE BOUNDARIES

This review authorizes no execution. It does not authorize the 150-rollout screen, cache construction, C0, fixed-C creation, A/B/C training, P/Q work, Stage 1, Stage 2, scientific target/outcome access, or live robot connectivity/motion. Issues 9/10/11/12/20/22 continue to gate C0/Stage1; 16/17/18 additionally gate Stage2. This is same-family provisional engineering review, not independent scientific acceptance.
