CALIBRATION: none

本轮仍无 curated known-good / known-bad proposal 可作外部定标。分数严格评价修订后的方法设计；已有 24 raw pairs 仅计 feasibility，正在运行但尚未冻结的 random/contact baseline 不计入方法有效性、新颖性或 venue readiness。

## Scores

| Dimension | Round 1 | Round 2 | Review |
|---|---:|---:|---|
| Problem Fidelity | 9 | 9/10 | Problem Anchor 原文保持，方法仍直接针对 factual residual 跨 candidate 不可识别，没有漂移成一般 VLA robustness、WAM 改进或 benchmark 扩张。 |
| Method Specificity | 6 | 8/10 | 主方法已实质收敛为两个 nominal traces、`G(C_c) \ G(C_f)`、三个固定端点和统一证书，工程师可以开始实现。剩余歧义集中在 `G` 的粒度、连续 factual→candidate replay 语义、baseline 的 block selection，以及 controller/cache 状态初始化。 |
| Contribution Quality | 6 | 7/10 | 唯一主贡献现在清晰、可消融且没有 optimizer 混杂。但它仍可能被评价为一个非常直接的 contact-support MT/fuzzing heuristic；需要 simulator 接触局部性的 soundness argument 和严格消融才能升级为机制贡献。 |
| Frontier Leverage | 8 | 8/10 | 冻结 VLA 只作支持内 action source，target WAM 完全后置，使用恰当且克制。无需加入 learned influence model、LLM searcher、RL 或生成式 WAM。 |
| Feasibility | 7 | 8/10 | 接触集合、MuJoCo 参数端点、rollback 和 manifest 都是低风险实现；已有非空 pair 支持这一判断。但不能把可实现性误写成集合相减已经有效。 |
| Validation Focus | 8 | 7/10 | unique witness、完整 calls 和 C1→C2 gate 都明显改善；但“相同 block count”可能泄漏 ISRAC 的筛选规模或使 baseline 选择不唯一，8 个 boundary 上的 bootstrap 也只能作探索性区间。 |
| Venue Readiness | 6 | 6/10 | 论文形状更干净，但顶会贡献上限仍未突破：若没有接触局部性带来的明确 soundness/efficiency 原理，以及公平预算下的强结果，`candidate contacts minus factual contacts` 很容易被认为是显然的测试工程。 |

**Weighted OVERALL SCORE: 7.75/10**

\[
0.15(9)+0.25(8)+0.25(7)+0.15(8)+0.10(8)+0.05(7)+0.05(6)
=7.75.
\]

## Anchor Status

**ANCHOR PRESERVED — no drift.**

修订仍解决原始问题：构造在 factual feedback 下不可区分、在后继 policy-supported candidate 下物理分叉的 twin worlds，以检验残差跨动作迁移。把方法缩到接触介导的 compliance/friction 是合理的 scope restriction，不是问题漂移。

需要守住一个边界：如果集合相减失败，不能把 C2 的 WAM harm 改写成新的主要贡献。修订版已经明确这一点。

## Dominant Contribution Sharpness

**明显变尖锐，但术语仍略有过度。**

现在可以用一句话识别方法：

> 使用 nominal candidate 与 factual rollout 的接触支持集差，预筛只可能在 candidate 阶段生效的物理参数块。

这比上一版的泛化 influence graph 清楚得多，也真正与 endpoint solver、WAM audit 解耦。

但是，当前 `C` 是一次 nominal rollout 中实际发生的接触集合，`G(C)` 只是把 geom contact 映射到参数地址；它不是一般意义上的 dependency graph，也没有证明完整的 causal influence。因此在没有 soundness 命题前，建议统一称：

**action-conditioned realized contact-support subtraction**

而不是较强的 “contact dependency-set subtraction”。后一个名称会邀请审稿人追问未发生但潜在可达的接触、非接触力、body 内多 geom、约束传播和参数改变后接触拓扑变化。

## Simplicity

**方法已经足够小，没有复杂度膨胀。**

核心路径只有：

```text
two nominal traces
→ contact-support subtraction
→ fixed endpoint replay
→ certificate
→ immutable manifest
```

这是本轮最成功的修订。C2 已被正确降为用途验证，没有形成第二条方法线。

仍可删除两处冗余：

1. `candidate-contact` 与“显式去掉 factual subtraction、其余完全相同”的 ISRAC ablation 本质上应是同一个 exact ablation，不应列成两个系统。
2. `grid/CMA-ES/BO` 不应在一个 baseline 名称下并列。固定一个最强、可完整计费的黑盒 optimizer；其余不需要为了数量而保留。

## Frontier Leverage

**Appropriate, not forced.**

冻结 foundation VLA 提供真实策略支持内的 factual/candidate suffix，正好保证反例不是手写破坏动作；target WAM 后置保证编译器不对特定模型过拟合。这已是足够的 foundation-model-era leverage。

MODERNIZATION OPPORTUNITIES: NONE.

加入 learned graph、VLM semantic selector、LLM search policy、RL curriculum 或 differentiable simulator 都会削弱当前贡献的可审计性与简洁性。

## Previous Blocking Issues

### 1. `G(C_candidate) \ G(C_factual)` 是否已成为可复现主方法

**大体解决。**

固定 nominal traces、固定集合差、固定三个端点和无 BO/CMA 的主路径已经消除了上一轮最严重的算法不唯一问题。

但 `G` 必须进一步固定为真实的 simulator 参数地址，而不是模糊的 owning body：

\[
G(C)\rightarrow
\{(\text{geom\_id},\text{parameter family})\}.
\]

MuJoCo friction/compliance 通常是 geom/contact 局部属性。若 factual 接触 body 的 geom A、candidate 接触同一 body 的 geom B，body-level subtraction 会错误删除 candidate-only surface。每个 block 至少应包含：

```text
simulator version
geom_id
owning body_id
parameter family
exact runtime/XML parameter indices
legal endpoint tuple
```

### 2. candidate-contact 是否真正只缺 factual subtraction

**概念上解决，协议上尚未完全解决。**

它现在明确只能读取 `G(C_c)`，不能读取 `C_f`，这是正确的 exact ablation。

但“选择与 ISRAC 相同 block count”有泄漏和公平性问题：

- ISRAC 的 `|B*|` 本身依赖 `C_f`；
- 把这个 K 告诉 candidate-contact 会泄漏 factual subtraction 的输出规模；
- 不说明从 `G(C_c)` 中如何选 K 个 block，会留下有利于 ISRAC 的自由度；
- 若 `|B*|=0`，等 block count 会让两者都不搜索，无法比较。

应改成**固定 per-boundary simulator-call cap**，而不是固定 block count。两种方法各自用其可见信息决定探索顺序并运行到预算耗尽；candidate-contact 的顺序必须预注册为 uniform seeded sampling 或固定 geom-ID 顺序。ISRAC 的两个 nominal trace 成本仍全部扣除。

### 3. calls 与 unique witness 是否足以隔离机制

**方向正确，但尚差两个定义。**

`2 + 8K` 的成本账已经比上一轮严谨，且 endpoint trajectory 可以复用于三个无序 pair，因此六次 endpoint rollout 加两次 repeat 在逻辑上成立。

仍需修正：

- 主 witness key 不应包含尚未定义的 `effect-signature`，否则同一 block 可通过改变 signature 划分再次膨胀。最简单的主键是  
  `(source trajectory hash, boundary id, candidate hash, geom id, parameter family)`，每个主键最多计一次。
- 若每个 boundary 严格预注册一个 candidate，则可以省略 candidate hash；否则必须加入。
- `effect-signature`、多个 endpoint pair 和 effect strength 只作为 witness metadata，不参与主计数。
- 所有方法按固定 boundary budget 比较，不能同时使用“相同 K”和“每 1k calls”两套不完全一致的公平性规则。

完成后，matched-call ablation 足以检验“subtraction 是否提高 search yield”，但仍不能单独证明一个全新的测试范式；修订版对此表述是诚实的。

### 4. Dynamic state / static hash

**大部分解决，尚有一个执行级缺口。**

将世界拆为 `W=(Z_t,η)`、完整哈希 `η+ / η−`、把 claim 降为枚举的 replay-relevant dynamic state，都是正确修复。明确不包含 solver warm-start/contact cache 也比声称 full simulator state 严谨。

剩余问题是：不可见的 OSC controller/cache 状态虽然不在证书内，仍可能影响 candidate rollout。仅声明“不声称包含”不能排除 twin divergence 来自不同 hidden controller state。

必须固定连续执行语义：

1. 两个 world 都从同一 `s_f` snapshot 与相同 controller/RNG initialization 开始；
2. 在 `η+`、`η−` 下分别执行同一个 `a_f`；
3. candidate `a_c` 必须直接从各自 factual endpoint 继续执行，不能重新加载一个独立的 nominal `s_c`；
4. controller 必须无状态、可显式 clone，或在每次 replay 前按相同规则 reset；
5. controller version、reset mode、RNG state 和 simulator/model hash 写入 certificate metadata。

否则 equality 只覆盖可见 `Z_t`，没有覆盖真正决定下一 candidate transition 的完整接口状态。

### 5. Compiler / audit 文件接口

**已解决到足够严谨。**

Manifest A 禁止包含 residual、embedding、ranking、WAM ID；hash 后才允许加载 WAM；Artifact B 只能消费固定 manifest；禁止 WAM 后筛 pair；recurrent/cache state 必须 twin-clone。这已经是清晰、可审计的 target-WAM-blind interface。

无需增加容器、可信执行环境或新软件模块。实现时只需保证 audit 默认消费全部 accepted witnesses，并把 manifest hash 写入每个输出记录。

## Is This Still MT/Fuzzing Engineering?

**目前仍有这个风险，但已不再必然只是工程。**

从测试范式看，它仍是一个针对 VLA/WAM 的特定 metamorphic relation；从搜索算法看，它是 contact-informed parameter pruning。集合差本身非常简单，这不是缺点，但审稿人需要看到它为什么不仅是直觉。

不增加模块的最小升级是给出一个窄的 simulator-semantics soundness statement：

> 对仅通过指定 geom contact law 生效的局部参数族，若 geom 不在 factual rollout 的 realized contact support 中，且改变参数不改变该 rollout 的接触拓扑，则该参数在 factual horizon 内不影响枚举动态转录；因此 `G(C_c)\G(C_f)` 是 factual-invariant、candidate-possibly-active blocks 的 sound candidate set，最终证书处理拓扑改变或数值例外。

这不是声称一般不可辨识性理论，而是说明 subtraction 有明确的 simulator-local soundness basis。配合 exact ablation 的 matched-call 优势，工作可上升为一个小而清楚的 certified search primitive。没有这条原理，即使出现 2×，仍可能只被视为经验启发式。

## Remaining Blocking Actions

### BLOCKER 1 — Formalize the primitive’s exact domain and soundness

- 把 `G` 固定到 `(geom_id, parameter family, parameter address)`；
- 明确只覆盖 contact-local parameters；
- 写出 realized-contact-support soundness proposition 及其假设；
- 用 certificate 捕获 contact topology 改变、非确定性和实现例外。

**Priority: CRITICAL**

### BLOCKER 2 — Replace equal-block-count with a leakage-free call budget

- 每个 boundary 预注册相同 call cap；
- 所有 setup、nominal trace、probe、repeat、失败 certificate 都扣费；
- candidate-contact 不得读取 `C_f` 或 `|B*|`；
- candidate-contact 的 block order/sampling rule 和 seeds 必须预注册；
- exact no-subtraction ablation 与 candidate-contact 合并。

**Priority: CRITICAL**

### BLOCKER 3 — Close sequential state and witness identity

- candidate 必须从各 factual twin endpoint 连续执行；
- controller/RNG/cache 必须相同 reset 或显式 clone；
- 主 witness key 加入 candidate/geom/parameter-family identity；
- effect signature 不参与独立发现计数。

**Priority: IMPORTANT**

### BLOCKER 4 — Evidence remains open

完成并冻结正在运行的 baseline 后，按上述协议重新计算 unique yield。当前 24 raw pairs 和未完成 baseline 仍然只说明 feasibility。若 exact ablation 等效，停止方法 claim；不得靠 C2、第二 simulator 或更多 benchmark 拉高分数。

**Priority: CRITICAL**

## GAP

本轮已经从“定义一个合格 pair”前进到“给出一个可实施的单一搜索原语”，这是实质提升。距离 9 分的差距现在很集中：需要把 realized contact set 与真正可修改的 geom-level 参数地址严格对齐，给出该剪枝在限定接触动力学下为何 sound 的最小论证，并用不泄漏 `|B*|` 的固定调用预算证明收益。动态/静态状态和 compiler/audit 文件边界已基本封闭，不再是主要问题。若上述协议下获得跨 boundary 的稳定优势，这会成为一篇小而明确的 certified diagnostic compiler；若不能，它仍只是合理的 MT/fuzzing 工程，修订文本本身不能替代这一证据。

## Drift Warning

NONE.

Problem Anchor 保持；dominant contribution 更单一；方法更简单；frontier leverage 仍适当。没有必要引入任何新模型或扩大 benchmark。

## Verdict

**REVISE**

修订解决了上一轮大部分结构性问题，但 weighted score 仍为 7.75，且存在四个 blocker。READY 要求 overall ≥9 且无 blocker；在 matched-call baseline 冻结、contact-support soundness 与公平预算协议闭合之前，不能判为 READY。
