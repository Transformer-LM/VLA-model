# VLA × WAM Research Handoff

这份文档是给下一个 GPT 账号的工作交接入口。快照日期：2026-09-04。

## 1. 研究边界

研究主题经历了 VLA、World Action Model（WAM）、PointMap/几何状态、长时任务记忆、imagined-state repair 和反馈接口可靠性等路线。当前项目配置中的活动研究名是 **Influence-Separated Residual-Alias Compiler（ISRAC）**，但仓库同时保留此前所有主要实验和被终止的路线，不能把“候选 idea”误读成已验证结论。

这是公开 GitHub 仓库中的安全快照。模型权重、数据集、视频、checkpoint、运行缓存、W&B 内容、SSH 信息和真实机器人控制没有上传；本地运行时依赖和第三方 vendor 树也没有上传。对应个人资产仍需在用户自己的机器/服务器中恢复。

## 2. 先读哪些文件

建议按下面顺序建立上下文：

1. `README.md`：仓库范围、隐私处理和环境变量约定。
2. `research/current-policy-repair/`：最近一次 WAM imagined-state repair 实验及审计。
3. `research/active-israc/`：当前 ISRAC idea、文献地图、实验计划和结果摘要。
4. `archive/all-experiments/<run>/`：完整历史实验快照（代码、计划、日志、JSON 结果和审计记录）。
5. 每个 run 中的 `CLAIMS_FROM_RESULTS.md`、`EXPERIMENT_AUDIT*.md`、`findings.md`：这些文件优先于宣传性摘要，决定哪些 claim 可以写进论文。

## 3. 主要实验路线与结论

### A. π0.5 长时任务进度/记忆路线

位置：`archive/all-experiments/pi05-progress-autoresearch/`

问题是长时任务中 progress 被错误写入、遗忘或在失败后继续执行。路线先做 snapshot/restore、progress state 和 assertion carrier 的小实验，再设计 false-progress harm-aware verifier。第一轮明确拒绝把 WAM、视频生成、planner、完整 recovery 和全量 π0.5 微调一次性塞进来。

状态：**RETHINK / PILOT GO**。这条路线提供了任务进度记忆和验证的背景，但当前快照没有证明 WAM 能改善 π0.5 的闭环成功率。

### B. Interaction-Fingerprint Belief（对象身份与物理属性）

位置：`archive/all-experiments/object-belief-autoresearch/`

用 privileged mass/friction oracle 检验物理响应是否能帮助对象 identity association。v5 M1a 的三 seed 结果：shared dynamics `95.5322%`，GT mass/friction oracle `96.1150%`，增益仅 `+0.5828pp`，低于预注册的 `5pp` 门槛；因此 M1b（system-ID vs full-history）没有启动。

状态：**KILL（针对当前 benchmark/operationalization）**。它不支持 RGB object binding、VLA action、长时记忆、recovery 或真实机器人结论。不要在同一数据集上降低门槛重跑。

### C. PointMap / 几何 relation-event verifier

位置：`archive/all-experiments/pointmap-progress-autoresearch/`

E0/G0 v3 比较 addressed RGB、完整 Depth、固定尺寸 object-relative PointMap 和 simulator-pose Oracle。360 个受控 LIBERO 样本、五个 task family 的摘要结果：PointMap macro-F1 `0.9002`，完整 Depth `0.6487`；PointMap 输入张量 `152` bytes，Depth `442,368` bytes。

状态：**只支持受控 E0 表征 headroom**。它没有验证 action-conditioned counterfactual dynamics、WAM 必要性、π0.5 改善、恢复、闭环或 sim-to-real。E1/B2 只有在重新固定阈值、训练协议和审计后才有条件授权。PointMap 不能被表述成普遍替代 Depth。

### D. 类内功能几何 VLA × WAM

位置：`archive/all-experiments/functional-geometry-vla-wam/`，相关 prior-art 检查在 `archive/all-experiments/scoop_functional_geometry/`。

核心问题是同一高层技能面对不同目标物—参照物几何配对时，抓取、对准、接近和放置 HOW 是否改变，而不是只平移目标坐标。已有 GIFT、FMB、RPDiff 等非 VLA 工作构成强邻域证据，因此实验计划要求先做 Oracle gap、终点位姿排除和 PointMap WAM 必要性测试。

状态：目前是**实验计划/可行性路线**，仓库快照没有完成的主结果；不要把计划当成已验证创新。

### E. WAM imagined-state repair（最近一次实际下游实验）

位置：

- 代码：`experiments/policy-relevant-imagined-state-repair/`
- 文档：`research/current-policy-repair/`
- 完整历史记录：`archive/all-experiments/ideaspark_run/policy-relevant-imagined-state-repair/`

冻结 StarVLA，给它当前观测或 action-conditioned WAM imagined frame，测试 imagined state 是否会改变下一次动作以及是否造成下游伤害。500-step FastWAM 只是弱 probe，最终帧 PSNR 约 `9.5–10.0`。

扩展到 18 个场景后：baseline 成功 `15/18`，raw-WAM `12/18`，anchored image blend `13/18`；观察到 3 个 baseline-success/raw-failure pair，anchored repair 只救回 1 个。它稳定证明了“WAM imagined state 可以改变冻结 VLA 的后续决策，并可能造成失败”，但没有证明 learned physical hallucination detector、几何 repair 或整体 success-rate 提升。

状态：**因果下游敏感性和伤害信号通过；最终 repair 方法未验证**。继续调普通像素混合没有信息价值；下一步应使用独立的 object/end-effector relative geometry 或 PointMap witness，并与 direct replan 比较 action regret 和 harmful intervention rate。

### F. ISRAC：Influence-Separated Residual-Alias Compiler（当前活动路线）

位置：`archive/all-experiments/ideaspark_run/influence-separated-residual-alias-compiler/`，精选入口在 `research/active-israc/`。

目标不是把任意残差跨动作搬运，而是自动构造两个 feedback-interface-preserving、物理机制不同的 alias world，使已执行动作的反馈接口保持一致、但未执行候选动作的真实物理效果或 residual/ranking 发生分离。然后用它检验反馈式 WAM 修正器的 correction harm，以及为 influence-separated residual transport/router 提供反例。

重要里程碑：

- P026 simple-baseline compiler gate 的 point-yield 比 strongest simple baseline 高于预注册门槛，且 paired bootstrap lower bounds 通过；但结果是 amended confirmatory，含已披露的 pre-formal contamination，所以只能叫 compiler comparison，不是干净的最终论文结果。
- P027C 的 calibrated global transport held-out E0 通过校准门，但 `candidate action ranking` 和 `learned router` claim 均未支持；普通 alias descriptive pattern 不能替代下游 WAM/VLA 结果。
- P027-A（强黑箱 optimizer falsifier）、P027-B（第二物理机制）和 P027-C（至少两个 held-out feedback interfaces 的 harm）是升级为 WAM correction claim 的前置门槛。
- 当前文档明确禁止把 simulator compiler 结果写成真实安全保证，也禁止把单一 WAM checkpoint 的 pixel/latent 分数当成两个独立模型。

状态：**ISRAC 的 simulator/compiler 证据部分已推进，但 WAM correction、router 和 VLA 闭环 claim 仍未通过**。继续工作时先读 `P027_CONDITIONAL_NEXT_GATE.md` 和 `refine-logs/EXPERIMENT_TRACKER.md`，按 gate 执行，不要跳过前置审计。

### G. ideaspark / novelty 运行记录

位置：`archive/all-experiments/ideaspark_run/` 和 `archive/all-experiments/novelty7_autoresearch/`。

这些目录包含母方向探索、候选 Idea、novelty/scoop 检查、review trace、失败尝试和中止原因。它们是研究 provenance，不等于实验验证。优先使用其中的 `IDEA_REPORT.md`、`NOVELTY_REPORT.md`、`TERMINAL_DECISION.md`、`CLAIMS_FROM_RESULTS*` 和 `EXPERIMENT_AUDIT*`。

## 4. 目录对照

| 目录 | 内容 |
|---|---|
| `skills/embodied-autoresearch/` | 当前自动科研 skill 的完整公开安全副本 |
| `skills/all-local-skills/` | 其他本地 research skills 的源码和说明（不含运行时依赖） |
| `experiments/policy-relevant-imagined-state-repair/` | 已整理、路径参数化的近期实验代码 |
| `research/current-policy-repair/` | imagined-state repair 的状态、结果、审计和下一步 |
| `research/active-israc/` | ISRAC 精选研究文档 |
| `archive/all-experiments/` | 所有主要历史 run 的源码/文档/JSON 结果快照 |
| `archive/project-context/` | 顶层 brief、配置、manifest 和旧账号交接材料 |
| `archive/orchestration-redacted/` | autoresearch 状态、候选、claims、研究 trace、工具和历史备份（已脱敏） |

## 5. 复现实验时必须知道的事

- 公开仓库没有数据和权重。代码若需要个人资产，应把环境变量 `VLA_WAM_PERSONAL_ROOT` 指向用户自己的研究根目录，再检查脚本中的数据/模型相对路径。
- `skills/all-local-skills/` 是可公开的 skill 源文件；本机 Python 运行时、第三方依赖和二进制库没有复制进仓库。
- 服务器没有外网，不能在服务器上临时下载依赖或模型；优先使用已有个人环境和资产。
- 任何运行产物、缓存、checkpoint、日志和视频都应放在个人目录，不要写团队/共享目录。
- 启动 GPU 前必须即时检查显存、利用率和 compute process；优先 2、3 号卡，只有四卡都立即空闲时才使用 0、1。不要抢占其他用户进程。
- 不自动发起真实机器人运动；当前公开快照只涉及离线/仿真研究。
- 先运行最小 sanity，再进入主实验；先读审计和 claim 文件，再决定是否可以扩展。

## 6. 给下一 GPT 的工作规则

1. 不要把计划、候选 Idea、初步结果和已证实 claim 混在一起。
2. 任何新结果都必须保留原始 JSON、配置 hash、数据 provenance、停止条件和独立审计记录。
3. 不能用更大的输入、更多参数、更多 token、更多候选或额外数据掩盖方法贡献；需要 matched controls。
4. 如果一个 gate 失败，记录 kill/pivot，而不是事后降低阈值。
5. 对 WAM imagined state 的结论必须区分：改变 VLA 动作、造成下游伤害、检测物理幻觉、修复动作、提升闭环成功率。这些是不同 claim。

补充：`archive/` 中个别早期自动科研 JSON 是原始 provenance 输出，源工作区本身就存在截断字符串或非严格 JSON；它们用于保留历史，不应直接当作可运行配置。若 JSON 与对应 Markdown 审计/结果摘要冲突，以原始实验审计和 claim 文件为准。
