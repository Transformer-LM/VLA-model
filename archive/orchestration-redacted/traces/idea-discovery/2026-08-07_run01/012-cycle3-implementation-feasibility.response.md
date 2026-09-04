# Cycle-3 read-only implementation feasibility audit

## Verdict

**CONDITIONAL GO.** Isolated implementation and a measured pilot may start. The full staged rollout is allowed only after cache parity, hot-switch parity, and the 20-rollout timing gate pass.

## Exact host integration

- Clean StarVLA HEAD: `3422b9f2387b6f682cf02802904a77b23ab13afd`.
- In `QwenOFT.py`, insert the adapter after `_gather_action_token_embeddings` and before `action_model.predict_action`: around lines 197–200 in training and 269–273 in prediction.
- Action-token representation shape is `[B,8,2560]`.
- `MLP_ActionHeader.py::predict_action` reshapes this directly to `[B×8,2560]`; a shape-preserving identity low-rank adapter is compatible.
- Freezing the action-head parameters does not block gradients from its output back into the adapter.

## Cache equivalence requirements

- Qwen must be fully frozen in `eval()` mode.
- Prompt, dual-view preprocessing, eight action tokens, and token-gather order must exactly match online inference.
- A fresh cache must pass direct-forward versus cached-hidden-to-action-head numerical parity.
- A/B/C must use one immutable cache and identical minibatch order.

## Future frames and DINO

- LeRobot supports arbitrary `delta_indices`, but current `_pack_sample()` reads only `data[video_key][0]` and therefore drops `t+8`.
- The isolated cache script must call `get_step_data()` and explicitly obtain `t` and `t+8`.
- Exclude samples whose `t+8` crosses the episode boundary. Never accept last-frame clip padding, which would create false persistence targets.
- Split train/validation by episode; C derangement must also be cross-episode and use non-overlapping future windows.
- Personal offline DINOv2 weights: `<PERSONAL_RESEARCH_ROOT>/checkpoints/dinov2/dinov2_vits14_pretrain/dinov2_vits14_pretrain.pth`.
- Personal official source: `<PERSONAL_RESEARCH_ROOT>/workspace/third_party/dinov2-main/dinov2-main`.
- The StarVLA wrapper first attempts the network; offline use must instantiate from local source with `pretrained=False` and then strictly load the personal checkpoint.

## Isolated implementation layout

Do not modify the dirty CF-DynAlign tree. In a clean isolated personal worktree/extension add:

- `h1/cache_features.py`
- `h1/models.py`
- `h1/train_paired.py`
- `h1/build_predictive_subspace.py`
- `h1/policy_wrapper_h1.py`
- `h1/eval_libero_h1.py`

`baseframework.from_pretrained()` is strict and will reject an added adapter. Strictly load the vanilla baseline first, then strictly load the small adapter/head/subspace artifact. The native trainer uses only `action_loss`, so use an isolated paired trainer.

Train A/B/C lockstep inside one process per seed rather than as fifteen independent jobs; this gives identical batches and lets C match A's adapter auxiliary-gradient norm batchwise. Keep a single frozen base model resident and hot-switch small adapters/interventions; do not reload a 9.78 GB checkpoint per condition. The evaluator must expose exact `task_ids`, `init_indices`, `adapter_id`, and `intervention`, and disable video encoding by default.

For a full A-to-B replacement, invoke paired A/B adapters and verify numerical reproduction of B's action as a positive-control gate.

## Storage and measured budget

- Two candidate LIBERO-10 tasks contain about 71 demonstrations / 20k frames.
- BF16 `[8,2560]` hidden cache is roughly 0.8 GiB; target/action/manifest included should remain below 1.2 GiB.
- Adapter, heads, and subspaces together should stay below 0.1 GiB.
- Personal disk has about 2.6 TiB free. Save only incremental artifacts, never a complete 9.78 GB base checkpoint per arm.
- Existing baseline logs identify two relatively fast, not fully saturated tasks at about 0.94 and 0.90 success, with about 40.98 and 31.92 seconds per rollout.
- Five hundred rollouts project to about 5.06 GPUh.
- Fresh cache, head pretraining, and five lockstep three-arm 500-step trainings project to about 0.5–1.2 GPUh.
- Total is roughly 5.6–6.3 GPUh, but longer failure trajectories can approach or exceed 8 GPUh.
- A slower task at about 0.86 success and 87.5 seconds/rollout is unsuitable under this budget.

## Hard gates

1. cache parity passes;
2. valid `t+8` indexing and episode-split audit pass;
3. adapter hot-switch and A-to-B replacement pass;
4. a 20-rollout calibration on GPUs 2/3 is charged to the cap;
5. projected cumulative use must remain at most 7.2 GPUh;
6. GPU 2/3 availability is rechecked immediately before every launch; GPU 0/1 may be used only if all four physical GPUs are proven idle.

The audit was read-only and launched no process or GPU work.
