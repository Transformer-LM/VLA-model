# Gap Map

_Field gaps with stable IDs._

## G1 — 感知保真度与控制功能保真度脱钩

视频/视觉预测指标不能稳定推出策略排序、闭环成功或接触可执行性。跨任务、跨策略族的 paired rollout 功能协议仍缺失。

## G2 — OOD evaluator 校准与尾部失败覆盖不足

world-model evaluator 在 policy/task/visual shift 下可能过度自信；需要排序一致性、coverage–risk、危险假阴性和最坏子组证据。

## G3 — representation × control-use 缺少公平因果比较

pixel/video、visual token、task latent 和 structured state 的比较常混入不同 planner、模型规模、数据与推理预算，尚不能回答哪类状态在何种控制用途下真正必要。

## G4 — imagined policy optimization 的模型利用问题

policy 更新后会进入 world model 的低支持区域，模型内回报改善可能来自 exploiting model error；缺少 policy-shift 后的 ground-truth replay 与不确定性审计。

## G5 — 跨 embodiment 的动作语义与接口不统一

continuous action、action token、latent action、控制频率与归一化差异限制 world/action 模块复用，也让“统一 world–action model”的收益难以归因。

## G6 — 合成轨迹的有效样本率与动作有效性不透明

world-generated data 的视觉合理性、物理可执行性、IDM 回译误差、污染和 held-out 控制边际价值尚缺统一审计。

## G7 — 罕见失败与安全边界数据不足

成功轨迹和常见错误主导公开数据，导致 critic、risk monitor 与 world model 对不可逆接触、损坏和恢复失败的证据薄弱。

## G8 — world–policy coupling 的因果贡献不清

联合模型通常同时增加参数、数据和训练 token；缺少 matched-scale 的 frozen / alternating / joint 对照，也缺少不共享偏差的外部评价锚点。

## G9 — 部分可观测条件下的长期 belief 与对象持久性

更长上下文不等于可靠记忆；需要当前画面相似但历史决定真实状态的 paired protocol，检验遮挡后的身份、接触状态、belief 校准和闭环价值。

## G10 — 结构相关性与因果干预效果未分离

对象 token、3D state 或 action conditioning 仍可能依赖外观相关性；缺少 spurious-correlation reversal 和 intervention-effect 测试来验证可供性不变性。

## G11 — 多模态接触动态受硬件和可观测性限制

视觉下不可辨识的滑移、受力和接触状态需要触觉/本体感觉，但同步、sensor dropout、跨材料和跨硬件泛化证据仍弱。

## G12 — 主动感知与主动采数的价值核算不足

当前 episode 的信息动作和面向未来学习的数据 acquisition 常被混合；两者都缺少匹配观测、移动、真实交互和人类时间预算的收益曲线。

## G13 — 部署时 system identification 与闭环收益脱节

短历史可能降低 configuration/dynamics prediction error，但尚需证明它能以少量安全 probe 改善新相机、摩擦、负载、延迟或 morphology 下的闭环控制。

## G14 — 长期 policy–world 共适应的遗忘与共同漂移

静态联合模型不能证明持续学习；缺少按任务流报告 forward/backward transfer、forgetting、全程 AUC、world calibration drift 和旧任务安全退化的协议。

## G15 — 缺少连接模型、策略和环境的 WAM 功能基准

action sensitivity、物理/接触一致性、policy-ranking agreement 和环境成功仍分散在不同 benchmark；视觉质量无法替代跨层预测效度。

## G16 — VLA 数据规模、多样性与质量的因果归因不足

通用 VLA 往往同时扩大数据量、任务/场景/embodiment 多样性、模型规模和训练 FLOPs；缺少固定模型与预算的数据 scaling curve、负迁移分析和单位采集成本的有效收益。

## G17 — VLM 语义迁移与闭环物理 grounding 脱节

互联网预训练可改善概念、语言组合和高层推理，但语义选择正确不保证空间精度、接触稳定和任务完成；需要同时连接 semantic endpoint 与 physical-control endpoint 的 matched evidence。

## G18 — VLA 动作表示缺少同骨干、同预算公平比较

离散 token、regression、ACT chunk、FAST、diffusion 和 flow 常使用不同 backbone、数据、控制频率、chunk horizon 与采样预算；尚不能回答何种表示在精度、延迟、反应性和多峰性之间真正占优。

## G19 — 跨具身 VLA 的完整留出与接口可恢复性不足

多机器人训练集内平均提升不能证明未见 embodiment 迁移；action normalization、坐标系、camera convention、control frequency 和 per-robot head 会混淆共享动作语义的贡献。

## G20 — 少样本 VLA 适配缺完整系统成本与 OOD 账本

参数量或 fine-tuning success 不能代表可部署性；需要 success–demonstration curve、训练 FLOPs、显存、wall-clock、端到端 Hz、能耗、输入输出规范和 OOD 退化的统一报告。

## G21 — 长程 VLA 的记忆、信息获取与失败恢复证据碎片化

层级推理、历史记忆、主动视角和人类 intervention 常与更强低层 policy、额外观察或更高推理预算同时出现；缺少固定底层能力下的误差传播、恢复率、观察成本和延迟比较。

## G22 — VLA 交互式后训练的稳定、奖励与持续安全问题

RL/post-training 可以覆盖行为克隆未访问的状态，但 reward hacking、on-policy 成本、reset、安全探索、旧技能遗忘和 OOD 鲁棒性可能同时恶化；需要匹配交互预算和全任务序列证据。
