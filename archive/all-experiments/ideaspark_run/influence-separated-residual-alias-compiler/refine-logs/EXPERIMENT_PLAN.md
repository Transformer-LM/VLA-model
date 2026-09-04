# 实验计划：Influence-Separated Residual-Alias Compiler（ISRAC）

**问题**：反馈式 WAM 根据一个已执行动作暴露的预测误差，去修正另一个尚未执行的候选动作；但单个 factual residual 可能无法识别跨动作的误差响应，导致“修正”反而颠倒真实动作排序。

**方法主张**：ISRAC 自动搜索两个合法物理世界，使已执行动作的完整反馈接口完全相同，但一个由冻结策略提出的未执行候选动作在两个世界中产生相反的物理效果或 residual/ranking；每个样本附带机器可验的物理与同一性证书。

**日期**：2026-08-31

## Claim Map

| Claim | 为什么重要 | 最低可信证据 | 关联实验块 |
|---|---|---|---|
| C1（主）ISRAC 能自动、跨任务地编译非 action-indexed、物理自然的 feedback-interface-preserving residual-alias twins | 这是相对 Capability Separation、Joint MDPs 和普通 metamorphic testing 的唯一可守新颖点 | 两个模拟器、至少两个物理机制族；相对 random/grid/CMA-ES 在同等 simulator calls 下显著提高合格 pair 产率；所有 pair 通过逐帧同一性与首次物理分歧证书 | B0、B1、B3 |
| C2（辅）这些 twins 能暴露现有反馈 WAM 修正器的 correction harm，而且不是针对某一方法过拟合 | 证明编译器生成的是有控制意义的反例，而非漂亮但无关的 simulator artifact | pair 编译过程不读取目标 WAM ranking；在未参与编译的 FWM/FBFM/ReDRAW 类方法上，false transport、ranking inversion 和 regret 显著高于普通扰动集 | B2、B4 |

**必须排除的反解释**：结果来自手工 `if action==a1`、scripted failure、渲染非确定性、低支持动作、直接把目标 WAM ranking 放进搜索目标、或单一任务的参数碰巧。

## 论文证据主线

- 主文必须证明：自动 compiler 的合法 alias 产率；证书确实成立；这些样本对反馈 WAM 有独特的 correction-harm 诊断价值。
- 附录支持：更多任务、参数范围、证书可视化、真实机器人可迁移性探索。
- 明确不主张：two-point lower bound 本身新颖；ISRAC 能修复 WAM；alias twin 覆盖所有真实分布外错误；模拟证书等价于真实安全保证。
- 暂时删去：从头训练新 WAM、大规模 RGB 生成质量比较、触觉、长期 RL post-training。

## 实验块

### B0：确定性、接口同一性与证书单元测试

- **Claim tested**：证书测到的同一性与分歧不是复跑噪声或日志假象。
- **Why**：若 factual transcript 不是同一个输入，整个不可识别性论证失效。
- **Dataset / task**：LIBERO/robosuite-MuJoCo 1 个 pick-place 或 contact-rich task；RoboTwin/SAPIEN 1 个对应任务；每任务 20 个可恢复 snapshot。
- **Compared systems**：相同参数重复回放；单个合法物理参数微扰；action-indexed fake switch（仅作应被拒绝的阳性控制）。
- **Metrics**：simulator state hash；逐帧 RGB/depth 最大差与 LPIPS；proprio 最大差；factual WAM residual 差；首次状态分歧帧；接触事件帧；证书拒绝原因。
- **Setup**：先不用目标 WAM 训练；固定随机种子、渲染器、控制频率与 checkpoint 恢复顺序。噪声阈值由 30 次同参数复跑的最大值确定，不人为指定宽阈值。
- **Success criterion**：同参数复跑 100% 通过；action-indexed/scripted 控制 100% 被拒绝；合格 twin 的 factual RGB/depth/proprio/residual 差不超过各自复跑噪声上界。
- **Failure interpretation**：checkpoint 恢复或渲染非确定，无法形成可信 benchmark，立即停止。
- **Table / figure**：主文 Table 1（证书定义与噪声上界）；Figure 2（同一 factual、分叉 candidate）。
- **Priority**：MUST-RUN。

### B1：自动 alias compiler 的产率与效率

- **Claim tested**：influence separation 是编译器的实质贡献，不是普通 fuzzing。
- **Why**：严格评审认为这决定 novelty 是 7.3 还是退化到约 6.4。
- **Compiler**：
  1. 从冻结策略 top-K chunk 中选 factual `a0` 和 alternative `a1`；
  2. 建立对象—表面—关节物理参数块与 contact/event activation trace；
  3. 用有限差分或 simulator 依赖图筛出对 `a0` 完整 transcript 影响低于噪声、但会被 `a1` 激活的参数块；
  4. 在物理合法范围内求解 `theta+ / theta-`，只最大化 `a1` 的真实任务效果分离，并硬约束 `a0` transcript 同一；
  5. post-hoc 检查 residual sign/ranking inversion；目标 WAM ranking 不得进入优化目标。
- **Baselines**：随机 domain randomization + rejection；等预算网格/CMA-ES constrained fuzzing；去掉 influence-zero 筛选的 ISRAC。
- **Metrics**：每 1,000 simulator rollouts 的合格 pair 数；合法 pair 成功率；calls/pair；wall time；跨 snapshot/task/机制覆盖；首次分歧与 contact activation 同帧比例；人工调参次数（必须为 0）。
- **Setup**：两个模拟器各 1 个任务，20 snapshots，top-8 chunks；至少摩擦/接触面与负载/遮挡状态两个机制族；3 个 compiler seeds。
- **Success criterion（48h E0 gate）**：每个平台至少两个机制族、每族自动得到 ≥4 对合格 twins；ISRAC 的合法 pair 产率至少为最佳同预算 baseline 的 2 倍；≥90% pair 的首次分歧与记录的真实物理激活同帧；无逐实例手调。
- **Failure interpretation**：任一平台无合格 pair、只能用 action-indexed/scripted 修改、或去掉目标 WAM ranking 后 pair 消失，kill 本 Idea。
- **Table / figure**：主文 Table 2（产率/效率）；Figure 3（参数影响图与约束求解）。
- **Priority**：MUST-RUN。

### B2：反馈 WAM correction-harm 评测

- **Claim tested**：alias twins 暴露的是现有反馈修正器的真实跨动作错误迁移。
- **Why**：把 compiler 从 simulator fuzzing 提升为 WAM/VLA 研究工具。
- **Compared systems**：无修正 WAM；FWM；FBFM；ReDRAW-style point residual；若代码不可得，先实现论文接口等价的最小复现并明确标注。
- **Metrics**：false-transfer rate；corrected-vs-uncorrected top-1 rollback regret；pairwise ranking accuracy；correction-harm rate（原本正确、修正后错误）；task success；future feature error仅作次指标。
- **Setup**：compiler 不访问任何待评方法的 score/ranking；同一 candidate bundle、同一 rollback ground truth；配对 bootstrap 95% CI；3 seeds。
- **Success criterion**：至少两种未参与编译的反馈方法在 alias set 上 correction-harm 显著高于普通物理扰动集，且 uncorrected WAM 不呈现同等幅度的人为退化。
- **Failure interpretation**：若只对一个被针对的方法有效，则是方法特定 adversarial test，不足支撑 C2。
- **Table / figure**：主文 Table 3（反馈方法 harm）；Figure 4（同 residual、相反正确修正方向）。
- **Priority**：MUST-RUN，须在 B1 通过后启动 GPU。

### B3：新颖性隔离与反作弊控制

- **Claim tested**：收益来自 influence-separated physical activation，而非更大的搜索预算或宽松证书。
- **Controls**：去掉 influence-zero；用目标 WAM ranking 参与优化（应报告为过拟合上界而非方法）；允许 action-indexed switch（应被证书拒绝）；appearance-only nuisance；低支持 candidate；放宽 transcript 阈值；只保留单 simulator。
- **Metrics**：合法 pair 产率、跨方法 transfer、证书违规率、correction-harm。
- **Success criterion**：完整 ISRAC 在相同 calls 下优于 random/CMA-ES；ranking-aware overfit 版本在 held-out WAM 上明显下降；宽松阈值只提高伪 pair 而不提高 certified pair。
- **Failure interpretation**：若普通 CMA-ES + rejection 等效，compiler 没有方法贡献。
- **Table / figure**：主文 Table 4（删除实验）；其余放附录。
- **Priority**：MUST-RUN。

### B4：跨任务/跨引擎与真实机器人可迁移性

- **Claim tested**：compiler 不是单任务工程脚本。
- **Setup**：扩至每引擎 ≥4 个任务、≥3 个机制族；真实机器人仅做少量安全、预先界定参数的 replay 验证，不宣称安全保证。
- **Metrics**：新任务 zero-manual-edit yield；证书通过率；未参与编译 WAM 的 harm transfer；真实/模拟 effect direction 一致率。
- **Success criterion**：同一 compiler schema 在两个引擎与多数新任务中无需任务专用代码即可产出 pair。
- **Failure interpretation**：需每任务重写参数语义则降为 benchmark engineering。
- **Table / figure**：附录主表；真实机器人 qualitative figure。
- **Priority**：NICE-TO-HAVE，E0 不做。

## Run Order and Milestones

| Milestone | Goal | Runs | Decision Gate | Cost | 风险 |
|---|---|---|---|---|---|
| M0 | 恢复 simulator checkpoint、确定复跑噪声、验证证书 | R001–R004 | 两平台 deterministic replay 通过；fake switch 被拒绝 | CPU 4–8h，无 GPU | 渲染/物理非确定性 |
| M1 | 48h compiler E0 | R005–R012 | 每平台两机制族各 ≥4 对；产率 ≥2×最佳 baseline | CPU 24–48h；必要时少量单卡策略采样 | 非光滑接触优化、参数语义不统一 |
| M2 | 冻结 π0.5/WAM 基线与 feedback 方法 | R013–R018 | 无修正 baseline 与至少两种反馈方法可复现 | GPU 0–24h，按代码可得性 | 论文代码/权重不可得、服务器无外网 |
| M3 | 核心 correction-harm 评测 | R019–R030 | ≥2种 held-out 方法出现可重复 harm；普通扰动负对照不等效 | 4×A100 约 24–72 GPUh | WAM 推理成本、候选 bundle 方差 |
| M4 | 删除实验与扩展 | R031+ | C1/C2 均被支持后才继续 | 视结果决定 | scope creep |

## Compute and Data Budget

- **E0**：以 simulator CPU 为主；先用缓存/固定 candidate chunks，避免在 premise 未通过前消耗 GPU。
- **通过 E0 后**：冻结 π0.5 与 WAM，只做候选采样、rollout 和反馈基线推理；四张 A100 可并行按 snapshot 或方法切分。
- **GPU 规则**：启动前逐卡确认显存 <500 MiB、利用率 ≤5%、无 compute process；默认 GPU 2/3，只有四卡全部空闲时使用 0–3；不抢占、不共卡。
- **数据**：全部位于 `<PERSONAL_RESEARCH_ROOT>`；不得写入团队/共享目录。
- **外网**：服务器无外网；代码、权重与依赖必须从本地已有安装或经本机安全传输。
- **最大瓶颈**：跨 MuJoCo/SAPIEN 的物理参数块抽象与 deterministic certificate，而不是 GPU 算力。

## 风险与缓解

- **风险：compiler 偷看目标 WAM ranking。** 缓解：ranking 永不进入优化目标；只在冻结 pair 后 post-hoc 评估，并做 held-out WAM transfer。
- **风险：所谓 twin 来自 renderer noise。** 缓解：阈值绑定同参数复跑最大噪声；保存逐帧 hash 与首次分歧证书。
- **风险：物理参数是隐藏脚本开关。** 缓解：只允许具备 simulator 原生物理语义的参数块；拒绝 action-indexed 条件逻辑。
- **风险：top-K 动作不真正可执行。** 缓解：候选必须来自冻结策略且通过 IK/workspace/control-limit 检查；报告 eligibility coverage。
- **风险：随机 fuzzing 已足够。** 缓解：matched simulator-call 预算比较；compiler 的新颖性以合法 pair yield 与跨方法 transfer 为准。
- **风险：现有反馈方法难以完整复现。** 缓解：先完成与方法无关的 C1；B2 使用官方实现优先，接口等价复现必须单列而不冒充官方结果。

## Final Checklist

- [x] 主张不超过两个
- [x] novelty 由 compiler 产率与删除实验直接隔离
- [x] 标准 lower bound 不计作创新
- [x] E0 有硬停止条件
- [x] GPU 仅在 compiler premise 通过后使用
- [x] 不使用触觉
- [x] 所有远端数据限定在个人目录
- [ ] 两平台 deterministic replay 已通过
- [ ] 自动 compiler E0 已通过
- [ ] correction-harm 在 held-out 方法上成立
