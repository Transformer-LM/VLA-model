# P028 严格评审

- review independence: same-family
- acceptance status: provisional
- verdict: **RETHINK**
- overall score: **5.4/10**
- calibration: none

| 维度 | 分数 | 判断 |
|---|---:|---|
| Problem Fidelity | 9 | 问题锚点准确，且诚实承认 P027C 阴性结果。 |
| Method Specificity | 5 | 关键监督、likelihood、critic 来源与可信 explanation set 未闭合。 |
| Contribution Quality | 4 | 核心基本是 value equivalence、robust decision、task-optimal system ID 与 active diagnosis 的 WAM 应用组合。 |
| Frontier Leverage | 6 | VLA top-K/WAM rollout 接口及时，但未形成新的 WAM-specific 机制。 |
| Feasibility | 4 | learned WAM 前提未成立；候选反事实监督、probe observation model 与 task preservation 代价高。 |
| Validation Focus | 6 | 有 gate，但决定去留的零训练测试还不够前置。 |
| Venue Readiness | 4 | 方法身份与普通有效性均有阻塞。 |

## 核心结论

当前 `ranking invariant over explanations` 属于有限候选集上的 value/policy-order equivalence；“只辨识影响当前任务的因素”与 task-optimal exploration 重叠；`I(z;o|p)-cost` 是标准 POMDP/active diagnosis。当前 proposal 没有给出超出这些原语的 WAM-specific operator。

最可能成立的新对象不是 active-identification 方法，而是：

> 在 matched factual residual 下，不同隐藏机制导致 frozen VLA candidate ranking reversal 的严格 witness。

然而当前把它放成 supporting compiler，却把高度拥挤的 POMDP loop 作为 dominant contribution，主次颠倒。

## 结构性监督缺口

- actuation、contact、support、container、perception 等原因并不互斥，单 factor-label CE 会错误类别化。
- matched-residual twins 要求同一可观测输入保留多个解释，这与单 simulator factor label 的 CE 冲突。
- `g(r,a^k,z)` 需要每个候选动作在每个 latent cause 下的 counterfactual future；真实日志不提供这种监督。
- frozen critic/progress head 的来源、分布和可靠性未定义。
- probe mutual information 需要 `p(o_{t+1}|z,p)`；若复用待诊断 WAM，会形成自我诊断循环。
- proposal 中的 expected regret 不是所声称的 robust regret，也不等价于全部可信解释下 ranking invariant。

## 当前实验前提

- `P027C_LOSO_6A79_WAM_E0` action-swap margin 为负，action-conditioning gate 失败。
- `P027C_LOSO_7D82_CALIBRATED_E0` ordinary calibration improvement 仅 0.045%，低于 1% gate。
- 另一 heldout source 上，calibrated transport 同时伤害 ordinary controls 与 alias，不支持 candidate-ranking/router claim。

因此当前 checkpoint 的 `Q_k(z)` 没资格承担 ranking-identifiability 判定；factor posterior 也不能修复一个不看动作或在 ordinary controls 上无有用反馈收益的 WAM。

## 建议的最小重构

若未来重新进入该路线，应删除显式 cause posterior 和 correction adapter，改成一个直接的 set-valued decision head：

\[
(h_t,r_t,a^{1:K})\rightarrow
\{\text{plausible pairwise rankings / regret intervals}\}.
\]

dominant contribution 只能限定为：

> matched-residual 条件下的 calibrated candidate-ranking set，用于判断 WAM feedback 是否具有决策可迁移性。

probe 只能作为引用既有 Bayesian decision/active-diagnosis 的 fallback，不应作为 novelty。

## 仅授权的 kill-only prerequisite audit

不授权 proposal 中的训练型 E0；只授权零训练、kill-only audit：

1. ordinary action grounding：matched action 必须显著优于 action-shuffled，且 source-stratified ordinary feedback 相对 no-feedback 有正收益；
2. residual-alias prevalence：block-disjoint twins 中真实 candidate-ranking reversal 比例需不低于约 10%，且不能依赖人工筛选；
3. oracle headroom：wrong intervention 至少下降 25%，ordinary useful correction 至少保留 90%，且不能被 scalar uncertainty/direct scorer 等效达到；
4. probe 仅作附加 oracle check；generic MI 若等效，则删除 probe novelty。

若没有现成 WAM 能通过 Gate 0，应立即停止当前方向，不训练 Router、`q(z)`、adapter 或闭环系统。

