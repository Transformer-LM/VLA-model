# WitnessWAM v4 第 5 轮最终严格复审

**评审角色：** research-refine senior reviewer  
**日期：** 2026-08-31  
**CALIBRATION:** none  
**Verdict:** **REVISE**

## 最终结论

Round 5 已修复两个实质 blocker：continuation envelope 现在只依赖 checkpoint EEF proprio、固定 skill retreat axis 和 queued denormalized commands，真正满足部署可检查性；capacity-matched full-history boundary verifier 也以最强合理形式加入，能够决定 explicit witness-time modeling 是否不可约。

仍有 **一个 reading-robust blocker**：lineage×key denominator 在文档内部定义矛盾。Section 1 说 pre-prefix denominator 只包含通过 paired agreement、safety 与 command envelope 的 attempts；Section 3 又说四个 attempts 全部留在 preservation/opportunity denominators；Gate 3/4 再写成所有 lineage-key attempts。无效、unsafe 或 envelope-failing key究竟是被排除、记 missing，还是作为 preservation/opportunity failure，当前无法唯一计算。

因此 proposal 质量已超过 9，但按照“overall ≥9 且无 blocker才 READY”的规则，本轮仍判 **REVISE**。只需统一一个 denominator 定义，不需要再改机制或扩展实验。

## 同一七维评分

| 维度 | 分数 /10 | 判断 |
|---|---:|---|
| Problem | **9.6** | 直接解决遮挡/别名阶段的错误 progress-memory 更新。 |
| Novel mechanism | **9.1** | Passive opportunity hazard相对visibility与buffered-history两条更小解释均有决定性kill gate。 |
| Causal identifiability | **9.5** | Immutable chunk、staged belief、boundary atomic apply与truth-transition accounting使轨迹和endpoint可归因。 |
| Data producer | **8.8** | Producer与audit完整；唯一缺口是attempt/contract denominator冲突。 |
| Implementability | **9.3** | Envelope、π0.5 keys、physical commands、RGB+proprio接口均可实现。 |
| Evaluation | **9.0** | Single IBS、paired lineage bootstrap、两个决定性小基线都正确；denominator必须先唯一化。 |
| Claim honesty | **9.7** | Claim ceiling、stop conditions与失败后的收缩路线均明确。 |

**OVERALL SCORE: 9.3 / 10**（七维等权）  
**Verdict: REVISE**（分数过线，但尚有一个定义 blocker）

## 三项最终核验

### 1. Command-only checkpoint-EEF retreat envelope

**通过。** Envelope 不再读取 body pose、segmentation、depth、PointMap、simulator geometry、future truth 或 learned eligibility。Initial EEF pose来自 proprio；retreat axis是数据收集前冻结的 skill/controller parameter；五步 denormalized clipped commands可在 rollout 前积分并检查单调投影、reversal、横向/旋转/速度界、gripper mode和额外 actuator变化。

它不能形式保证物理 predicate preservation，但 proposal 没有做此过度主张，而是对完整 contract population进行 privileged per-step audit，并要求每 family ≥95%。Truth transition计为 violation/system failure。该组合是 deployment-valid contract + honest simulator precision audit，不再存在 privileged future selection。

固定 retreat axis可能降低某 family 的自然 yield，但这是 E0 falsification risk，不是 proposal blocker。

### 2. Lineage×key denominator 与 lineage bootstrap

**Bootstrap通过；denominator尚未通过。** Parent lineage是唯一重采样和split单位，四 keys绝不当作独立样本，这一点清楚正确。

但以下三句话不兼容：

1. Section 1：pre-prefix denominator只含“pass agreement, safety, command-only envelope”的lineage-key attempts；
2. Section 3：“All four attempts remain in preservation and opportunity denominators”；
3. Gate 3/4：“over all lineage-key attempts”。

例如第四个key若paired action disagreement或unsafe，就无法按同一物理intervention产生有效`t​​au_protocol`；将它计入opportunity denominator需要明确赋值为failure，而排除它则与“All four”冲突。该选择会直接改变95% preservation与25% opportunity gates，不能留给实现者解释。

### 3. Capacity-matched full-history boundary verifier

**通过，且足以检验 timing irreducibility。** 它获得完整五步RGB/proprio/action trace、相同query、encoder capacity、temporal-token/evidence budget、augmentation、tuning和training lineages；没有`t​​au_protocol`或privileged geometry；在自然boundary一次输出belief。它能利用任何transient witness，因此不会因只看final frame而被人为削弱。

WitnessWAM与它在相同physical chunk、同coverage、同boundary FSM endpoint比较，并需每 retained family达到≥10% total-error improvement且paired lineage-bootstrap CI排除零。若失败，proposal明确收缩为buffered temporal verification。这一baseline公平、强且决定性；无需再加其他机制对照。

## 唯一剩余 reading-robust blocker

### Q1. Attempt denominator 与 contract denominator未唯一化（CRITICAL but local）

当前无法唯一计算preservation/opportunity gates。最小修复是明确两个集合并全篇统一：

- `D_attempt`：每个physical parent的四个fixed-key attempts，全部进入ledger，无replacement，用于报告contract coverage与missing/unsafe/agreement失败；
- `D_contract`：`D_attempt`中通过paired agreement、safety与command-only envelope的lineage-key attempts。Truth transitions保留在此集合并作为preservation、opportunity和system failure；`tau_protocol`只在truth-preserving members上形成监督。

Gate 3和4应明确以`D_contract`为分母；另报告`|D_contract| / |D_attempt|`，避免一个极窄envelope被隐藏。K-prefix分析仍要求一个parent至少3/4 keys属于`D_contract`。所有CI继续按parent lineage paired bootstrap。

如果作者坚持所有四keys都作为Gate 3/4分母，也可以，但必须预注册invalid/unsafe/non-envelope attempt的确定failure编码；不能同时使用Section 1的conditional denominator。二者只能选一个。前述双集合定义更自然。

## 最小局部修复

仅统一Section 1、Section 3、Gate 3/4中的`D_attempt`与`D_contract`定义，并给contract coverage一个固定报告/门槛。除此之外不建议任何方法、模型、family、horizon或baseline扩展。

## Drift warning

**NONE.** 方法仍是单一的passive witness scheduling贡献。

## Simplification / Modernization

**NONE.** 当前结构已是最小充分方案。

