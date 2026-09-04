# 实验计划：类内功能几何条件下的 VLA × WAM 反事实动作验证

**问题**：同一语义类别中的功能几何变化会使 VLA 的常用动作失效；动作条件的对象相对几何 WAM 能否在运行时识别并选择更合适的动作？  
**方法主张**：冻结或轻量适配 π0.5，用目标物—参照物 PointMap 构成任务相关几何状态；对 π0.5 的候选 action chunks 进行短时动作条件几何 rollout，并据此选择、修正或拒绝动作。  
**日期**：2026-08-30

## Claim Map

| Claim | 为什么重要 | 最低可信证据 | 对应实验块 |
|---|---|---|---|
| C1：类内功能几何 OOD 中存在可利用的 action-selection gap | 先证明失败不是“候选中根本没有正确动作” | Oracle rollout 重排序在配对初始状态上比 π0.5 top-1 提升至少 10 个成功率百分点，并明显优于仅提供 Oracle 终点位姿 | B1 |
| C2：学习到的动作条件几何 WAM 能回收该 gap，且作用不等价于更多 3D 输入或直接 success scorer | 证明 WAM 是必要机制，而非装饰性辅助任务 | 相同数据、候选集合和计算预算下，WAM 至少回收 30% Oracle gap，并比最强直接 PointMap-VLA/直接 scorer 提升至少 5 个百分点；动作打乱会显著破坏排序 | B2、B3、B4 |

**必须排除的反解释**：收益只来自更多参数、更多候选、Oracle/特权几何、最终位姿提示、额外数据，或者一个不做 rollout 的直接成功分类器。

## 论文故事线

- 主文必须证明：功能几何受控 split 上存在 C1；WAM 在运行时的动作条件预测改善真实/仿真闭环决策；收益超过直接 PointMap 输入和直接 action scorer。
- 附录支持：候选数、rollout horizon、不确定性、更多形状因子、延迟和失败案例。
- 暂时砍掉：完整 RGB-D 视频扩散、联合训练大型 VLA、长期记忆、自动恢复策略、触觉、多轮 policy–WAM 共演化。它们会模糊第一篇论文的核心因果链。

## Route Card

```yaml
representation: R3/R4 task-centric latent plus explicit object-relative geometry
control_use: U3 candidate-action evaluation; optional short-horizon U4 replanning
observations: [RGB-D, target/reference masks or addresses, proprioception, language]
prediction_targets: [relative object pose, sparse point motion, clearance, collision/contact predicates, task relation, uncertainty]
action_interface: action-conditioned chunk
rollout_horizon: one action chunk initially
policy: frozen pi0.5 candidate generator
world_model_update: frozen after offline training for the first paper
data_regime: mixed simulation/real trajectories, with personal-only storage
primary_claim: runtime counterfactual geometry prediction improves intra-category functional-geometry OOD action selection
main_failure_mode: candidate coverage failure or WAM extrapolation to policy-generated actions
```

## 数据与 split 设计

### 任务族

首个 pilot 只选择一个能稳定重置、能产生几何约束差异的任务族；最终至少覆盖三个机制不同的任务族：

1. `insert/inside`：不同物体宽度、长度、把手位置；不同开口尺寸、深度、倾角；
2. `hang/attach`：不同孔洞/把手几何与挂钩方向；
3. `constrained-place/transport`：相同终点但障碍间隙、物体外形要求不同接近方向或中间旋转。

### 类内功能几何 split

- 语义类别、语言指令和目标关系保持不变；
- 每个几何因子值在训练中单独出现；
- 测试保留未见实例和未见有序目标物—参照物组合；
- 建立 `terminal-matched` 子集：最终目标位姿相同，但正确路径/抓取/阶段不同；
- 建立负对照：颜色、纹理、背景变化，但正确动作不应改变；
- 建立不可行子集：目标关系在当前几何下无法建立，测试正确拒绝而非强行执行；
- 所有 CAD、几何参数、实例 ID、split 与采集版本进入不可变 manifest，禁止按测试结果移动实例。

## 实验块

### B0：接口、候选多样性和数据审计

- **Claim tested**：尚不测试论文 claim；验证接口与测试问题真实存在。
- **为什么存在**：若 π0.5 不能产生多样候选，重排序问题从一开始就不成立。
- **任务**：单一 pilot 任务族；少量训练内和类内 OOD 几何。
- **系统**：π0.5 固定 top-1；不同采样随机性/温度产生 K 个 action chunks；必要时使用受约束的小扰动作为独立候选来源并单列报告。
- **指标**：候选动作方差、top-k 环境成功覆盖率、重复候选率、动作合法率、推理延迟。
- **成功条件**：OOD 失败状态中，top-k 候选至少在一部分样本含有可成功动作；候选不是数值重复。
- **失败解释**：若候选覆盖为零，停止 WAM reranking，转向几何条件 action generation/residual policy。
- **优先级**：MUST-RUN。

### B1：Oracle gap 与终点位姿排除实验

- **Claim tested**：C1。
- **为什么存在**：在训练 WAM 前判定未来后果信息是否真的能改善动作选择。
- **任务/split**：pilot 任务；配对初始状态；重点报告 terminal-matched 和不可行子集。
- **比较系统**：
  1. π0.5 top-1；
  2. K 候选随机选取；
  3. Oracle 最终 6D pose/终态关系评分；
  4. Oracle 完整环境 rollout 排序；
  5. Oracle 几何约束评分（碰撞、间隙、接触、关系）。
- **主要指标**：闭环成功率；次要指标为 top-k coverage、top-k regret、碰撞/卡死/错抓/未对准分解、拒绝准确率。
- **成功条件**：完整 Oracle 比 top-1 至少 +10pp；且相对于 Oracle 终点位姿仍保留清晰增益，证明不是单纯 pose estimation。
- **失败解释**：
  - 完整 Oracle 无增益：重排序路线停止；
  - 终点位姿解释绝大多数增益：转向 relation-pose/placement；
  - 候选覆盖不足：转向 action generator；
  - Oracle 轨迹也失败：转向控制/状态估计。
- **图表**：主文 Figure 1（问题存在性）和 Table 1（Oracle ladder）。
- **优先级**：MUST-RUN，训练任何正式 WAM 前的硬门。

### B2：学习到的动作条件 PointMap WAM

- **Claim tested**：C2 的预测和决策部分。
- **模型**：
  - 目标物和参照物 PointMap 分别编码；统一到参照物坐标系；
  - 输入当前几何 latent、proprio 和候选 action chunk；
  - 多步预测相对位姿、任务关键稀疏点运动、signed clearance、碰撞/contact/关系概率；
  - 使用 ensemble 或 distributional head 输出不确定性；
  - 不解码完整 RGB/Depth 视频。
- **比较系统**：
  1. RGB-only latent WAM；
  2. Depth/全局 PointMap WAM；
  3. 对象相对 PointMap WAM；
  4. Oracle geometry upper bound。
- **指标**：候选两两排序准确率、Spearman、top-k regret、按 horizon 的状态/关系误差、Brier/ECE、risk-coverage、动作打乱敏感性。
- **成功条件**：对象相对版本在 OOD 几何和 policy-generated actions 上提高排序并保持校准；动作打乱/跨候选置换明显破坏预测。
- **失败解释**：只降低几何 RMSE 但不改善排序，不支持 C2。
- **图表**：主文 Table 2 和 calibration/ranking figure。
- **优先级**：MUST-RUN。

### B3：WAM 必要性与最强简单基线

- **Claim tested**：C2 的机制隔离。
- **比较系统**：
  1. frozen π0.5；
  2. π0.5 + 当前 PointMap adapter；
  3. π0.5 + training-only future-geometry auxiliary objective；
  4. 直接 action scorer：`score(current PointMaps, candidate action)`，参数/数据匹配但不预测未来状态；
  5. 提议的 action-conditioned geometry WAM；
  6. WAM + shuffled action、zero action、去掉参照物、去掉对象相对坐标。
- **固定因素**：同一候选集合、同一训练轨迹、同一 action horizon、相近参数量、相同训练步数和评估初始状态。
- **主要指标**：闭环成功率；次要指标为 Oracle-gap recovery、碰撞率、错误拒绝率、延迟。
- **成功条件**：WAM 比最强简单基线至少 +5pp 且回收至少 30% Oracle gap；动作条件和对象相对表示的删除会同时损害预测与闭环选择。
- **失败解释**：
  - 直接 scorer 持平：完整 dynamics/WAM 没有必要；
  - PointMap adapter 持平：运行时 rollout 没有必要；
  - shuffled-action 不下降：模型没有学到可控动力学。
- **图表**：主文主结果 Table 3。
- **优先级**：MUST-RUN。

### B4：跨任务族、闭环重规划与真实机器人

- **Claim tested**：C2 的环境层泛化。
- **设置**：固定模型和阈值，扩展至至少三个任务族；每次 action chunk 后用真实观察重置 WAM latent；真实机器人先进行速度/工作空间/碰撞安全审查。
- **指标**：每任务成功率与置信区间、failure taxonomy、拒绝/停滞率、控制频率、GPU显存与延迟。
- **成功条件**：效果不只来自单一插入场景；至少两个不同失败机制的任务族保持方向一致，并有真实机器人支持。
- **失败解释**：若只在一个任务族有效，论文 claim 降级为 task-local，不宣称通用类内几何泛化。
- **图表**：主文 Table 4、失败案例图；更多任务进入附录。
- **优先级**：Oracle 与 pilot 通过后 MUST-RUN。

### B5：失败分析与 WAM exploitation audit

- **Claim tested**：可靠性边界，不新增主 claim。
- **内容**：找出 imagined-success 高、环境-success 低的动作；按接触、遮挡、反光/透明、薄结构、长 horizon、候选 OOD 聚类；检查不确定性是否能拒绝。
- **指标**：imagined–real gap、tail exploitation、risk-coverage、错误接受/错误拒绝。
- **优先级**：主结果通过后 MUST-RUN；更多定性视频 NICE-TO-HAVE。

## Run Order and Milestones

| Milestone | 目标 | Runs | Decision Gate | 预计成本 | 风险 |
|---|---|---|---|---|---|
| M0 | 数据、动作、坐标和候选接口正确 | B0 toy overfit、候选多样性、split audit | 候选合法且存在非零 top-k 成功覆盖 | 0.5–1 A100-day + 环境采集 | π0.5候选过于集中 |
| M1 | 判定研究缺口是否真实 | B1 Oracle ladder | 完整 Oracle ≥ top-1 +10pp，且不被终点位姿解释 | 主要为环境 rollout，约1–3天 | reset/成功标签不可靠 |
| M2 | 训练最小几何 WAM | B2 单任务、单 seed、短 horizon | 排序优于 RGB/全局几何，动作置换下降 | 4–12 A100-h 起步 | policy action OOD |
| M3 | 证明 WAM 必要性 | B3 三 seeds、匹配 baselines | ≥5pp 且 ≥30% Oracle-gap recovery | 约24–60 A100-h | direct scorer 持平 |
| M4 | 跨任务与真实机器人 | B4 固定配置、多任务、实机 | 至少两个任务族方向一致 | 约60–120 A100-h + 实机试验 | sim-to-real、重置成本 |
| M5 | 可靠性收尾 | B5 stress/exploitation | 明确可校准的使用边界 | 视 stress 数量而定 | WAM盲区被planner利用 |

## 第一批三项运行

1. `R001`：冻结 π0.5，在一个功能几何任务族上生成 K 候选，测候选多样性与 top-k 成功覆盖。
2. `R002`：相同初始状态运行 top-1、Oracle终点位姿、Oracle完整rollout，计算 Oracle gap。
3. `R003`：建立 terminal-matched 对照，确认同一终点下不同几何确实要求不同路径/抓取/阶段。

这三项完成前，不训练完整 WAM。

## 计算和数据预算

- **GPU**：可使用 4×A100；M0–M2 初期只需 1–2 卡，M3/M4 再按 seed 并行使用 2/3 卡；仅在确认 0/1 空闲时使用全部四卡。
- **数据**：需要包含失败和非最优候选结果，不能只用专家成功轨迹；每条 transition 记录 RGB-D、对象实例与 mask/address、proprio、实际 action、后续几何/关系和成功标签。
- **存储与服务器边界**：所有项目、缓存、数据、checkpoint 和日志仅位于 `<PERSONAL_RESEARCH_ROOT>`，仅使用 `liu_meng`，不使用 root/sudo/su，不修改 `.bashrc`、系统 CUDA、全局 Conda 或共享目录。
- **最大瓶颈**：不是GPU，而是可靠的对象/参照物 PointMap、可重复环境 reset、候选动作 ground-truth rollout，以及严格无泄漏的几何 split。

## 风险与缓解

- **候选没有正确动作**：先做 top-k coverage；失败即转 action generation，不训练 reranker。
- **任务太宽松**：优先选择相同终点但路径/抓取确实不同的 terminal-matched 样本。
- **WAM退化为success classifier**：加入参数匹配 direct scorer，并要求中间几何预测和动作因果控制共同通过。
- **WAM利用伪相关**：对象相对坐标、颜色/纹理负对照、实例与组合双重 held-out。
- **WAM对policy动作分布外**：训练集混入 π0.5 候选和受控失败动作，单独评估 behavior-policy 与 policy-generated action 分布。
- **PointMap感知错误**：加入 Oracle PointMap 与估计 PointMap 交叉实验，区分感知和动力学瓶颈。
- **规划利用WAM漏洞**：限制短 horizon、ensemble不确定性惩罚、真实观察重置，并报告 imagined–real tail gap。

## Final Checklist

- [x] 主 claim 不超过两个
- [x] Oracle gate 在正式训练前
- [x] 包含直接 PointMap-VLA 与直接 scorer 强基线
- [x] 区分预测、排序、闭环和真实环境证据
- [x] 包含动作因果控制与 WAM exploitation audit
- [x] MUST-RUN 与 NICE-TO-HAVE 已分离
- [x] 服务器个人目录与 GPU 约束已继承

