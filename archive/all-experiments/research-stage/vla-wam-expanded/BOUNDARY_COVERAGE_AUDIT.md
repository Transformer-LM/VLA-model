# VLA × WAM 扩展版图：边界与覆盖审计

**Run ID：** `20260806-vla-wam-expanded-field-map`  
**审计对象：** 16 条母方向、69 条去重文献记录、44 个定向 query family。  
**结论：** `PASS with WARN`。旧版 6 条全部有去向，新版 16 条无 orphan；R1–R4 × U1–U6 在概念上完整覆盖，但若干格只有邻域或窄场景证据，必须保留 sparse/warn，不能为了填格而生成第 17 条方向。

## 1. 旧 6 条如何扩成新 16 条

为避免旧、新 H 编号复用造成伪 lineage，旧版统一写作 O1–O6，新版写作 H1–H16。

| 旧方向 | 新方向去向 | 为什么必须拆开 |
|---|---|---|
| O1 预测式 world objective 改善 VLA | H1 主继承；分出 H2/H3/H4；与 H14 交叉 | future auxiliary、latent intervention、结构化物理变量和 persistent belief 的预测对象与决定性证据不同；原生 jointness 是另一个架构问题 |
| O2 learned rollout planning 与 deployment steering | H5/H6/H7；条件交叉 H8/H16 | 生成 desired subgoal、比较 action consequences、为信息增益选择 sensing action 是三个不同 endpoint；只有部署交互改变 system belief 才进入 H16 |
| O3 VLA 裁判、critic 与安全闸门 | H8/H9/H10；失败回灌时交叉 H13 | reward/value、整套 policy 评估和逐步 runtime intervention 的决策单位不同 |
| O4 learned world 生成经验并后训练 VLA | H11/H12/H13 | 固定 synthetic data、在 WM 内依据回报更新 policy、由失败主动采数并交替更新，是三种 update regime |
| O5 joint World–Language–Action foundations | H14 主继承；机制可交叉 H1/H2/H8 | H14 只回答 joint architecture 是否承重；具体 future、latent action、value 的贡献必须回到相应用途方向 |
| O6 跨具身 action-effect 与 policy–world 共适应 | H15/H13/H16；表示桥可交叉 H2 | 跨 morphology 的 effect interface、生命周期级 data flywheel、单次部署的 system ID/TTA 发生在不同 population/time scale |

反向检查：H1–H4 均可追溯到 O1/O5/O6 的被压缩子问题；H5–H10 可追溯到 O2/O3；H11–H13 可追溯到 O3/O4/O6；H14–H16 可追溯到 O5/O6。结论为 **6/6 无丢失，16/16 无 orphan**。

## 2. R1–R4 × U1–U6 覆盖矩阵

图例：**●**＝已有直接 VLA×WM primary anchor；**◐**＝直接证据集中于单线、新预印本或 strict VLA/WAM 一侧偏弱；**△**＝主要是邻域/边界证据；`*`＝该 H 是消费端点或更新制度 overlay，不等同于 U 类别。

| Representation \ Use | U1 表征预训练 | U2 goal/trajectory proposal | U3 candidate evaluation | U4 MPC/planning | U5 imagined policy optimization | U6 joint world-action policy |
|---|---|---|---|---|---|---|
| **R1 decoded video/pixel** | ● H1 | ● H5；H11* | ● H6/H8；H9*/H10* | ● H6 | ● H12；H13* | ● H14（兼 H1） |
| **R2 pixel/video latent** | ● H1 | ● H5；H11* | ● H6/H8；H9*/H10* | ● H6 | ● H12；H13* | ● H14 |
| **R3 task-centric latent/belief** | ◐ H1/H2/H4；H11* | ●/◐ H2/H5；H11*/H15* | ●/◐ H6/H8；H9*/H10*/H16* | ◐ H6/H7；H15*/H16* | ◐ H12；H13* | ●/◐ H2/H4/H8/H14；H15*/H16* |
| **R4 explicit state/object/contact/reward** | ◐ H3/H4；H11*/H15* | ◐ H3/H5；H11*/H15* | ◐ H8/H10；H9*/H16* | △ H3/H7/H10/H15；H16* | △/◐ H12/H13 | ◐ H3/H14；H15*/H16* |

矩阵说明：

- 24 格都被 16 条方向在概念上容纳，但 **R3×U4、R4×U4、R4×U5** 主要依赖邻域或窄场景证据，是 evidence gap，不是自动新增宏方向的理由。
- H9 evaluation、H10 assurance、H11 data engine、H13 co-evolution、H15 transfer、H16 deployment adaptation 是生命周期 overlay；强塞进 U3/U5/U6 会丢失独立 endpoint。
- H7 常实现为 U4，但优化的是 information gain/belief reduction，不是一般 task return；H8 可按使用位置落到 U3、U5 或 U6。
- 同一论文可占多个格，但按去重论文与独立 claim 计数；多标签不会凭空增加证据量。`●` 也不代表成熟或已正式发表。

## 3. 方向重叠时如何归类

总规则是按 **核心科学主张 + 主要 endpoint + 发生时点 + 谁被更新** 归主方向，而不是按模型名字、模态或架构命名。同一论文可以多标签，但同一项因果主张只能有一个 primary H。

| 易混组合 | 归类判据 |
|---|---|
| H1 vs H14 | 可移除的 future auxiliary 主要改善动作归 H1；研究 shared/joint architecture 本身归 H14 |
| H2 vs H11 vs H15 | latent intervention representation 归 H2；变成伪标签/数据归 H11；跨 native action space 的 effect transfer 归 H15 |
| H3 vs H5/H6/H10 | 结构化物理预测本身归 H3；desired subgoal 归 H5；action alternatives 归 H6；风险干预归 H10 |
| H4 vs H7 vs H16 | 维护 partial-observability belief 归 H4；主动选 sensing action 归 H7；识别改变的系统并适配归 H16 |
| H5 vs H6 | 生成“想达到的未来”再执行归 H5；比较候选 native actions 并闭环 replan 归 H6 |
| H6 vs H8 | 搜索/选择机制归 H6；reward/value/critic 的正确性与作用归 H8 |
| H8 vs H9 vs H10 | 当前动作/训练的 score 归 H8；整套 policy/checkpoint 评估归 H9；逐步 veto/intervention/recovery 归 H10 |
| H10 vs H13 | 处理当前 rollout 失败归 H10；失败决定下一轮采数和模型更新归 H13 |
| H11 vs H12 vs H13 | 固定生成集再 SFT/BC 归 H11；在固定 learned world 中依据 return 优化归 H12；主动采数且 WM/policy 交替更新归 H13 |
| H13 vs H16 | 跨任务/生命周期的 population-level flywheel 归 H13；单次部署实例的快速适应归 H16 |
| H15 vs H16 | 无需当前 system ID 的 shared effect transfer 归 H15；部署后从 probes/history 推断当前系统归 H16 |
| H16 vs H6 | 冻结系统的 imagine-and-rank 归 H6；context/belief/WM/policy 因当前交互而改变归 H16 |

## 4. 证据密度审计

- **稠密/拥挤：** H1、H5、H6、H9、H12、H14。H1/H9/H14 仍大量依赖 E2，数量不等于因果成熟。
- **中等/快速形成：** H2、H3、H8、H10、H11。H3 高度集中于 2026；H10 是检测多、恢复少；H11 裸记录多，但 strict VLA×可 rollout WM 比例较低。
- **frontier/sparse：** H4、H7、H13、H15、H16。H7 多为非通用操作或非 strict VLA；H15 多为 latent-action/no-language 邻域；H16 有 ICWM 直接强锚点，因此是 breadth sparse，不是“尚不存在”。
- **强制 WARN：** R4×U4、R4×U5；H10 autonomous recovery；H13 calibrated active acquisition；H15 双向 native-action↔effect；H16 explicit system-ID identifiability。

## 5. 是否遗漏第 17 条方向

未发现同时满足“至少 2 个独立 primary anchors + 新核心科学问题 + 新主要 endpoint + 能用决定性证据与现有 H 区分”的遗漏簇。以下保留为横切 watchlist，不升格为方向：

- uncertainty/calibration：横跨 H7/H9/H10/H13/H16；
- long-horizon/temporal abstraction：H4/H5 的压力轴；
- action-free web/human video：H1/H2/H11/H14/H15 的 data regime；
- audio/force/proprioception 等模态：H3 的 observation slice；
- tool-use/cascade/joint：耦合 topology，不是独立科学 endpoint；
- real-time、efficiency、distillation：资源约束，不是母方向；
- navigation、mobile manipulation、humanoid、social/multi-agent：任务/具身 slice，是本轮操作任务偏置的 search blind spot；
- causality、controllability、action sensitivity：所有方向的证据要求。

## 6. 审计结果

| 检查项 | 结果 | 备注 |
|---|---|---|
| old→new lineage | PASS | 6/6 无丢失，16/16 无 orphan |
| R/U structural coverage | PASS with WARN | 24 格概念覆盖，3 格证据偏邻域/窄场景 |
| direction independence | PASS with rules | 重点防 H1/H14、H5/H6、H8/H9/H10、H11/H12/H13、H13/H16 相互吞并 |
| evidence maturity | WARN | frontier/sparse 标签不得由邻域论文补齐 |
| 17th-direction omission | NO demonstrated omission | watchlist 保留，等待未来证据形成独立簇 |
| workflow checkpoint | PASS | `selected_macro_direction = null`；Idea 阶段应阻塞等待人工选择 |

资源审计：**0 GPUh、0 paid cost、0 real-robot trials、0 launched jobs**。本轮没有具体 Idea、benchmark 选择、实现或实验。
