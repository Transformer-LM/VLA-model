# Cycle-2 flow/noisy-action candidate review

结论：只剩 1 个窄候选，判定为 `PARTIAL`，不是干净的 broad novelty。若论文仍表述为“让 future prediction 看到 action / predicted action”，已经被撞掉。

## 已排除的机制

| 机制 | 判定 | 最近工作 |
|---|---|---|
| clean demonstration action → future head | `SCOOPED`，且存在训练期 GT shortcut | [SelfWAM](https://arxiv.org/html/2608.00725) 用单独 clean-action stream 条件化 future RGB/mask；[UWM](https://arxiv.org/html/2504.02792) 也以 clean action 实现 forward dynamics |
| raw noised action x_tau → future latent | `SCOOPED` | [FLARE](https://arxiv.org/html/2505.15659) 的 future token 已与 noised action 共同 self-attend |
| joint action–future flow、独立 modality timestep | `SCOOPED` | [DUST](https://arxiv.org/html/2510.27607)、[GigaWorld-Policy-0.5](https://arxiv.org/html/2607.13960)、[UWM](https://arxiv.org/html/2504.02792) 均覆盖；[NoiseGate](https://arxiv.org/html/2605.07794) 进一步把 latent timestep 作为信息门 |
| 直接把当前 denoised action hypothesis 回馈 world predictor | `SCOOPED/PARTIAL` | [DAWN](https://arxiv.org/html/2605.11550) 已递归执行 action→world→action refinement |
| 单纯跨 denoising timestep consistency | `SCOOPED` 于 action 输出层 | [Consistency Policy](https://arxiv.org/html/2405.07503) 已沿 diffusion trajectory 约束 action endpoint 一致，但没有约束 future outcome |

## 唯一保留候选：Policy-Trajectory Outcome Consistency

核心不是把训练数据中的 action 换一种形式喂进去，而是 future head 只能看到由策略自身、从纯噪声端生成的低维物理动作估计。

关键约束：

- 两个 action estimate 均来自模型自己的 denoising trajectory；future 路径不接触 ground-truth action 或由它构造的 noisy action。
- future head 只能看到解码后的低维物理动作向量，不能看到 action-DiT hidden state，避免隐式高带宽“藏答案”。
- 在 action estimate 边界停止梯度，避免 future loss 把动作小数位变成未来 latent 的编码通道。
- future query 与 action query 使用单向 mask；future 可读动作，动作不可读 future target。
- 先学习 observation-only 基线，动作分支只解释剩余变化；加入 matched-vs-swapped action margin，避免 residual head 退化为第二个 observation-only predictor。

### 精确 novelty delta

- 与 [VLAFlow](https://arxiv.org/html/2607.01586) 相比，VLAFlow 明确禁止 latent token 读取 noised action；本候选加入 action→outcome 路径。
- 与 FLARE/SelfWAM/GigaWorld 相比，future head 不接触 clean/noised demonstration action，只接触策略从纯噪声生成的动作估计。
- 与 DAWN 相比，这不是测试时递归 world-action rollout，而是 action-only deployment 下的训练期 latent auxiliary。
- 与 Consistency Policy 相比，一致性对象不是 action endpoint，而是“同一模型动作轨迹在不同 denoising 时刻所暗示的 outcome residual”。

未找到把这四点同时组合的 2024–2026 primary source，但各组成思想都有强先例，因此只能报 `PARTIAL / narrow novelty`。

## 建议的 <=8 GPUh pilot

固定 checkpoint、数据、seed、参数量和训练时长，冻结 VLM 与 future target encoder，仅训练 shared-DiT LoRA 和等参数量 future heads。比较 observation-only future alignment、raw noised-action future alignment、policy-trajectory outcome consistency 三组。主要诊断为 matched action 相对 swapped action 的 future-latent binding 增益，同时报告 future-latent cosine/MSE、跨时间 residual 差异、action validation loss 和闭环成功率。

致命 falsifier：在 self-generated action 下的 binding 增益 bootstrap 95% CI 不大于 0，或 residual norm 收缩到近零；尤其若换成 clean GT action 后 binding 才出现，则说明无泄漏接口无法提供足够 outcome 信息，应直接放弃 H1。附加停止条件是 action validation loss 恶化超过 3%，或闭环结果没有任何方向性收益。

一句话论文边界必须收紧为：`leakage-free outcome consistency along the policy's own denoising trajectory`。如果 pilot 不通过，就应记为 `NO-CANDIDATE`，不再退回 clean/noised-action 拼接。

本轮仅做了只读文献核查；未编辑文件、未连接服务器、未启动训练。
