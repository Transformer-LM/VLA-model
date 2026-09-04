# 对象级 WAM × 几何/4D WAM：空白区与候选 Idea

时间：2026-08-25  
阶段：Idea discovery / novelty triage；未启动训练或服务器任务。

## 结论先行

可以结合，但不能把贡献写成“把对象 slot 与 3D/4D 特征拼起来”。OA-WAM 已覆盖持久对象地址、对象内容与 9D pose；MRO-GWM/ORD-WM 已覆盖对象中心、动作条件的 3D 刚体动力学；PointAction、WSA1 又覆盖了 3D 世界—动作接口。因此，宽泛组合的新颖性不足。

目前最可守的交叉空白是：

> **语言可寻址、动作条件、可反事实的稀疏对象几何状态。** 固定语义地址回答“是谁”，SE(3)-等变几何状态回答“在哪里”，动作条件动力学回答“执行候选动作后它会怎样变化”；最后用语言指定的对象关系评价 π0.5 候选动作，而不是生成好看的未来视频。

暂名 **ACG-WAM (Addressable Counterfactual Geometry WAM)**。

## 为什么不是简单相加

| 已有工作 | 已覆盖部分 | 尚未充分打通的接口 |
|---|---|---|
| OA-WAM | persistent address/content、对象 pose、next-slot auxiliary prediction、联合动作头 | world-side prediction 不是由未来候选 action chunk 驱动的多步反事实 rollout |
| MRO-GWM | object-centric Gaussian、未来动作条件、3D 刚体多步动力学、MPC | 假设对象分解/位姿较强，缺语言指代到持久对象地址的 VLA 绑定 |
| ORD-WM（预印本/项目） | 对象点云、SE(3)增量、解析几何变换、动作条件多步 rollout | 语言地址、身份—几何独立干预、VLA 候选动作绑定仍不是核心 |
| PointAction | RGB + 动态 3D pointmap，作为跨本体动作接口 | 不是显式持久对象地址与逐对象因果归因 |
| WSA1 | 统一语义、3D world modeling 与 action generation | 规模大；“哪个对象—哪段候选动作—哪种关系效果”的因果可寻址性并非其主要可验证命题 |
| WAM4D / X-WAM / GWM | 几何监督、多视角 RGB-D、Gaussian 世界预测 | 不等于语言指代下的逐对象反事实动作评价 |

## 主候选：ACG-WAM

### 表示

对每个对象维护：

\[
s_i^t=[q_i\;\|\;g_i^t\;\|\;c_i^t],
\]

其中 `q_i` 是跨时间稳定的语义地址；`g_i^t` 是世界坐标或对象坐标中的 pose、稀疏形状和速度；`c_i^t` 是接触/抓持/支撑等关系状态。地址在相机变化或对象运动时保持不变，几何状态按 SE(3) 变换。

π0.5 先产生 K 个 action chunks。WAM 对每个候选动作分别预测：

\[
p(g_{1:N}^{t+1:t+H},r^{t+1:t+H}\mid s^t,a_k,\ell).
\]

语言任务只查询目标对象与参照对象的未来关系，例如 `inside(red-cup, green-tray)`、`grasped(cup)`、`clearance(gripper, obstacle)`，从而给候选动作排序或拒绝明显错误的动作。

### 真正的贡献必须是可检验的因果分解

1. **地址交换试验**：几何完全不变，只交换红杯/蓝杯地址。物理 rollout 不应乱变，但语言任务评分和被选动作应随目标地址交换。
2. **几何变换试验**：地址不变，对场景施加已知 SE(3) 变换。预测轨迹和动作应等变，身份不能改变。
3. **动作干预试验**：当前观测完全相同，只换候选 action chunk。受作用对象的未来几何必须对应改变，未作用对象不应出现虚假运动。
4. **共运动负控制**：分别构造移动相机、移动承载托盘、直接推杯子，检查模型能否区分相机运动、间接运动和直接动作效果。

### 最小可行实验

先不要端到端训练大模型。使用仿真 oracle object ID/pose，冻结 π0.5：

1. 每个状态由 π0.5 采样 K=4/8/16 个 action chunks；
2. 收集每个候选在 ground-truth simulator 中的真实短时对象轨迹与任务进展；
3. 比较全局 latent WAM、无地址对象几何 WAM、ACG-WAM、直接 discriminative scorer、oracle simulator；
4. 在 object swap、layout shift、camera shift、同类干扰物下测试候选 pairwise ranking、top-1 regret 和闭环成功率。

若 oracle 对象状态版本都不能改善动作排序，就没有理由投入 SAM/DINO/pose estimator 与大规模训练。

### Kill criteria

- 相对最强同预算 baseline，pairwise candidate ranking 没有至少 +10 个百分点；或闭环成功率没有至少 +5 个百分点；
- 同容量直接 scorer 与多步 dynamics 持平，说明 WAM rollout 没有必要；
- 地址交换或 SE(3) 等变测试失败；
- 增益只来自额外深度/pose 标签，匹配监督后消失；
- K 增大时 WAM 选择产生明显 winner's curse，真实 simulator 排名反而下降。

## 去重后的其他候选空白

| 候选 | 可守的窄问题 | 最小实验 | 判断 |
|---|---|---|---|
| 身份边缘化 object rollout | 遮挡/跨相机后不硬绑定 ID，而在少量身份假设上分别 rollout，再边缘化选动作 | 同类物体交叉遮挡；比较 hard-ID、3D tracker 与 identity posterior | **较值得做**；必须证明收益来自 posterior 进入动作选择，而非只提升 tracking |
| 可逆对象关系事件 WAM | 预测 contact/support/inside/grasp 的新增、删除与失效，而非只预测连续 pose | 放入后取出、堆叠后碰倒、抓住后滑落 | **较值得做**；与长时进度、验证和纠错最贴合 |
| 校准对象占据管 | 为每个对象输出未来 4D occupancy set 与身份/pose 不确定性，并进入 chance-constrained 控制 | 遮挡、摩擦、相机基线 shift；测 coverage、碰撞与保守率 | **有空间但较难**；安全 claim 要严格限制为经验校准，不可声称形式保证 |
| 部件—对象层级地址 | handle→drawer→cabinet 的层级 identity，预测关节内在状态而非自由 SE(3) | 门、抽屉、旋钮与相似把手 | **应用型强候选**；容易与 part-centric/articulation 工作碰撞 |
| 接触介导的反事实效果路由 | 区分直接受作用对象、承载导致共运动对象和相机运动 | 推杯、移动托盘、移动相机三组匹配观测 | **科学问题好但数据难**；需要 simulator branching 或强因果配对 |
| Object-frame effect Jacobian | 预测局部动作对对象 pose/contact 的效果导数，用少量迭代优化动作 | 推、拨、抓；比较等调用预算候选 rollout | **方法感强、风险高**；接触模式切换会破坏局部线性 |
| 决策敏感的局部几何细化 | 只在不同分辨率会改变动作排序时，细化接触区域 4D 几何 | 杂乱场景、窄间隙抓取、插入；匹配 GPU 延迟 | **工程/效率型空白**；要证明不是普通 uncertainty-triggered refinement |
| 主动身份消歧 | WAM 预测换视角/轻触等探针后的身份信息增益，再执行任务 | 相似对象遮挡；固定额外动作预算 | **有空间但更像主动感知**，不是最直接的 WAM 主线 |
| 地址分裂—合并 lineage | 内容物显露、拆盖、区域碎裂时维护 identity lineage 与历史关系 | 取出内容物、拆盖、重遮挡 | **新但很难**；RGB 下守恒量不可靠，任务覆盖较窄 |
| 跨本体 contact token | `(object, surface point, normal, displacement, contact mode)` 作为共享 action-effect | 两种机械臂/夹爪的少样本迁移 | **拥挤**；PointAction、μ0 等已非常接近 |

## 独立查新终审（provisional）

| 排名 | 候选 | Novelty | Impact | Feasibility | 终审判定 |
|---:|---|---:|---:|---:|---|
| 1 | 身份边缘化 object rollout | 7.6 | 8.0 | 7.0 | 最可守；novelty 必须是身份后验进入 action-conditioned rollout，而不是更好的 tracking |
| 2 | ACG-WAM | 6.4 | 8.8 | 6.5 | 影响潜力最高，但被已有工作的并集严重包围；宽泛 address+geometry claim 不成立 |
| 3 | 校准对象占据管 | 7.2 | 8.4 | 6.2 | 有新意，但闭环校准、安全与保守停滞使实现风险较高 |

终审认为 ACG-WAM 未被任何单篇论文完全封死，但必须击败“OА-WAM 地址模块 + ORD/MRO rollout + 通用关系评分器”这一组合基线。可守贡献严格限定为：冻结 π0.5 产生多个候选 chunk，对被语言寻址的对象执行反事实 pose/relation/contact rollout，并据目标关系 rerank/verify。

语言双向绑定、主动身份消歧、地址 lineage、跨视角规范化、effect Jacobian、跨本体 contact token、坐标运输主要只有 component/benchmark 价值。关系事件图若不能改变控制决策，也应降级为 benchmark。

## 当前优先级

1. **身份边缘化 object rollout**。问题边界最清楚；必须证明身份 posterior 进入 rollout 后降低 wrong-object action，而不是只提高 IDF1。
2. **ACG-WAM：语言可寻址的候选动作反事实几何**。与 π0.5 对接最自然、影响潜力最高，但应先做 oracle 实验，避免投入一个仅靠现有模块拼接即可实现的系统。
3. **校准对象占据管**。适合安全敏感场景；实现和论证难度高于前两项。

**可逆对象关系事件 WAM** 与用户已经遇到的长时任务失忆、错误完成和恢复最贴合，建议把它作为前两项中的输出状态/验证头，而不是单独堆成第四个大模型。

对象占据管适合作为第二阶段安全扩展；部件/关节和双臂 payload 几何适合作为明确应用域，但不建议一开始同时加入。

## 推荐的论文形状

最干净的版本不是“全都做”，而是：

> 一个冻结 π0.5 的候选动作生成器 + 一个轻量 ACG-WAM。核心输出只包括被语言寻址对象的多步相对 pose、关键关系事件和不确定性。通过 identity swap、SE(3) transform、action intervention 三类因果测试证明表示正确，再用候选动作 reranking/verification 证明闭环价值。

第一版不要同时加入完整 RGB 视频生成、跨本体、在线系统辨识、触觉和大规模真实机器人训练。它们会使因果主张无法归因。

## 主要文献

- OA-WAM, arXiv:2605.06481
- MRO-GWM, arXiv:2606.01950
- PointAction, arXiv:2606.03943
- WSA1, arXiv:2607.03941
- WAM4D, arXiv:2606.14048
- X-WAM, arXiv:2604.26694
- GWM, arXiv:2508.17600
- ORD-WM project/preprint

## 暂停点

本轮只完成方向组合、候选发散、去重、最近邻冲突与最小证伪设计。未进入具体实现，也未启动 GPU 或真实机器人实验。
