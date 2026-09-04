# Round 2 Refinement

## Problem Anchor

- **Bottom-line problem**：反馈式 WAM 会利用一次已执行动作的预测残差，去修正、排序或拒绝另一个尚未执行的候选动作；但同一段 factual 反馈并不一定能识别不同候选动作所需的物理修正方向。我们需要自动构造可审计的具身反例，判断这种跨动作残差迁移何时在信息上不充分、何时会伤害 VLA 的动作选择。
- **Must-solve bottleneck**：现有 WAM 纠错与 VLA 测试缺少一种同时满足以下条件的反例生成器：factual 动态转录在两个合法物理世界中相同；候选动作由冻结策略真实提出；候选动作的物理结果发生可定位分叉；编译过程不读取被测 WAM 的 score；每个样本附带机器可验的 equality–activation–first-divergence 证书。
- **Non-goals**：不训练新的 RGB/Depth/PointMap WAM；不提出新的 VLA action head；不把一般 world-model exploitation、一般 metamorphic testing 或 two-point 不可辨识性定理包装成新贡献；当前不启动真实机器人；不使用触觉。
- **Constraints**：远端无外网；所有资产与结果仅位于 `<PERSONAL_RESEARCH_ROOT>`；冻结现有 StarVLA/π0.5 类策略；第一阶段以 LIBERO/robosuite rollback 为主；仅在编译器门槛通过后使用空闲 A100 做 WAM 审计；所有搜索与证书必须报告完整失败样本和 simulator-call 预算。
- **Success condition**：在相同 simulator calls、相同物理参数范围和相同证书下，ISRAC 相对最强 random/grid/CMA-ES/BO 类搜索至少获得稳健的 2× certified-pair yield，并跨多个任务、至少两个物理机制族复现；随后这些冻结并哈希的 pairs 在至少两个未参与编译的反馈 WAM 接口上显著提高 correction-harm 或 ranking-regret，相对普通强度匹配扰动具有特异性。

## Anchor Check

- 核心仍是 factual feedback 无法决定未来 candidate 的物理修正，而不是一般 WAM 质量或 VLA 鲁棒性。
- 本轮只封闭搜索原语的定义、调用预算、连续状态和 witness 身份，没有增加模型。
- 若严格协议下集合相减不优于 exact ablation，则停止 ISRAC 方法主张；不会用 WAM harm 或更多 benchmark 挽救。

## Simplicity Check

- **唯一主贡献**：action-conditioned realized contact-support subtraction。
- **核心路径**：two nominal traces → geom-level support subtraction → fixed endpoint replay → certificate → immutable manifest。
- candidate-contact 与 no-subtraction ablation 合并为一个 exact ablation；主强优化器后续只选择一个完整计费的 CMA-ES 或 BO，不并列堆积。
- 不引入 learned dependency graph、LLM searcher、RL、Depth/PointMap head 或新 WAM。

## Changes Made

### 1. 将 `G` 固定为 geom 级参数地址并给出限定 soundness

- 每个 block 唯一标识 simulator/version、model hash、geom id、body id、parameter family、runtime parameter indices 与合法 endpoints。
- 术语改为 realized contact-support，而不声称一般 causal dependency graph。
- 增加只针对 contact-local parameter family 的 soundness proposition；证书处理接触拓扑变化和数值例外。

### 2. 用固定调用上限替代相同 block 数

- 每个 boundary 的 P025 cap 固定为 26 rollouts：2 次 nominal trace，加至多 3 个 block × 8 次 endpoint/repeat rollout。
- candidate-contact 只能读取 `G(C_c)`，不知道 `C_f` 或 `|B*|`；按预注册 seeded geom permutation 搜到 cap。
- ISRAC 只读取 `G(C_c)\G(C_f)`；pool 不足时未用预算仍计入 denominator。

### 3. 封闭连续状态与 witness identity

- 两个 world 从同一 factual snapshot 和同一 reset rule 开始；candidate 直接从各 factual endpoint 继续，不加载独立 nominal candidate state。
- 保存 nominal factual endpoint 与原轨迹下一 boundary 的误差，只作 policy-support 诊断。
- 主 witness key 固定为 source trajectory hash、boundary、candidate hash、geom id、parameter family；endpoint pair 与 effect strength 不参与独立计数。

## Revised Proposal

# ISRAC: Certified Search by Realized Contact-Support Subtraction

### Problem and Delta

反馈 WAM 会把 factual 动作暴露的预测误差迁移到另一个 candidate。已有工作覆盖反馈纠错、候选 rollout、WAM exploitation、VLA metamorphic testing 与通用 simulator falsification。ISRAC 不再主张新的测试范式；它检验一个更窄的机制：**factual 与 candidate 的 realized contact support 差，是否是一种有局部物理 soundness、且能在等 calls 下提高 residual-alias witness 发现率的搜索剪枝原语。**

### Exact Domain

第一版仅覆盖 MuJoCo/SAPIEN 中通过指定 geom 的局部接触律才生效的参数，如 surface compliance 或 Coulomb friction。参数块为：

```text
(simulator version, model hash, geom_id, body_id,
 parameter family, exact runtime/XML indices, legal endpoint tuple)
```

不覆盖质量、重力、磁力、长程约束、视觉外观或会在无接触时生效的参数。

### Realized-Support Soundness Proposition

设局部参数 `η_g` 只出现在 geom `g` 的接触转移项中。若在 factual horizon 内：

1. `g` 不在 nominal realized contact support；
2. 改变 `η_g` 不改变 factual contact topology；
3. 非接触转移与传感器生成不依赖 `η_g`；
4. simulator/controller/RNG reset 在 twin 间一致；

则 factual horizon 的枚举 replay-relevant dynamic state 与观测不受 `η_g` 影响。因此：

```text
B* = G(C_candidate) \ G(C_factual)
```

是“factual-invariant、candidate-possibly-active” block 的 sound candidate set。该命题不保证参数变化不会改变接触拓扑；最终 equality–activation–first-divergence certificate 对所有 endpoint 重放，拒绝此类例外、非确定性和数值漂移。

### Canonical P025 Algorithm

1. 从冻结 StarVLA 成功轨迹读取 factual snapshot、factual chunk 和固定后继 candidate suffix。
2. 在 nominal physics 下，从同一 factual snapshot 连续执行 factual→candidate；分别记录 `C_f`、`C_c`。两个 segment 的 nominal rollout 都计费。
3. `G` 将每个非机器人 contact geom 映射到精确 contact-parameter 地址。
4. ISRAC pool 为 `G(C_c)\G(C_f)`，按固定 geom id 顺序探索；candidate-contact exact ablation pool 为 `G(C_c)`，按预注册 seeded uniform permutation 探索；random-scene 从全部合法 geom 地址同样采样。
5. 每 boundary 固定收费 26 rollouts；最多探索 3 个 block。每 block 使用 3 个预注册端点：6 次 factual/candidate endpoint replay + 2 次 repeat。pool 不足的未用预算仍收费，任何方法都不知道另一方法的 pool size。
6. 对每个参数 endpoint，从同一 factual snapshot 开始，一次 reset 后连续执行 factual→candidate；不加载保存的独立 candidate snapshot。
7. certificate 检查 factual dynamic state、proprio、完整 RGB/depth array digest、candidate 参数激活、首次物理分叉、单 block 合法静态配置、动作/轨迹 hash 与 search-term anti-leakage。

### State and Static Configuration

- `η+ / η−`：完整运行时 `geom_solref` 与 `geom_friction` 数组在修改后的 SHA-256；只允许指定 geom/family endpoint 不同。
- `Z_t`：完整 `MjSimState.flatten()`、完整 proprio；RGB/depth 使用包含 dtype/shape/全部 bytes 的 SHA-256 digest；所有可移动非机器人 body pose 作为 effect evidence。
- 不声称覆盖 simulator 未暴露的 solver warm-start/contact cache。控制语义为 `restore_canonical once → factual → candidate`；controller/reset mode、RNG seed、model hash 和软件版本写入 metadata。
- 保存 `replayed factual endpoint` 与原轨迹 `candidate boundary` 的最大差异；若超过预注册 policy-support tolerance，该 boundary 不进入正式 claim。

### Witness Identity and Accounting

主 witness key：

```text
(source trajectory hash, boundary step, candidate hash,
 geom id, parameter family)
```

每个 key 最多计一次。三个 endpoint 的多个合格 pair、effect signature 与强度曲线仅作 metadata。主指标为 unique witness / charged 1k rollouts；同时报告 raw endpoint pairs、actual/unused budget、passing-block rate、证书违规与全部失败原因。

### Compiler/Audit Isolation

Compiler manifest 只含 simulator schema、actions、static hashes、accepted/rejected endpoints 与 certificate；不得含 WAM residual、embedding、ranking、WAM ID。manifest 哈希冻结后，单独 audit artifact 才可加载 target WAM；audit 必须消费全部 accepted witness，禁止后筛。

### Validation and Kill Gate

- **Protocol debug**：旧 P024 完整落盘，但它使用 equal block count 且独立 candidate snapshot，只能诊断，不能验证方法。
- **P025 sanity**：先在一个边界确认连续执行、endpoint fidelity、固定 cap、geom block 与 manifest anti-leakage。
- **P025 pilot**：当前已看过的 8 boundaries 只测试协议稳定性；主张需要新冻结的 held-out boundaries。ISRAC 与 candidate-contact/random-scene 共享固定 cap、参数地址、端点与证书。
- **主 gate**：对最强 simple exact ablation 的 unique-witness point ratio ≥2；随后固定一个强 CMA-ES/BO baseline，正式结果要求 paired boundary CI 下界 >1、至少两类 contact-local mechanisms。8 boundaries 的 CI 明确标为探索性。
- **Kill**：exact ablation 等效/更好；优势来自 endpoint 重复计数、边界事后选择、任务对象白名单、candidate pool size 泄漏、独立 candidate reload、宽松阈值或 target-WAM 结果时，停止方法 claim。
- **C2**：只有 C1 通过后，才在 immutable manifest 上测试至少两个 held-out feedback WAM 的 false transport/ranking regret/correction harm；C2 不能挽救 C1。

### Resources

P025 为 MuJoCo/OSMesa CPU 实验，A100 不加速。GPU 只在 C1 通过且存在兼容 feedback-WAM checkpoint 后启用；每次启动重新检查四卡，所有资产留在 `<PERSONAL_RESEARCH_ROOT>`，不启动真实机器人。
