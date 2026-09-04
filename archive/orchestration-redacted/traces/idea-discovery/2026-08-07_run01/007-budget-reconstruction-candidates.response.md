# Cycle-2 budget-constrained reconstruction

结论：有 2 个可进入 ≤2 GPUh pilot 的“条件候选”；不建议凑第三个。二者均为 R3/U6、固定离线数据、短程 PEFT、world 分支训练期使用且推理删除。

## 候选 1：ASAF — Action-SNR-Aligned Foresight

核心机制：把“动作信息可靠度”与“对应的物理未来时刻”在单个训练样本内绑定。高噪声动作只监督近未来，接近 clean action 时才监督 chunk 末端。每样本只预测一个缓存 DINO target，head 从 action-query hidden 读取信息，world gradient 只更新与 action loss 共用的固定 rank-4/8 adapter；推理删除 world head。

Novelty delta：UWM 独立采样 action/video diffusion timestep，但不把 action SNR 映射到物理未来 horizon；Diffusion Forcing 与 NoiseGate 占据 per-token noise/schedule；Fast-LeWM 占据 dense action-prefix→multi-horizon latent prediction；X-Foresight 占据按训练进度 short-to-long horizon curriculum。可主张的窄 delta 仅是同一样本内将 action denoising reliability、可见动作支持与真实物理 horizon 三者绑定。

最小 pilot：一个非饱和 5k/10k checkpoint、两个 action-only success 约 40–80% 的 LIBERO 任务；缓存多个 horizon 的 DINOv2 latent；比较 continued action-only/dummy、固定-horizon future、ASAF、反向或 batch-permuted mapping。参数、target 数、数据顺序、steps 和 FLOPs 匹配。

Kill：严格 future target 不胜 persistence/action-agnostic 或 action-shuffle ratio ≤1.1；对齐映射不优于固定和反向/置乱映射；pooled paired success 增益 <5 pp；非 flow/OFT 降级版本无法触达共享 action representation；四臂 pilot 超过 2 GPUh。

该候选只有在宿主具有原生 flow/noise action path 时才干净；确定性宿主风险明显更高。

## 候选 2：CATF — Control-Affine Tangent Foresight

核心机制：不拟合自由的 future head，而是让共享 action-query representation 参数化局部视觉控制 Jacobian。对白化后的 future-minus-current DINO displacement，使用无 action-agnostic bias 的低秩 control-affine predictor `d_hat = B(h) u`，并让 action loss 与 tangent loss 只共享局部 PEFT adapter；world head 在推理时删除。

Novelty delta：SelfWAM、SG-WAM 和普通 latent WAM 学 endpoint prediction；RobustVLA 正则化 policy Jacobian；VERA 使用 embodiment/kinematic Jacobian 做 video-to-action IDM。未查到 VLA/WAM 直接以视觉 latent 的 forward control Jacobian 作为 removable representation-shaping objective，但控制仿射/Koopman dynamics 是明确先例，因此 novelty 只能落在 VLA 交叉点。

最小 pilot：一个 5k/10k checkpoint、两个未饱和任务；先在 frozen hidden 上筛 horizon；再比较 continued action-only、参数/FLOP 匹配的 endpoint MLP、CATF，并在预算允许时加入 random-orthogonal tangent target。目标维度 64–128、低秩 4–8，不做昂贵逐维 JVP。

Kill：frozen-state probe 不胜 persistence/action-agnostic，或 shuffled action 不显著恶化；rank 4→8 仍无法解释 held-out displacement；CATF 不优于 endpoint head或 random tangent 同样有效；增益只来自 update norm，或任何任务回退 >2 pp。

不列第三个：dense prefix prediction、split/self-consistency、普通 horizon curriculum 和独立 timestep/noise schedule 已被近期工作占据。
