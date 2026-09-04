# Post-WitnessWAM capability-changing mechanism pool

**范围**：VLA、WAM、VLA×WAM；RGB + proprio；无触觉。  
**目标痛点**：π0.5 在长时任务中丢失进度、重复动作、偏离后失败，以及 planner 主动利用 WAM 的系统误差。  
**生成约束**：以下仅做机制发散；没有文献查新、novelty 打分、筛选或排名。编号仅用于引用。每项都必须改变系统的决策空间、干预空间、优化对象或因果接口，而不只是提高同一预测器的精度。

共同的 kill-test 原则：先在小规模模拟器中使用 privileged state、真实事件标签、oracle dynamics/Jacobian 或 oracle reachability，把“表示学习是否成功”从“新能力是否有用”中剥离。若 oracle 版本都没有闭环收益，则直接终止该方向，不启动大模型训练。

## 因果干预镜头

### 1. Reversible Causal Graph Surgery（可逆因果图手术）

- **新增对象 — causal interface**：局部任务因果图上的可执行 `do` 干预，以及对图边的在线增删/定向操作。
- **能力变化**：基线只能在失败后重新出动作；该机制能主动区分“哪个可控前提失效”，并据此改变后续动作依赖关系。
- **方法（3步）**：
  1. WAM 将近期 action–effect 轨迹实例化为局部因果图，节点是当前阶段的物理关系，边表示动作可改变的依赖。
  2. 在不破坏已完成关系的可逆动作集合内，选择一次能最大区分候选边方向的微干预并执行。
  3. 用干预结果对图做 edge surgery，再从修改后的图直接合成下一段控制，而非返回原策略重试。
- **最小 oracle kill 实验**：在 30 个被人工破坏单一因果边的模拟 episode 中，用真值图和真值干预结果；若正确边定位率低于 80%，或相对普通重新规划不能把重复动作次数降低至少 30%，则 kill。
- **工程复杂度**：**高**；需要关系事件抽取、可逆动作库和局部图规划接口，但 E0 可全部使用 simulator predicate。
- **Naturalness**：**中**；主动干预与因果故障定位吻合，但图节点若过度手工化会削弱 VLA/WAM 的自然性。
- **不退化说明**：输出不是置信度或 visibility gate；干预改变了可获得的数据分布，图手术改变了后续可行计划族。

### 2. Task-Null Instrumental Perturbations（任务零空间工具变量）

- **新增对象 — intervention**：在“预期任务效果相同”的局部 action nullspace 中选择工具变量扰动。
- **能力变化**：planner 不再只能接受 WAM 给出的梯度；它能用一次物理干预识别 WAM 最容易被利用的局部误差方向，并改变搜索几何。
- **方法（3步）**：
  1. 从 WAM 的局部 effect Jacobian 求出不改变目标谓词的一组 action-nullspace 基。
  2. 选择在这些基方向上对候选动力学解释最有区分度的安全扰动，执行并读取真实 effect residual。
  3. 将 residual 转成 WAM Jacobian 的方向性修正，并把 planner 的后续优化投影出该 exploit direction。
- **最小 oracle kill 实验**：在 20 个状态上用 simulator finite difference 提供真值 Jacobian；若一次 nullspace probe 得到的误差方向与真值余弦相似度中位数不超过 0.5，或投影后 best-of-N 性能仍随 N 增大而恶化，则 kill。
- **工程复杂度**：**中**；冻结 WAM 即可做自动微分/有限差分，主要难点是安全 nullspace 与执行尺度。
- **Naturalness**：**中**；它直接针对 optimizer exploitation，但任务效果等价类必须能从 RGB/proprio 稳定定义。
- **不退化说明**：不是 per-candidate uncertainty 或 rerank；它通过真实干预估计一个误差方向，并改变 planner 的连续优化坐标。

### 3. Residual-to-Intervention Compiler（残差到补偿干预编译器）

- **新增对象 — intervention**：受保护关系约束下、由实际 effect residual 反演出的最小状态改变操作。
- **能力变化**：基线遇到偏差只能重做阶段或调用通用 recovery；该机制能针对“少发生了什么/多发生了什么”生成定量补偿，并继续原计划。
- **方法（3步）**：
  1. 将 WAM 预期 effect 与 RGB/proprio 观测 effect 的差表示为关系空间 residual，而非成功/失败标签。
  2. 通过 WAM inverse solve 找到消除 residual、同时保持已成立关系的最小补偿动作。
  3. 执行补偿，将达到的新状态接回尚未执行的计划后缀；不重置任务阶段。
- **最小 oracle kill 实验**：用真值状态与 simulator inverse dynamics，在随机注入摩擦、时延和物体位姿偏移的 30 个 episode 中；若两段 action chunk 内恢复受保护关系并继续前进的比例低于 60%，或不优于完整重规划，则 kill。
- **工程复杂度**：**高**；需要可微/可搜索的 inverse WAM 和关系约束，但无需修改 π0.5 action head 即可先做外部 controller E0。
- **Naturalness**：**高**；effect residual 天然对应控制中的补偿量，且直接处理长时执行偏差。
- **不退化说明**：它不是通用 recovery 分类器；核心输出是满足约束的连续干预，而不是一个恢复模式标签。

### 4. Deliberate Recoverability Construction（主动构造可恢复状态）

- **新增对象 — decision**：是否先执行一个“恢复性构造动作”，把当前场景变成存在低代价逆控制的物理 checkpoint。
- **能力变化**：基线只能在既定状态上判断能否恢复；该机制能在进入脆弱长后缀之前主动制造可恢复性。
- **方法（3步）**：
  1. WAM 在当前阶段预测若干未来不可逆转移及其失败后的可达集。
  2. 联合优化一个短构造动作，使关键物体/机器人进入仍保持进度、但局部逆动力学条件良好的 checkpoint。
  3. 从 checkpoint 执行主任务；若后续偏离，则使用其已合成的逆控制回到 checkpoint 再改计划。
- **最小 oracle kill 实验**：用 simulator reachability oracle 在 20 个含随机滑移/碰撞的长后缀前构造 checkpoint；若相同动作预算下，从 checkpoint 可恢复的扰动比例不高于直接执行，或构造动作导致超过 10% 的无扰动成功损失，则 kill。
- **工程复杂度**：**中到高**；E0 只需 oracle 可达性，学习版需要 WAM 预测局部逆可控性。
- **Naturalness**：**中**；机器人主动摆出可恢复构型很合理，但容易因人为 checkpoint 定义变成任务脚本。
- **不退化说明**：不是安全 gate；系统执行一个改变未来可达性的实体动作，而非只接受/拒绝原计划。

## 规划与优化对象镜头

### 5. Counterexample-Guided Plan Constraint Compilation（反例引导的计划约束编译）

- **新增对象 — optimization object**：由一次真实/模拟反例编译出的“计划族约束”，直接收缩后续搜索空间。
- **能力变化**：普通 replan 可能反复生成同构失败计划；该机制能证明并永久排除导致同一失败的整族计划。
- **方法（3步）**：
  1. VLA 将计划表示成带 action realization 的事件程序，WAM 明确每个事件转移依赖的 postcondition。
  2. 在 rollout 或真实执行中找到最早被反例否定的转移，并提取使该反例成立的最小因果条件。
  3. 把条件编译成 hard constraint，重新求解一个不属于该失败等价类的计划，而非在有限候选中换最高分者。
- **最小 oracle kill 实验**：给定真值事件程序和 simulator 反例，在 20 个可产生同构重试的任务实例中；若 plan-family constraint 不能把相同失败复发率降低至少 50%，或误删超过 10% 的真值可行计划，则 kill。
- **工程复杂度**：**中**；需要事件程序和约束求解器，但可先以 simulator predicate + 冻结 π0.5 作为 action realizer。
- **Naturalness**：**高**；反例本来就应改变 planner 的可行域，而不是只给 WAM 再加一个分数。
- **不退化说明**：保存的是可执行约束而非普通 episodic memory；它对所有未来计划施加结构性限制，也不是 candidate rerank。

### 6. Observation-Contingent Action Trees（观测条件动作树）

- **新增对象 — decision**：一个共享前缀、事件条件分支和分支后缀组成的短 horizon policy tree，替代单一 action chunk。
- **能力变化**：π0.5 不必等整段动作执行完再被动重规划；它能在 chunk 内依据物理结果走不同控制分支。
- **方法（3步）**：
  1. VLA 生成一个公共动作前缀，以及按可观测 causal event 分区的 2–3 个后缀。
  2. WAM 联合展开整棵树，在共享扰动下优化分支覆盖与最终任务效果，而非给若干独立 chunk 打分。
  3. 执行公共前缀，事件一发生即绑定相应分支并继续；未覆盖事件进入显式补偿叶节点。
- **最小 oracle kill 实验**：使用 oracle 事件标签，在具有随机接触时延/抓取结果的 30 个 episode 中，将深度 2 树与等动作预算、每 5 步 replanning 的单序列基线比较；若成功率和重复动作均无改善，则 kill。
- **工程复杂度**：**高**；需要树形解码/批量 WAM rollout 和中段分支执行接口，但深度 2 的 E0 可以模板化树结构。
- **Naturalness**：**高**；多结果接触动作本来就是 contingent control 问题，单开环 chunk 才是能力瓶颈。
- **不退化说明**：事件不是置信度 gate；它选择树中不同控制律，决策对象从 sequence 变成 closed-loop contingent policy。

### 7. Effect-Equivalence Quotient Planning（效果等价类商空间规划）

- **新增对象 — optimization object**：由有序 causal-effect trace 定义的 action-sequence 等价类，以及可在线 split/merge 的商空间。
- **能力变化**：planner 能分辨“动作看起来不同但依赖同一错误 WAM 机制”的冗余搜索，并把预算用于真正不同的物理策略。
- **方法（3步）**：
  1. WAM 把短 action sequence 映射为有序 effect signature，而非只给最终 progress scalar。
  2. planner 在 effect-class 图上搜索，每类只保留一个可实现代表；实际 effect 与类定义冲突时立即 split 该类。
  3. π0.5 作为 inverse realizer，把选定 effect transition 解码成当前几何下的具体动作。
- **最小 oracle kill 实验**：用 simulator 真值 effect signature，在固定 64 次模型查询下比较 raw-action search 与 quotient search；若后者不能提高独特可达 effect 数量，或不能降低因同一 WAM 错误导致的重复失败，则 kill。
- **工程复杂度**：**高**；需要 effect abstraction、动态聚类和 inverse realization；oracle signature 可显著压低 E0 成本。
- **Naturalness**：**中**；从结果空间规划契合任务语义，但等价关系若不稳定会退化为另一套离散标签。
- **不退化说明**：它没有对普通候选重新打分；搜索变量、邻接关系和预算分配都从 action 空间改成 effect-class 空间。

### 8. Joint Progress–Compensation Planning（进展—补偿联合规划）

- **新增对象 — optimization object**：主任务轨迹与从每个承诺边界出发的补偿策略所组成的联合解。
- **能力变化**：planner 不再先选看似最优的动作、失败后才想恢复；它能选择“会前进且可补偿”的动作，即使其名义 progress 略低。
- **方法（3步）**：
  1. 对每个尚未执行的不可逆边界，同时生成 forward suffix 与将常见 residual 拉回可继续状态的 compensator。
  2. WAM 在共享扰动下联合优化二者，使 forward 末态推进任务、compensator 末态能重接计划，而不是分别打分。
  3. 执行 forward；出现已建模 residual 时直接进入对应 compensator，再从其重接点续行。
- **最小 oracle kill 实验**：用真值 dynamics/reachability 合成 compensator，在 30 个注入滑移、欠执行和误抓的 episode 中；若相同总动作预算下不优于“名义最优 plan + 失败后完整 replan”，则 kill。
- **工程复杂度**：**高**；联合 rollout 数量增加，但可冻结 π0.5/WAM，以有限 compensator horizon 做 E0。
- **Naturalness**：**高**；恢复能力应在动作承诺时被共同设计，而不是事后外挂。
- **不退化说明**：核心不是 residual gate 或 backup candidate；优化变量本身就是 forward/compensation policy pair。

### 9. Sparse Causal-Dynamics Minimax Planning（稀疏因果动力学极小极大规划）

- **新增对象 — optimization object**：与近期真实转移一致、但允许少量因果机制发生结构变化的 dynamics adversary。
- **能力变化**：当 planner 找到 WAM 的漏洞时，系统能规划对“哪条因果规则错了”不敏感的轨迹，而不是只缩小搜索预算或降低置信度。
- **方法（3步）**：
  1. 将 WAM rollout 分解为少量可干预的 effect mechanisms，并以近期 action–effect 观测约束允许的稀疏机制修改。
  2. 内层 adversary 寻找最小机制修改，使候选计划的预测进展失效；外层 planner 优化在该修改下仍能推进的轨迹。
  3. 新的真实转移继续收缩可行机制修改集，使 robust plan 随执行逐步减少保守性。
- **最小 oracle kill 实验**：在 simulator 中只改变一个已知动力学机制（如摩擦、夹爪闭合延迟或物体约束）；若 oracle 稀疏 adversary 仍不能捕获真实变化，或不能阻止 best-of-N 随 N 增大而退化，则 kill。
- **工程复杂度**：**高**；需要结构化 WAM 接口和双层优化，但 E0 可用手工三类机制参数代替学习 adversary。
- **Naturalness**：**高**；planner exploitation 本质上是对模型机制错误的优化，直接把该错误放进对抗规划对象比全局不确定性更贴题。
- **不退化说明**：不是 ensemble confidence、conformal bound 或 LCB rerank；它产生一条对反事实动力学修改鲁棒的新轨迹。

## 执行语义与在线控制镜头

### 10. Event-Surface Action Semantics（事件曲面动作语义）

- **新增对象 — causal interface**：由闭环控制场、物理终止事件曲面和超时逃逸组成的 action primitive，替代固定长度 chunk。
- **能力变化**：同一个高层动作能随接触时延和执行速度自适应持续时间，避免欠执行后重复或过执行后破坏进度。
- **方法（3步）**：
  1. π0.5 的短动作被实例化为可逐步重条件化的控制场，同时指定一个 RGB/proprio 可判定的目标 effect surface。
  2. 执行器在 surface 到达前持续调整动作时间尺度和幅度；只有达到事件或触发超时逃逸才终止 primitive。
  3. 达到的 event surface 成为下一个 primitive 的精确起始接口，而不是由固定 5-step 边界隐式猜测进度。
- **最小 oracle kill 实验**：先用 simulator 真值 event detector，仅把固定 chunk 改成 oracle event termination；在 30 个随机时间缩放/接触延迟 episode 中，若 overshoot、欠执行和重复动作合计不下降至少 30%，则 kill。
- **工程复杂度**：**中**；E0 不需训练新 WAM，主要改 receding-horizon 执行接口；学习 event surface 后复杂度上升。
- **Naturalness**：**高**；机器人动作的物理完成天然由事件而非固定 token 数定义。
- **不退化说明**：event surface 不是 visibility/confidence gate；它重定义了动作的持续时间、反馈律和阶段交接语义。

### 11. Online Action-Patch Algebra（在线动作补丁代数）

- **新增对象 — intervention**：作用于“尚未执行的 action suffix”的组合补丁，如时间伸缩、增益修正、局部坐标偏移和接触次序修补。
- **能力变化**：基线只能取消整段动作并从头生成；该机制能在毫秒级局部改写正在执行的 chunk，保留已完成部分并修正剩余部分。
- **方法（3步）**：
  1. WAM 计算已执行前缀的预期 effect 与真实 effect 之间的连续 residual，并估计 residual 对补丁基的局部 Jacobian。
  2. 在保持已满足关系的约束下，求解最小补丁系数，对未执行 suffix 做组合变换。
  3. 立即执行 patched suffix，并用其真实效果更新局部 patch Jacobian；无需重新采样完整 action chunk。
- **最小 oracle kill 实验**：使用真值 residual 和 simulator finite-difference Jacobian，在注入执行时延、尺度误差与小位姿偏差的 30 个 episode 中；若 oracle patch 在相同控制延迟下不优于“取消 + π0.5 重新规划”，则 kill。
- **工程复杂度**：**中到高**；补丁基可先手工定义，难点是 π0.5 action normalization 与执行器坐标的一致变换。
- **Naturalness**：**高**；执行误差常是原动作的局部变形，修补 suffix 比重启整段控制更符合系统结构。
- **不退化说明**：不是辅助 loss、候选 rerank 或通用 recovery；模型输出一个直接作用于当前控制信号的可组合变换。

## 机械去重说明

三个镜头分别围绕“获得新的因果证据并改变模型结构”“改变 planner 的搜索变量/可行域”“改变动作执行语义”展开。去重只按核心能力对象进行：图手术、误差方向、补偿干预、可恢复状态、计划族约束、条件动作树、effect 商空间、forward–compensator 联合解、因果动力学 adversary、事件动作、suffix patch 互不等价，因此保留 11 项。未进行质量淘汰或隐式排序。
