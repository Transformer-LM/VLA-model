# Research Wiki Query Pack

_Auto-generated. Do not edit._

## Project Direction
# Research Brief — ISRAC

**状态：** ready-for-discovery / selected-idea execution  
**语言：** 中文  
**论文写作：** 关闭

## 研究问题

反馈式 World Action Model（WAM）会根据已经执行动作暴露的预测误差，
修正、重排或否决尚未执行的 VLA 候选动作。单个 factual residual 可能
无法识别误差对不同动作的响应：两个合法物理世界可以产生完全相同的
历史观测与 residual，却让同一个未来候选动作产生不同的真实效果。

## 当前 Idea

**Influence-Separated Residual-Alias Compiler（ISRAC）** 自动寻找两个
simulator-native 物理世界，使：

1. 冻结 VLA 的 factual action 和完整反馈接口在两世界中相同；
2. 未执行候选动作会激活此前零影响的物理参数块；
3. 候选未来的物理效果显著分离；
4. 编译搜索不读取目标 WAM 的 score、ranking 或 residual sign；
5. 每个 pair 附带参数语义、历史同一性、首次激活与首次分歧证书。

## 可证伪主张

主张 C1：相对随机/网格/CMA-ES 等预算物理扰动，influe
## Open Gaps
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


## Key Papers (46 total)
- [paper:assran2025_vjepa_selfsupervised_video] V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning
- [paper:bagaria2026_recursive_belief_vision] Recursive Belief Vision Language Action Models
- [paper:belkhale2024_rth_action_hierarchies] RT-H: Action Hierarchies Using Language
- [paper:bhamidipaty2026_imperfect_world_models] Imperfect World Models are Exploitable
- [paper:black2024_visionlanguageaction_flow_model] $π_0$: A Vision-Language-Action Flow Model for General Robot Control
- [paper:brohan2022_rt1_robotics_transformer] RT-1: Robotics Transformer for Real-World Control at Scale
- [paper:brohan2023_rt2_visionlanguageaction_models] RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control
- [paper:bu2025_univla_learning_act] UniVLA: Learning to Act Anywhere with Task-centric Latent Actions
- [paper:cheang2024_gr2_generative_videolanguageaction] GR-2: A Generative Video-Language-Action Model with Web-Scale Knowledge for Robot Manipulation
- [paper:chen2026_lawam_latent_world] LaWAM: Latent World Action Models for Efficient Dynamics-Aware Robot Policies
- [paper:collaboration2023_open_xembodiment_robotic] Open X-Embodiment: Robotic Learning Datasets and RT-X Models
- [paper:du2023_learning_universal_policies] Learning Universal Policies via Text-Guided Video Generation
## Recent Relationships (23 total)
  idea:active-causal-discrepancy-experiments --addresses_gap--> gap:G9
  idea:witness-carrying-progress-actions --addresses_gap--> gap:G7
  idea:witness-carrying-progress-actions --addresses_gap--> gap:G9
  idea:task-equivalent-recovery --addresses_gap--> gap:G7
  idea:task-equivalent-recovery --addresses_gap--> gap:G9
  idea:controllability-phase-progress-certificates --addresses_gap--> gap:G1
  idea:controllability-phase-progress-certificates --addresses_gap--> gap:G9
  idea:controllability-phase-progress-certificates --addresses_gap--> gap:G10
  idea:policy-conditional-correction-slack --addresses_gap--> gap:G7
  idea:policy-conditional-correction-slack --addresses_gap--> gap:G9
  idea:policy-conditional-correction-slack --addresses_gap--> gap:G10
  idea:endogenous-suffix-witnesses --addresses_gap--> gap:G7
  idea:endogenous-suffix-witnesses --addresses_gap--> gap:G9
  idea:endogenous
