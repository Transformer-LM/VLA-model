# Action-Fiber Set Diffusion：严格新颖性 Jury

## 最终判决

- **Verdict：FAIL**
- **Novelty：6.90 / 10**
- **严格门槛：必须 >7.0；7.0 本身也 FAIL**
- **Naturalness：6.65 / 10**
- **Scoop level：Level 2 / High Overlap**（最强近邻匹配四轴中的三轴）
- **小型 compiler E0：不授权**
- **GPU/训练实验：不授权，且本轮未启动任何实验**

没有检索到一篇论文逐项包含“同一 VLA state 的 rollback-verified K 个接触/接近 action chunks、joint set diffusion、unbalanced OT、短前缀执行”全部组件。但这不足以通过严格门槛：已有文献分别覆盖了该候选最重要的三条思想——**轨迹集合覆盖、集合级匹配、多模态机器人 action diffusion**。剩余组合是连贯的，但目前更像把 SetTraj/CoverNet 的 trajectory-set 学习迁移到 Diffusion Policy/VLA，并用 planner/rollback 生成集合标签。

更严重的是，当前 claim 把“生成 chunk 未匹配有限 planner roster”解释为“invalid probability mass”。有限 planner 集不是完整 feasible set；未匹配的 chunk 可能是 planner 没枚举到的可行解。没有额外可微 validity oracle、校准的 feasibility estimator 或经过验证的 support estimator，UOT 不能给这个物理语义兜底。

## 被审查的精确 claim

给定相同 RGB、proprioception、语言状态和可见功能几何：

1. 从同一 simulator checkpoint rollback，得到无序的 `K` 个 temporally extended feasible action chunks；
2. 用 approach/contact event clustering 让它们跨越不同可行 mode；
3. VLA diffusion action head 一次联合生成 `K` 个 chunks；
4. 使用 permutation-invariant unbalanced OT 做 set-to-set matching；
5. 显式惩罚遗漏的 feasible modes 和生成的 invalid probability mass；
6. 部署时从集合选一个 mode，只执行短前缀并重新观察；
7. 不使用 WAM、value model、test-time reranking 或触觉。

## 四个 novelty 轴

### 1. Problem framing

学习同一视觉状态下多个 temporally extended、物理可行且接触结构不同的机器人动作，而不是只拟合一条示范。

**判定：中等新颖。** VLA 场景和 rollback-verified contact modes 是较新的限定，但“同一状态存在多种合理轨迹，需要覆盖多模态支持”是 Diffusion Policy、Factorized Diffusion Policy、RPDiff、CoverNet 和多模态轨迹预测的共同出发点。

### 2. Core mechanism

joint K-set diffusion + permutation-invariant UOT set matching，双向惩罚 target omission 和 generated unmatched mass。

**判定：中等偏低。** SetTraj 已将多模态轨迹预测改写为端到端 set prediction 并使用 Hungarian matching；CoverNet 已围绕有限 trajectory set 的 coverage 与 physically impossible trajectories 建模。把 Hungarian/assignment 换成 unbalanced OT 能处理未匹配质量，但还没有形成机器人专属的新 learning principle。

### 3. Key insight

普通 diffusion 的 i.i.d. 多采样或单示范训练不能保证覆盖多个可行 mode；应联合预测整个 action set，并直接监督 mode omission。

**判定：低到中。** 多假设轨迹预测、trajectory-set classification、multiple-choice learning 和 diversity-aware prediction 已长期研究这个问题；Factorized Diffusion Policy 也明确以不同 diffusion components 捕获 behavioral sub-modes。候选的独特点是把这些思想落在 rollback-verified manipulation action chunks 上。

### 4. Application domain

RGB/proprio/language-conditioned VLA，面向可见 functional geometry 的闭环 manipulation。

**判定：中高。** 尚未找到 exact VLA set-diffusion 近邻，但“将已有 set-prediction 机制应用于 VLA”本身不足以自动构成高新颖性。

## Primary-source exact-mechanism 对照

| Primary source | 实质覆盖 | 关键差异 |
|---|---|---|
| [SetTraj: Reformulating Multimodal Pedestrian Trajectory Prediction as End-to-End Dynamically Adaptive Set Prediction](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5854926) | 直接把多模态轨迹预测改写成 set prediction；Hungarian matching；端到端产生 coherent、well-calibrated trajectory set；动态 observation-conditioned queries | 行人预测，不是机器人控制；没有 simulator rollback、接触 mode、diffusion head 或物理执行 |
| [CoverNet: Multimodal Behavior Prediction using Trajectory Sets](https://arxiv.org/abs/1911.10298) | 明确构造有限 trajectory set 以获得 coverage，并排除 physically impossible trajectories；对 trajectory set 建模概率 | 自动驾驶预测，不是执行 policy；使用 classification，不是 learned joint diffusion set |
| [Flexible Multitask Learning with Factorized Diffusion Policy](https://arxiv.org/abs/2512.21898) | 机器人 manipulation action diffusion；多个 diffusion components 捕获不同 behavioral sub-modes；observation-conditioned composition | 最终采样一个 action trajectory；没有 K-set 输出、set matching 或 rollback-verified per-state roster |
| [Diffusion Policy](https://arxiv.org/abs/2303.04137) | 视觉条件 action-chunk diffusion；receding-horizon execution；明确以 multimodal action distribution 为核心优势 | 标准单样本 denoising objective；K 次采样彼此独立，没有集合级 coverage loss |
| [RPDiff](https://arxiv.org/abs/2307.04751) | 局部几何条件下拟合多模态 manipulation solutions；扩散产生精确且多模态的 relational placements | 输出 terminal SE(3) pose，不是完整 action chunks；没有 joint set objective 或接触顺序 |
| [SPLIT](https://arxiv.org/abs/2411.10049) | 3D scene-to-pose-set matching；SE(3) diffusion 从局部几何生成多用途 pose samples | pose sampling，不是 temporally extended VLA action set；没有 set-to-set omission objective |
| [Learning Action Manifold with Multi-view Latent Priors for Robotic Manipulation](https://arxiv.org/abs/2605.11832) | VLA/机器人 action manifold 叙事；几何增强；直接生成 action chunks | “valid manifold”是 clean-action prediction 的动机，不枚举可行集合，也不训练 mode coverage |
| [Motion Planning Diffusion](https://arxiv.org/abs/2308.01557) | 从成功 planner trajectories 学习多模态 robot motion distribution，并泛化到未见障碍 | 是 generative motion-planning prior；没有语言 VLA 或 K-set supervision |
| [M2Diffuser](https://arxiv.org/abs/2410.11402) | 3D scene-conditioned diffusion，从 expert planner trajectories 学习高维 manipulation motion distribution，并以物理 cost 引导 | test-time optimization/guidance；不是直接 actor 的 set-to-set coverage objective |
| [Factorized Diffusion Policy之外的 Discrete Policy](https://arxiv.org/abs/2409.18707) | 面向机器人多任务中“一项任务多种完成方式”的多模态 action representation | 离散 latent code，不联合预测可行 trajectory set |

SetTraj 的 SSRN PDF 在本次访问中返回 403；其上表描述只使用作者在官方 SSRN 页面公开的摘要声明，没有把未核验的正文细节当作证据。其摘要已经足以确认最危险的 headline mechanism：trajectory set prediction + Hungarian matching。其他核心判断来自官方 arXiv 页面或全文。

## 最强近邻与 overlap 等级

### 最强核心机制近邻：SetTraj

- **Problem framing：match**——多模态未来不能靠一个轨迹表示，应直接产生预测集合。
- **Core mechanism：partial/match**——无序输出集合与 assignment matching 已存在；UOT 是更一般的软/不平衡 assignment。
- **Key insight：match**——集合级学习用来提高多样性、覆盖与校准。
- **Application domain：different**——行人预测而非 VLA manipulation。

按 scoop-check 的四轴规则，这是 **3 axes matching → Level 2 / High Overlap**。

### 最强领域近邻：Factorized Diffusion Policy

- **Problem framing：match**——机器人 action distribution 高度多模态，不同 mode 应被明确表示。
- **Core mechanism：different/partial**——多个 diffusion components，而非 joint K-set + UOT。
- **Key insight：match**——单体 diffusion 容易 underfit，不同 behavioral sub-modes 需要结构化表示。
- **Application domain：match**——视觉机器人 manipulation diffusion policy。

同样是 **Level 2 / High Overlap**。

### 最强语义近邻：CoverNet

CoverNet 已同时说出候选最想拥有的两个目标：finite trajectory set 的 coverage，以及排除 physically impossible trajectories。候选把这个预测问题改成机器人 action generation 并学习连续 chunks，但“coverage + invalid trajectory mass”不能再作为新 insight。

## 是否只是组件重组

严格判定：**当前主要是非平凡但仍然直接的组件重组。**

推导链条非常自然：

1. Diffusion Policy 能拟合多模态 action chunks；
2. planner/rollback 能从同一状态给出多条可行路径；
3. SetTraj/CoverNet 说明多模态轨迹可作为无序集合监督；
4. Hungarian/OT 解决输出 slot 与 target trajectory 不具固定对应关系；
5. unbalanced OT 允许未匹配质量并对其收费；
6. receding-horizon policy 只执行其中一条轨迹的短前缀。

这套组合是连贯的，但缺少一个只有机器人 action-fiber 才产生的新算法约束、估计理论或控制机制。没有单篇论文包含所有六步，不足以把 novelty 提升到严格 7 分以上。

## 致命方法学反对

### 反对 1：unmatched 不等于 invalid

编译器只输出 planner 找到的 `K` 条轨迹：

`F_hat(s) = {a_1, ..., a_K} subset F_true(s)`。

如果生成轨迹 `a_new` 没有靠近 `F_hat(s)`，UOT 会把它当 unmatched source mass；但它可能属于 `F_true(s)`，只是 planner 没找到。于是所谓“invalid probability mass penalty”其实是“远离有限 roster 的质量惩罚”，会压制新但可行的 mode。

当前最多能称为 **roster-unmatched mass**，不能称为 physical invalid mass。

### 反对 2：一个 K-set 不是已校准的 action probability distribution

模型联合输出 `K` 个 chunks，但 proposal 没有定义每个 slot 的概率质量、可变基数、duplicate 合并或 mode existence。部署时如果均匀选择一个 slot，模型被强迫给 planner roster 中每个 mode 相同概率；如果按 learned weights 选择，则又需要额外校准目标。集合 coverage 与单次执行所需的 action marginal 不是同一对象。

因此，“explicitly penalizes invalid probability mass”在当前输出参数化下甚至没有被完全定义。

### 反对 3：收益可能完全来自 planner data augmentation

把每个状态的 K 条成功轨迹拆开，以标准 Diffusion Policy 训练，并在测试时匹配总采样数，已经可能恢复相同分布。若 joint set model 只是在一个 batch 中看见 K 个 positives，其收益不是 set objective 的证据。

### 反对 4：固定 K 与真实 mode 数冲突

不同 functional geometry 下可行接近/接触 modes 数量不同。固定 `K` 要么复制 mode，要么将同一连续 mode 人为切成多个 cluster，要么遗漏 mode。UOT 能放松匹配质量，但不能自动决定真实 mode cardinality。

## Reviewer 最可能的一句话否决

> “This is SetTraj/CoverNet-style multi-trajectory set prediction attached to a Diffusion Policy/VLA head and supervised with planner rollbacks. Replacing Hungarian matching with unbalanced OT does not make unmatched planner-roster mass physically invalid, and the paper does not establish that the finite target set represents the feasible action fiber.”

目前没有足够强的回答。

## 剩余最小、可 defend 的 delta

若保留该方向，唯一较稳妥的差异是：

> 对同一个完整 robot/VLA state，通过 simulator rollback 取得经执行验证、按 approach/contact events 去重的 temporally extended action-chunk roster，并研究 joint set supervision 是否比把这些 chunks 当作独立 demonstrations 更好地保留已枚举的 manipulation modes。

这是一项有价值的数据协议与经验问题，但不能扩大成“学习完整 feasible action fiber”或“显式消除 invalid probability mass”。

一条严格可用的 delta statement 是：

> Unlike Factorized Diffusion Policy, which represents behavioral sub-modes through composed diffusion components trained on ordinary demonstrations, the proposed study supervises a single VLA action head with rollback-verified same-state action-chunk rosters and permutation-invariant set matching, testing whether joint roster supervision improves verified contact-mode recall at a fixed training-data and sampling budget.

注意这里主动删除了“完整 feasible set”“invalid probability mass”和“保证不漏 mode”。

## Claim ceiling

即使实验结果为正，当前机制最多支持：

> 在编译器可枚举、simulator 可复现、RGB 可观测的若干 manipulation geometry families 中，joint set-supervised action diffusion 相比独立 demonstration diffusion，在固定成功轨迹数量、训练算力和测试 action-sample budget 下，提高 compiler-roster recall / worst-roster-mode success，同时保持闭环任务成功率。

不能支持：

- 学到真实或完整的 feasible action fiber；
- 对所有可行 mode 提供 coverage 保证；
- UOT unmatched mass 等价于物理 invalid probability mass；
- 首次表示多模态机器人 action distribution；
- 首次从 planner trajectories 训练 diffusion robot policy；
- 首次做 trajectory-set coverage 或 set matching；
- 一般化到编译器未枚举的新接触 mode；
- 安全保证。

## Naturalness 评估

正面因素：

- 多个 approach/contact modes 是操作任务的真实结构，不是纯粹为论文制造的 latent；
- 同一 checkpoint rollback 比从不同 episode 拼接“多解”更干净；
- 无序集合符合 mode 本身没有天然 slot 编号的事实；
- 部署无需 WAM、reranking 或额外传感器。

负面因素：

- fixed-K set 与可变数量的真实可行 modes 不匹配；
- set coverage objective 与最终只执行一个 action 的 calibrated marginal 不一致；
- UOT 对有限 roster 的距离没有物理 invalidity 语义；
- joint K diffusion 的必要性尚未区别于 K 次普通 sampling；
- planner 发现频率会被模型误当成 mode 概率或等权存在性。

综合 **Naturalness = 6.65 / 10**。

## 最小 falsifier 与 E0 授权

### 理论上最小的非 GPU falsifier

在任何训练前，只对三个 geometry families 做 50–100 个 states 的 compiler audit：

1. 每个 state 是否稳定得到至少两个经 rollback execution 验证、事件上不同的成功 mode；
2. 更换 planner seeds 后，roster 的 Jaccard/cluster coverage 是否稳定；
3. 增加 planner budget 时，新发现 feasible modes 是否快速饱和；
4. target-set 外的随机/优化 trajectories 中，是否存在大量 simulator-valid alternatives；
5. fixed `K` 是否在不同 state 上造成频繁 duplicate、truncation 或 empty slot；
6. 只以 action distance 构造的 UOT cost 是否能区分“新可行 mode”和“invalid trajectory”。

预注册 kill criteria：

- 少于 30% 的 states 能得到至少两个事件可分的成功 modes；
- planner budget 翻倍后，超过 20% 的 states 仍新增 mode，说明 roster 未饱和；
- target-set 外生成/搜索到的 trajectories 中 simulator-valid 比例超过 10%，却会被 UOT invalid-mass 项惩罚；
- 超过 20% 的 states 需要复制或截断 mode 才能填满固定 K；
- action-space OT cost 对 valid-unseen 与 invalid 的 AUROC `<0.75`。

### 本次正式授权

**不授权小型 compiler E0。** 原因不是 compiler 不可行，而是当前候选 novelty 为 6.90，未通过用户要求的 `>7.0` gate。先跑 compiler 只能验证数据可构造性，不能修复 SetTraj/CoverNet + Diffusion Policy/FDP 的机制重叠，也不能自动解决 unmatched≠invalid。

若未来先重写核心机制，使可变基数、mode mass 和 physical validity 的关系被明确定义，再做上述只读/CPU compiler audit 才合理。本轮不得启动 GPU、simulator 批量采集或训练。

## 结论

Action-Fiber Set Diffusion 抓住了真实问题：标准 diffusion 的多样本能力不等于在有限采样预算下覆盖多个接触/接近 modes。同状态 rollback roster 也比普通多轨迹数据更干净。但 proposal 当前最强的算法表述——joint trajectory set、permutation-invariant matching、coverage 与 invalid mass——分别被 SetTraj、CoverNet 和多模态 diffusion policy 文献强烈预占；UOT 只是把 assignment 放松到不平衡质量，并没有让有限 roster 成为真实 feasibility oracle。

**严格 novelty = 6.90 / 10，FAIL。当前不授权 compiler E0，不启动实验。**
