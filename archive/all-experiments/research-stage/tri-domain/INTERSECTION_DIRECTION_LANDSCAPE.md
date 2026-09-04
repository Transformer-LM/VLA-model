# VLA × WAM 强交叉母方向版图（6 条）

**定位：** 每条路线必须同时指出 VLA 接口、learned dynamics 的实际作用和二者的因果连接。只把 VLA 当黑盒 policy、或只共享视频 backbone，不算强交叉。  
**评分：** 科学影响 25%、创新空间 20%、证据缺口 20%、当前配置可行性 20%、取得可信初证速度 15%；不构成自动选择。

## 总览

| ID | 母方向 | WAM 在 VLA 生命周期中的角色 | 密度/拥挤度 | 分数 |
|---|---|---|---|---:|
| H1 | 预测式世界目标改善 VLA | 训练时辅助监督/预训练 | 中高 | 72.4 |
| H2 | Learned rollout 规划与 deployment steering | 推理时想象、选择、重规划 | 高 | 74.7 |
| H3 | VLA 裁判、critic 与安全闸门 | 评估、排序、拒绝、风险 | 中等、证据断层最大 | **94.5** |
| H4 | Learned world 生成经验并后训练 VLA | synthetic data / imagined RL | 中等、快速增长 | 80.0 |
| H5 | 联合 World–Language–Action 基础模型 | 原生共享表示与目标 | 很高、foundation-scale 拥挤 | 66.3 |
| H6 | 跨具身 action-effect 对齐与 policy–world 共适应 | 迁移和在线交替更新 | 低到中、最开放也最难 | 79.1 |

## H1 — 预测式世界目标能否真正改善 VLA

**人话解释。** 训练 VLA 时顺便要求它预测未来图像、运动或 future features，看这是否让动作更懂物理。

**耦合位置。** World prediction 是预训练或辅助监督，最终 endpoint 仍是 VLA action quality；推理时可以丢弃 world head。

**方法与锚点。** future-frame/feature prediction、motion/flow target、latent dynamics auxiliary、interleaved video-action pretraining；GR-1/2、DUST、Joint Motion Image Diffusion，V-JEPA 2 只作弱邻域。

**边界与冲突。** 执行时真正调用 rollout 转 H2；生成训练轨迹转 H4；原生联合且 world path 长期保留转 H5。额外视频、参数和 token 常与 world objective 同时增加。

**决定性证据。** 同 VLA、数据、参数、token 和优化步，比较 action-only、静态辅助、future feature 与 future video；冻结/切断 world path，并以 held-out 闭环控制而非 probe 作为终点。

**资源与风险。** 公开 checkpoint 加小 head/LoRA 适合 2 GPUh pilot；从头视频预训练超预算。评分 **72.4**。

## H2 — 用 learned rollout 给 VLA 做反事实规划与部署时 steering

**人话解释。** 先把若干候选动作在模型里“试演”，再让 VLA 执行预测后果最好的一个，并根据新观测重规划。

**耦合位置。** VLA 提议 native action 或 chunk，action-conditioned WM 预测后果，goal/value 选择候选；二者在推理时闭环连接。

**方法与锚点。** video/keyframe plan、latent rollouts、best-of-N、tree search、value-guided replanning；Cosmos Policy、World Pilot、DREAMSTEER、World-Value-Action，UniPi/VLP/RoboDreamer 是早期层级锚点。

**边界与冲突。** 只生成理想关键帧而不比较候选动作属于弱规划；只做离线 policy ranking 属 H3。长 horizon 增加远见也放大误差，推理预算常远高于 direct VLA。

**决定性证据。** 匹配 wall-clock、FLOPs、候选数和 replanning 频率，比较 direct VLA、model-free value/self-consistency、learned WM 与 oracle dynamics，并报告 action sensitivity、OOD calibration、drift、latency 和闭环成功。

**资源与风险。** 短 horizon、少候选可低成本证伪；完整长时规划通常超过 8 GPUh。评分 **74.7**。

## H3 — 世界模型能否成为可信的 VLA 裁判、critic 与安全闸门

**人话解释。** 不上真机或少上真机，先判断哪个 policy/checkpoint 更好、哪个动作危险、什么时候应拒绝或求助。

**耦合位置。** Learned dynamics 产生 policy-conditioned future，critic/VLM/value 转成 ranking、risk、veto 或 selective autonomy。

**方法与锚点。** paired rollout、Monte Carlo policy evaluation、world-value、risk head、VLM judge、calibration/selective prediction；WorldEval、WorldGym、PiL-World、GigaWorld-1、Gemini-in-Veo、TACO。

**边界与冲突。** 只评价视频质量不算。把任意 VLA 放进模拟器却不验证 policy ranking、安全或选择收益，也只是邻域。相对排序可能成立，而新 policy/OOD action 上绝对风险严重偏乐观。

**决定性证据。** paired ground-truth rollout；与 VLM-only judge、model-free value 和 oracle dynamics 比较 ranking、ECE/Brier、coverage–risk、危险动作召回，并专测 policy-induced OOD 和尾部失败。

**资源与风险。** 可复用日志和 checkpoint，最适合零真机、2/8 GPUh 配置；共享 foundation bias 与失败数据稀缺仍限制安全结论。评分 **94.5**。

## H4 — 用 learned world 生成经验并后训练 VLA

**人话解释。** 让 VLA 在想象世界里获得新示范、失败修正或 RL 经验，再回真实/ground-truth 环境验收。

**耦合位置。** World model 改变 VLA 的训练数据或提供训练环境；可以是离线 synthetic trajectory，也可以是闭环 imagined RL。

**方法与锚点。** video→LAM/IDM pseudo-actions、world simulator RL、reflector/correction、latent bootstrapping、policy–simulator curriculum；World-Env、WMPO、World-Gymnast、WoVR、RehearseVLA、SWORD、TACO，DreamGen 是弱数据邻域。

**边界与冲突。** 只评 policy 属 H3，只在推理时选择动作属 H2，原生 joint model 无外部后训练属 H5。dynamics、reward、termination 和伪动作错误会复合，且 policy 会主动寻找模型漏洞。

**决定性证据。** 匹配真实交互、训练 FLOPs 和总样本，比较 real-only SFT、普通增强、model-free RL、learned WM 与 oracle simulator；把 imagined 高回报轨迹回放到 ground truth，统计虚假高回报和 effective sample yield。

**资源与风险。** 2 GPUh 可审计 frozen WM exploitation；可信多种子 post-training 往往接近或超过 8 GPUh。评分 **80.0**。

## H5 — 联合 World–Language–Action 基础模型

**人话解释。** 同一模型同时理解语言、预测未来并输出动作，而不是把 VLA 与 WM 简单串成两块。

**耦合位置。** World、language、action token/latent 共享或交错，并联合训练 future、action、value 或 inverse/forward objectives。

**方法与锚点。** shared backbone + heads、interleaved sequence、dual diffusion/flow、统一 video/action token；GR-1/2、3D-VLA、WorldVLA、RynnVLA-002、DUST、DreamZero、Cosmos Policy。

**边界与冲突。** 只有 next action token、只共享视觉 backbone、或没有语言接口的视频—动作模型不算强交叉；因此 UWM/UVA 降为邻域。当前“联合”本身很拥挤，规模与机制归因普遍薄弱。

**决定性证据。** 同数据、参数、训练 token、步数和推理预算比较 action-only、world-only、separate cascade 与 joint shared；冻结或删除 world path，检查动作收益是否仍存在。

**资源与风险。** 当前只能基于公开 checkpoint 做小消融/低秩适配，foundation-scale 从头训练远超 8 GPUh。评分 **66.3**。

## H6 — 跨具身 action-effect 对齐与 policy–world 在线共适应

**人话解释。** 不同机器人关节命令不同，但可共享“动作造成什么物理效果”；部署后 policy 与 WM 还要随新身体和新分布互相更新而不一起学错。

**耦合位置。** Shared effect/dynamics space 翻译不同 native actions；policy rollout 更新 WM，WM imagination/critic 再更新 policy。

**方法与锚点。** latent/effect action、embodiment-conditioned dynamics、world-policy alternating update、test-time training、co-evolution；DreamZero、World-VLA-Loop、WoVR、World-Gymnast，LAPA 与 Scaling Cross-Embodiment WM 是弱邻域。

**边界与冲突。** 没有 learned dynamics 的普通 adapter 属 V4/V5；固定 WM 的一次性后训练属 H4。fixed WM 会 distribution shift，co-evolution 又可能共同漂移。

**决定性证据。** 完整 held-out embodiment，匹配目标数据与 adapter 容量，验证 `native action → shared effect → target action` 的双向可恢复性；比较 frozen、policy-only、WM-only、alternating co-adaptation 与 oracle，并测校准和遗忘。

**资源与风险。** 公开多机器人日志可做离线 pilot；真正在线跨硬件结论受零真机和 8 GPUh 限制。评分 **79.1**。

## 六方向之间的严格边界

- H1 在训练时提供预测监督；H2 在推理时消费 rollout；H3 评价/拒绝；H4 改写训练经验；H5 原生联合；H6 处理身体/时间变化。
- 同一论文可以跨多条路线，但同一项因果主张必须落到一个明确 endpoint。
- “加入 world objective 后分数更高”不够；至少需要 matched action-only、切断 world path 或 oracle/外部环境锚点中的一种强因果对照。
- 本图没有选择具体 Idea、模型、benchmark 或实现。
