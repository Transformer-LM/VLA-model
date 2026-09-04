# PGR-Audit v2.1 协议歧义审计

**审计时间**：2026-08-07 13:43:38 +08:00  
**审计性质**：新鲜上下文、只读、same-family provisional  
**冻结清单 SHA256**：`21267bf7a0b34d1f101398963011697ea451a6a4a5869dd97317319bd637ea6f`  
**009 jury 响应 SHA256**：`4c5778ca4fd2d2f5f76c121e4d2566474ac961c73f3da718bda55af870905431`

## 范围结论

- A（个人隔离基础实现）可以继续。
- B（纯工程 canary）在 CPU/static 测试、fresh code review、输入摘要/键白名单复核和 launch guard 通过后可以继续；不得读取科学目标或结果。
- 最早可进入的科学范围是 C：150 条 treatment-blind checkpoint screen；它必须等待 A/B 通过。
- C0、A/B/C adapter 训练和 Stage 1 在问题 9、10、11、12、20、22 被明确冻结、重哈希并重新 jury 前不得开始。
- Stage 2 还必须额外解决问题 16、17、18并重新 jury。
- 真实机器人 live connectivity/motion 仍未授权；仿真结果不是它的前置条件，但精确机器人合同与单独安全/科学 jury 是前置条件。

分类统计：3 `ALREADY-DEFINED`、6 `UNIQUE-ENGINEERING-INTERPRETATION-NO-SCIENTIFIC-DEGREE`、3 `NONBLOCKING-AUDITABILITY-GAP`、6 `BLOCKS-D-STAGE1`、3 `BLOCKS-D-STAGE2`、1 `BLOCKS-F-ROBOT-ONLY`。

## 逐项裁定

| # | 分类 | 裁定与最小动作 |
|---:|---|---|
| 1 | NONBLOCKING-AUDITABILITY-GAP | 冻结 JSON 中的 pending 状态由外部、哈希绑定的 009 `CONDITIONAL-GO` 覆盖。建立不可修改 bundle 之外的 jury receipt sidecar，不改冻结输入。 |
| 2 | UNIQUE-ENGINEERING-INTERPRETATION-NO-SCIENTIFIC-DEGREE | 目录只遍历真实目录节点；仅规则指定的 regular files 进入记录；按 POSIX 相对路径 Unicode code-point 排序；DINO/LIBERO 仅排除精确 `.git`/`__pycache__` path components；symlink/special file fail closed。补 Unicode/子目录/链接/特殊文件 conformance test。 |
| 3 | ALREADY-DEFINED | Freeze manifest 精确枚举八个文件，文件和 manifest 均按 raw-byte SHA256 验证。 |
| 4 | UNIQUE-ENGINEERING-INTERPRETATION-NO-SCIENTIFIC-DEGREE | `selected_checkpoint.json` 与 `primary_task_set.json` 必须作为一个 transaction directory 或一个绑定双哈希的 commit record 原子发布；单文件状态不授权 progression。 |
| 5 | NONBLOCKING-AUDITABILITY-GAP | 150 条 screen 不完整时产生 terminal-invalid、audit-only manifest；不得生成 selector，不得进入 C0/D。 |
| 6 | NONBLOCKING-AUDITABILITY-GAP | 绑定 selector/revealer/auditor executable hashes，记录读取，scientific workers 禁止 reveal path；在 B/code review 检查。 |
| 7 | ALREADY-DEFINED | 普通文件 raw-byte hash，语义 JSON canonical hash，目录 bundle 使用目录规则；每个 artifact 记录 kind，未知 kind fail closed。 |
| 8 | UNIQUE-ENGINEERING-INTERPRETATION-NO-SCIENTIFIC-DEGREE | reveal 前只允许一个无 arm/condition 标签的 logical-job-wide `nonfinite_any` OR；禁止任何 per-arm nonfinite。 |
| 9 | BLOCKS-D-STAGE1 | C0 action-norm tercile cutpoints 的来源未固定。冻结为已定义的 D_adapter、per-dataset-task、`inverted_cdf` cutpoints 并形成哈希 artifact；C0 前重新 jury。 |
| 10 | BLOCKS-D-STAGE1 | strongest-control 的七个候选虽可推断，但 nuisance ridge、current-DINO z-score、progress decile、intercept、alpha tie/refit 规则不闭合。全部明确后重新 jury。 |
| 11 | BLOCKS-D-STAGE1 | matching 的 row/column/stratum/order 与 whole-assignment tie 不闭合。冻结 `(dataset_task_index, episode_index, t)` 排序和完整 secondary rule 或 nonunique fail guard 后重新 jury。 |
| 12 | BLOCKS-D-STAGE1 | fixed-C 的 target artifact 及 eligible-pair moment population 未固定。明确 nuisance-residual target、global/level/stratum population 与 scale 计算后重新 jury。 |
| 13 | UNIQUE-ENGINEERING-INTERPRETATION-NO-SCIENTIFIC-DEGREE | whitening 的科学 artifact 保存最终 symmetric whitening matrix；不以 raw eigensystem 为 artifact，避开符号/重根基旋转歧义。 |
| 14 | UNIQUE-ENGINEERING-INTERPRETATION-NO-SCIENTIFIC-DEGREE | nuisance crossfit 分别保存 `alpha_delta` 与 `alpha_target`，不得隐式复用。 |
| 15 | ALREADY-DEFINED | `B_N` basis 必须为 `d × k`、列正交；样本按 `n × d` 存储时用 right singular vectors 的等价实现。 |
| 16 | BLOCKS-D-STAGE2 | 冻结 P ridge 的精确矩阵方程、penalty scaling、solver、centering/intercept、prediction formula；沿用既有 fold0–1 fit-target mean 作为 R² reference；重新 jury。 |
| 17 | BLOCKS-D-STAGE2 | 1000 次 within-task episode-block target permutation 遇到不等长 episode 的对齐/缺失行规则未固定。明确唯一算法后重新 jury。 |
| 18 | BLOCKS-D-STAGE2 | Q 的 fold3 readout、intercept、alpha 身份及 fold3/fold4 reuse 未固定。明确后重新 jury。 |
| 19 | UNIQUE-ENGINEERING-INTERPRETATION-NO-SCIENTIFIC-DEGREE | fold4 bootstrap 只重采样 scoring episodes；fold0–1 readout 固定且不在 replicate 内重拟合。 |
| 20 | BLOCKS-D-STAGE1 | role-derived RNG literal registry 与 exact byte serialization 不完整，尤其 Stage-1 LCB/bootstrap。建立穷尽 registry 后重新 jury。 |
| 21 | BLOCKS-F-ROBOT-ONLY | 机器人合同必须使用 protocol 指定的 randomized complete blocks，不采用 plan 中的 Latin-square 备选；未来 robot-specific bundle 修正并单独 jury。 |
| 22 | BLOCKS-D-STAGE1 | action-token cache 的 producer/storage/load/compute dtype、compression 与 representation-level round trip 未固定。优先冻结 exact upstream BF16 bits 保存、显式 FP32 adapter cast、representation 与 action 双 parity；重新 jury。 |

## 当前执行边界

本审计不改变已冻结 v2.1 bundle。A/B 可以继续；C screen 只能在 A/B 通过后执行。任何 C0、cache 科学构建、A/B/C 训练、Stage 1/2 或 live robot 工作都必须遵守上述新 gate。歧义的解决将形成新的协议版本与新的 hash-bound jury，不回写历史文件。
