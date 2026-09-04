# Round 1 Refinement

## Problem Anchor

- **Bottom-line problem**：反馈式 WAM 会利用一次已执行动作的预测残差，去修正、排序或拒绝另一个尚未执行的候选动作；但同一段 factual 反馈并不一定能识别不同候选动作所需的物理修正方向。我们需要自动构造可审计的具身反例，判断这种跨动作残差迁移何时在信息上不充分、何时会伤害 VLA 的动作选择。
- **Must-solve bottleneck**：现有 WAM 纠错与 VLA 测试缺少一种同时满足以下条件的反例生成器：factual 动态转录在两个合法物理世界中相同；候选动作由冻结策略真实提出；候选动作的物理结果发生可定位分叉；编译过程不读取被测 WAM 的 score；每个样本附带机器可验的 equality–activation–first-divergence 证书。
- **Non-goals**：不训练新的 RGB/Depth/PointMap WAM；不提出新的 VLA action head；不把一般 world-model exploitation、一般 metamorphic testing 或 two-point 不可辨识性定理包装成新贡献；当前不启动真实机器人；不使用触觉。
- **Constraints**：远端无外网；所有资产与结果仅位于 `<PERSONAL_RESEARCH_ROOT>`；冻结现有 StarVLA/π0.5 类策略；第一阶段以 LIBERO/robosuite rollback 为主；仅在编译器门槛通过后使用空闲 A100 做 WAM 审计；所有搜索与证书必须报告完整失败样本和 simulator-call 预算。
- **Success condition**：在相同 simulator calls、相同物理参数范围和相同证书下，ISRAC 相对最强 random/grid/CMA-ES/BO 类搜索至少获得稳健的 2× certified-pair yield，并跨多个任务、至少两个物理机制族复现；随后这些冻结并哈希的 pairs 在至少两个未参与编译的反馈 WAM 接口上显著提高 correction-harm 或 ranking-regret，相对普通强度匹配扰动具有特异性。

## Anchor Check

- **Original bottleneck**：同一 factual residual 对未来不同 candidate 的正确修正方向不可辨识。
- **Preserved**：修订仍然只生成并审计这类反馈接口的物理 twin，没有转成新 WAM 或一般 VLA benchmark。
- **Rejected drift**：不靠增加第二个 WAM head、LLM searcher、RL 或更多 benchmark 来掩盖核心搜索原语尚未成立；若 compiler gate 失败，允许降级/淘汰，不能把 WAM harm 改写成同一方法主张。

## Simplicity Check

- **Dominant contribution**：动作条件接触依赖集合相减，是一个 target-WAM-blind 的参数块预筛原语。
- **Removed/merged**：删除“finite difference 或 dependency graph 或 solver 任择”的模糊描述；第一版只覆盖接触介导的 surface compliance/friction；主方法固定端点 sweep。
- **Rejected complexity**：不训练 influence predictor，不添加 learned critic，不把 Depth/PointMap 并入当前论文。
- **Smallest adequate route**：两个 nominal contact rollouts、一次集合差、固定合法端点、统一证书。

## Changes Made

### 1. 固定核心算法

- Reviewer said：`I_f/I_c` 只是合格条件，不是区别于 fuzzing 的算法。
- Action：把 ISRAC 定义为 `B* = G(C_candidate) \ G(C_factual)`；`C` 是 nominal rollout 的 simulator-native 接触集合，`G` 把接触 geom 映射为非机器人 body-owned 物理参数块。
- Impact：第一版方法身份从泛化“影响图”收窄为可实现、可消融的 action-conditioned contact-set subtraction。

### 2. 锁定成本、去重与状态语义

- Reviewer said：raw pair count 会被同一 block 的多个参数端点膨胀，且所谓 full state 不可审计。
- Action：主统计单位改为唯一 `(boundary, block, effect-signature)`；同一块多个端点只作强度曲线。两次 nominal contact rollout、所有端点、repeat 和证书 replay 全部计费。状态称为“枚举的 replay-relevant dynamic state”，明确可见字段和不可见 controller/cache。
- Impact：当前 24 raw pairs 仅为 feasibility，不再作为 24 个独立发现。

### 3. 文件级隔离 WAM audit

- Reviewer said：“WAM 尚未加载”只是过程性声明。
- Action：compiler 仅输出 immutable manifest、accepted/rejected candidates、静态参数 hash 和证书；其中禁止出现 residual、embedding、ranking、WAM ID。manifest 哈希后单独 audit，audit 禁止重新筛 pair。
- Impact：编译器统一称 `target-WAM-blind`，WAM harm 只作为 downstream utility test。

## Revised Proposal

# Research Proposal: ISRAC——影响分离的残差别名反事实编译器

### Technical Gap

反馈式 WAM、候选重排序、WAM exploitation、VLA metamorphic testing 和控制器 falsification 均已有先例。未被当前证据完整覆盖的窄问题是：能否不读取目标 WAM，利用 factual 与 candidate 的**动作条件物理依赖差**，高效编译“历史反馈相同、未来候选结果分叉”的 VLA 支持内反例，并给出严格证书。

第一版不再声称一般 dependency graph。它只研究接触介导的物理参数：一个候选动作将首次接触、而 factual 动作没有接触的非机器人表面，其 compliance/friction 可以在 factual 历史不可见，却改变 candidate 后果。真正要验证的是**集合相减本身**是否比只有 candidate contact 的搜索有效。

### Method Thesis

> 对冻结 VLA 的 factual chunk 和后继 candidate suffix 各运行一次 nominal contact trace，并用 `candidate contact blocks − factual contact blocks` 剪枝原生表面参数空间，可以在统一证书与完整调用计费下，提高独立 residual-alias witness 的发现率。

### Contribution Focus

- **唯一主贡献**：action-conditioned contact dependency-set subtraction 作为 target-WAM-blind witness compiler primitive。
- **用途验证，不是第二贡献**：冻结 manifest 上的 held-out feedback-WAM correction-harm audit。
- **不主张**：新 WAM/VLA 架构、一般物理可辨识性理论、完整世界状态、真实机器人安全保证。

### Canonical Compiler

给定相邻保存边界 `s_f, s_c`、冻结策略动作 `a_f, a_c`：

1. 在 nominal physics `η0` 下各回放一次，收集所有 simulator-native geom contact pair：`C_f` 与 `C_c`。这两次 rollout 计入预算。
2. `G(C)` 将接触 geom 映射到其 non-robot owning body，自动形成 surface parameter blocks；不读取任务谓词、对象名称白名单或 WAM score。
3. 主方法只保留
   
   `B* = G(C_c) \ G(C_f)`。
   
   `candidate-contact` 基线使用 `G(C_c)`，因此它知道 candidate activation，但不知道 factual subtraction；`random-scene` 从所有非机器人 body block 采样。
4. 每个 block 使用固定、预注册的三个合法物理端点。compliance 第一版固定为 `0.004/0.020/0.100 s`，friction 固定为 `0.05/0.30/1.50`；主方法不使用 BO/CMA 或目标模型梯度。
5. 对三个端点的每个无序 pair 使用同一 factual/candidate rollback 和同一证书。所有端点 rollout、repeat rollout、失败证书均计费。
6. 对一个 `(boundary, block)`，若多个端点 pair 合格，主指标最多计一个 `effect-signature`；其余记录为同一机制的 effect-strength curve。

当前实现每个边界的调用成本为：

`2 nominal-selection rollouts + 8 × selected block count`。

其中每个 block 的 8 次包括 3 个 factual 端点、3 个 candidate 端点和各 1 次 repeat。任何 baseline 使用相同 block count 时获得完全相同调用预算。

### Certificate Schema

每个静态世界写为 `W=(Z_t, η)`：

- `η`：静态 physics configuration。两个世界只允许目标 block 不同；`η+`、`η−` 各自完整哈希。
- `Z_t`：当前 simulator 可枚举的 replay-relevant dynamic state。LIBERO E0 记录完整 `MjSimState.flatten()`（当前任务为 79 维，含 time/qpos/qvel/act/udd_state），逐帧 proprio、RGB、depth，以及所有带关节非机器人 body 的 world pose。它不声称包含未暴露的 solver warm-start/contact cache 或连续 OSC controller cache。
- `A_t`：冻结动作序列及其来源 rollout hash。

证书要求：

1. factual 两世界中 `Z_{0:T}`、观测与 `A_{0:T}` 不超过同参数 repeat-noise envelope；
2. 静态配置只有一个预注册 block 不同；
3. candidate rollout 中该 block 被真实接触激活；
4. candidate effect 首次分叉与激活帧在预注册 lag 内；
5. candidate 来自冻结 VLA 成功轨迹的后继 suffix；
6. search terms 中没有 WAM score/ranking/embedding。

### Immutable Compiler/Audit Boundary

```text
Compiler input:
  snapshot + frozen VLA actions + simulator block schema
  + legal ranges + noise/certificate thresholds

Compiler output (manifest A):
  all accepted/rejected blocks and endpoints
  + observations/actions/dynamic-state evidence
  + η hashes + certificate hashes
  - residual / WAM embedding / WAM ID / ranking 全部禁止

hash(manifest A) 后不可修改

Audit input:
  frozen manifest hash + independently loaded target WAM

Audit output (artifact B):
  WAM residual equality + false transfer + ranking regret + correction harm
```

任何看过 WAM 结果后的删除、重排、阈值修改或 pair 子集选择都算违规。若 WAM 有 recurrent/cache state，audit 必须在 twin 之间显式克隆内部状态。

### Baselines and Isolation

所有方法共享 boundary、candidate、block schema、参数范围、endpoint sweep、effect predicate、证书、去重规则和总调用预算：

1. `random-scene`：从全部合法 non-robot blocks 随机选择相同数量；
2. `candidate-contact`：从 `G(C_c)` 选择相同数量，不做 `−G(C_f)`；
3. `no-subtraction constrained search`：在相同 MR/certificate 上使用 grid/CMA-ES/BO，所有调参与 probe calls 计费；
4. `ISRAC ablation`：显式去掉 factual subtraction，其他部分完全相同。

这不是要证明一个新的测试范式，而是证明一个明确的 simulator-native search primitive 是否提高发现率。

### Main Metrics and Statistics

- 主指标：unique certified `(boundary, block, effect-signature)` / 1k simulator rollouts；
- 次指标：raw endpoint pairs、calls/unique witness、passing-block rate、证书违规率、activation/divergence alignment、效应强度曲线和失败原因；
- 统计单位：独立 boundary；3 个 search seeds；paired boundary/bootstrap 95% CI；
- 当前 24 raw pairs 只写为“LIBERO feasibility：非空生成”，不得写作 24 个独立 witness。

### Claim-Driven Validation

#### C1（唯一方法主张）

在现有 8 个冻结策略边界上，先比较 ISRAC、candidate-contact 与 random-scene。pilot 通过只表示值得实现强 baseline：ISRAC 对最强简单 baseline 的 unique-witness yield point ratio ≥2，且优势不由单一 boundary 贡献。随后加入等预算 CMA-ES/BO；正式支持要求 95% CI 下界 >1、至少两个物理机制族复现。第二 simulator 只确认 abstraction transfer，不用于掩盖 C1 失败。

#### C2（用途验证）

仅在 C1 通过后，将 immutable manifest 输入至少两个 held-out feedback WAM；比较 severity-matched 普通物理扰动，报告 false transfer、pairwise ranking、rollback regret、correction-harm 和闭环成功。C2 不能挽救 C1。

### Failure/Kill Conditions

- candidate-contact 或最强 matched-call baseline 等效/更好：ISRAC 方法主张失败；可降级为 benchmark generator，但不能保持原新颖性结论。
- 去掉 subtraction 后 yield 不降：核心机制失败。
- 结果依赖同一 block 多端点重复计数、任务专用 object 名、action-indexed switch、宽松阈值或目标 WAM leakage：失败。
- 第二机制完全无 witness：接触依赖抽象过窄，需要停止或重新定义，不直接训练大 WAM。
- compatible feedback-WAM checkpoint 不存在：C2 暂停，但不得用不匹配 checkpoint 假装验证。

### Compute and Scope

- 当前 matched-call pilot 是 CPU MuJoCo/OSMesa，A100 对其无加速；它会完整跑完并按新去重规则重新分析。
- 通过 C1 后才重新检查 GPU 0–3 的即时空闲条件，并在个人目录启动 WAM inference/training。
- 所有代码、日志、checkpoint、cache 和结果仅在 `<PERSONAL_RESEARCH_ROOT>`；无真实机器人自主运动。
