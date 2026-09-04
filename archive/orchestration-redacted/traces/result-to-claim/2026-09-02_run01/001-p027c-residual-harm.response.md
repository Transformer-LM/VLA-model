claim_supported: no

what_results_support:

- 数值证据存在性为 7/7 verified，但这只证明数值可追溯。
- 训练侧网格校准在 6 个 source、406 个 ordinary-overlap endpoints 上将 source-balanced objective 从 1.3737103 降至 1.2784379，改善 6.9354%，选择 `alpha=0.7, decay=0.95`。
- 该校准修正在 heldout source 的 boundary 1/2/9 上均使 alias 与 ordinary controls 的 normalized endpoint error 变差，说明当前主要问题是 residual transport 未跨 source/boundary 泛化。
- `alias-minus-control` normalized delta 分别为 `-0.00052568/-0.00117045/-0.00078231`，alias 在三个 boundary 上数值上均未表现出更强伤害。
- masked raw-state RMSE 也无一致 alias 特异方向；residual magnitude 的差异同样未与 alias excess harm 对齐。

what_results_dont_support:

- 不支持 candidate-only influence alias 相对 ordinary-overlap controls 造成更强错误残差迁移。
- 不支持 calibrated residual correction 能改善 heldout ordinary-overlap controls；三个 exact-boundary gate 全部失败。
- 不支持将训练侧 6.9354% 改善解释为 heldout alias claim。
- 不支持 influence separation 是当前失败的关键解决因素：连 oracle-defined ordinary-overlap transport 在 heldout 上也总体有害。
- 不支持 learned router、candidate ranking 或 VLA closed-loop 改进；这些实验均未运行。

missing_evidence:

- 多个真正独立 heldout sources/seeds 上 ordinary-overlap correction 必须先稳定优于 no-correction。
- 预注册直接效应 `delta_alias - delta_ordinary`、非零实际意义阈值及成功门槛。
- block-first/address-clustered/source-level 推断，并将 calibration 与 WAM training source 解耦。

suggested_claim_revision:

在一次单 seed、单个 training-heldout 但 retrospective 的 simulation-only E0 中，训练侧校准找到可降低同源 ordinary-overlap objective 的 residual-transport 参数；但该参数在 heldout source 的三个 exact boundaries 上对 alias 与 ordinary controls 造成近乎相同的 normalized endpoint-error 增加。因此当前结果表明 transport 泛化失败，未提供 alias-specific excess migration 证据，也不授权进入 learned router、candidate ranking 或 VLA closed loop。

next_experiments_needed:

- 必须先 pivot 到 residual-transport validity：nested leave-source-out 或独立 validation/test，多 source、多 seed 验证 ordinary-overlap correction 的 heldout 改善；若仍失败，终止当前 correction 形式。
- 仅在 validity gate 通过后运行 exact-boundary alias-vs-control direct contrast。
- 仅在 alias excess-harm gate 通过后训练 router、ranking 和 closed loop。
- 不应在当前旧 heldout source 上事后重调超参数、挑 boundary/指标、使用 pair 伪重复或直接训练 router。

routing_action: pivot

confidence: high

review_independence: same-family

acceptance_status: provisional
