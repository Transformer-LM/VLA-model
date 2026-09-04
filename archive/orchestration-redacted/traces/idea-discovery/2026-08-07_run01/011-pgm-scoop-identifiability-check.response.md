# PGM 查新、可识别性与预算复核

## 硬结论

- 查新结论：**PARTIAL，Level 2—High Overlap**
- 实验结论：**CONDITIONAL-GO**
- 定位：可以作为“future-gradient 因果诊断”推进；不应包装成新的 future head、adapter、WAM 方法，也不能声称完整 causal mediation。

最接近的是 PFD。它已经研究“future branch 的收益是否只是 regularization”，采用输出侧 residual adapter、pure-finetune control 和 shuffled-future control，并明确声称收益来自 future-conditioned correction。PGM 剩余的窄增量是：在 deterministic StarVLA action interface 上做严格的 gradient-routing 随机化、加入 support/gradient-norm matched placebo，并用 cross-fitted representation intervention 检查闭环收益是否依赖该新增子空间。

## A>B 与 A>C 的含义

**A>B 单独不够。** 它只识别“让 correct future loss 的梯度进入 adapter”的总效应，无法排除任何 auxiliary gradient、优化噪声或隐式 regularization 都可能产生相同收益。

加入 C 后，若同时满足：

- A > B：correct future gradient 相对无 auxiliary gradient 有收益；
- A > C：correct correspondence 相对相同强度的 deranged auxiliary gradient 有收益；

则可以排除一个重要的 generic-gradient 替代解释。但结论必须限定为：future-correspondence-specific gradient routing 优于该 support- and norm-matched deranged placebo。不能声称排除了所有 generic auxiliary regularization，因为 norm matching 不匹配梯度方向、协方差、曲率、与 action gradient 的夹角、Adam moments 和 clipping 交互。

C 必须满足：

- task×phase×speed 内无固定点 derangement；
- 不得来自同 episode 或重叠 future window；
- 保留 target/action 边际；
- batch-wise 匹配进入 adapter 的 auxiliary-gradient norm；
- 记录 `cos(g_aux,g_action)`、总梯度 norm、clip rate、Adam update norm；
- 若 C 明显训练崩溃或远差于 B，则 A>C 很可能只是 C 有害，不能支持强 specificity claim。

PFD 已经有普通 shuffled-future control，因此 C 的严格 support 和 gradient matching 是必要增量，不是可选项。

## 五个 paired seeds 的统计推断

五个 paired seeds 可以支持非常窄的一侧方向检验，但门槛极严：

- 每个 seed 先聚合两个预注册任务、每任务 10 个共同 initial states；
- 推断单位是 training seed，不是 rollout；
- 对 A−B、A−C 分别做 one-sided exact sign test；
- 五个非零差值全部为正时，最小 `p=1/32=0.03125`；
- 任一 tie 使有效样本降到 4，最小 p 变为 0.0625；任一负号也不能通过。

最终主张要求两个不等式同时成立，可预注册为 intersection–union test：两项都须 `p<0.05`，无需再做 Bonferroni。不得改用 two-sided test；五对样本的 two-sided 最小 p 是 0.0625。

每 seed 只有 20 个 episode，单个 episode 会改变该 seed 聚合值 5 pp。该设计适合检测一致且较大的效果，约 10–15 pp 以下很可能不稳定。只能推广到这两个固定任务上的 seed-averaged effect，不能声称 LIBERO 普遍规律。

另加预注册实际意义门：五个 seed 符号全正，且总体 A−B、A−C 均至少达到预设最小效应。

## 300→500 rollout 分阶段设计

- 第一阶段：A/B/C intact，共 `5×2×3×10=300` rollouts。
- 只有 A>B 和 A>C 两道门都通过，才运行 A predictive-subspace removal 与 A matched-rank/matched-energy orthogonal placebo，共 200 个新增 rollouts。

第二阶段只能支持：该 cross-fitted treatment-delta subspace 对 A 的收益具有行为必要性。不能称为完整 mediation，因为 mediator 没有独立随机化，adapter 与 action head 会共同适配，treatment 会产生 exposure-induced confounders，subspace 是 post-treatment quantity，closed-loop intervention 会改变后续状态分布，而 cross-fitting 只解决 double dipping。

若 predictive removal 比 orthogonal placebo 更差，且把 A−B gap 明显拉回 B，应称为 necessity/attenuation evidence。没有 B→A coefficient restoration 就没有 sufficiency evidence；即使补上，也仍不是自然间接效应。

## 8 GPUh 可行性

**有可能，但必须由实测门控制。** 29k steps≈107 min 粗略对应 500 steps≈1.8 min，但原运行 GPU 数未知，且 checkpoint 加载、缓存、evaluation 往往主导耗时。若 Qwen 完全 frozen、hidden/DINO targets 已缓存，500-step adapter run 可能很短。

历史 500-rollout 约需 3–6 GPUh，因此：

- 500 rollouts：约 3–6 GPUh；
- 15 个短 adapter runs、cache、head pretraining：可能约 1–2 GPUh；
- 总体约 4–8 GPUh，正好处于边界。

先实测 frozen-Qwen/DINO cache、future-head pretraining 与 strict gate、一个完整 500-step adapter run、20-rollout wall time。随后计算：

`T_cache + T_head + 15*T_adapter + 25*T_20rollout + analysis overhead`

GPUh 按物理 GPU 数乘 wall time，并保留至少 10% 余量。若完整上限外推超过 **7.2 GPUh，立即停止**。

缓存必须保证 Qwen frozen/eval、预处理确定、无被缓存抹掉的随机图像增强或 dropout、三臂读取相同 cache、future head 从同一初始化/预训练 checkpoint 克隆。

## 最近工作后的精确 delta

- **PFD**：最危险近邻。相同问题、future-specific correction、small output adapter、pure-finetune 与 shuffled-future controls；PGM 只多出更严随机化、gradient-norm matched placebo、strict world gate 和 representation necessity audit。
- **VLAFlow**：已比较 action-only 与 future-latent objectives，并报告 future fidelity 与成功相关；没有随机 gradient routing 或 representation intervention。
- **VLA-JEPA**：已用未来 latent objective 塑造 latent-action/VLA representation，但没有三臂因果归因。
- **SelfWAM**：clean demonstrated action 条件化 future queries，并做 action sensitivity；说明 action-conditioned future 本身不保证政策收益。
- **CheckVLA**：已有 retrained action-shuffled predictor，但 world model 与 policy 分离，无梯度进入 VLA。
- **DynaMo**：latent forward/inverse dynamics pretraining 改善下游 representation，但不是 VLA，也不做 predictive-gradient 因果识别。
- **Output-Level Regularization**：揭示 VLA seed lottery；不涉及 future objective，但直接支持 paired multi-seed 设计。
- **ProgressVLA**：可微 world-model gradient 作用于 latent actions，用于 diffusion inference guidance/RL，而非 deterministic VLA 训练表征诊断。
- **Embodied Interpretability**：VLA 因果干预对象是视觉输入区域，不是 randomized future-treatment delta subspace。

## 最窄可辩护主张

> 在 frozen-backbone、deterministic StarVLA 的低秩 action interface 上，允许一个通过严格 held-out validity gate 的 future-latent objective 回传梯度，相比 stop-gradient 和 support/gradient-norm matched deranged-future placebo，在两个预注册非饱和任务上产生一致的闭环收益；cross-fitted treatment-delta subspace removal 表明该收益依赖新增的 future-sensitive interface component。

不得声称新 future objective/adapter/WAM、重塑 Qwen、SOTA、完整 causal mediation、排除所有 generic auxiliary regularization，或对 LIBERO/VLA 普遍成立。

## Fatal gates

任一失败即 **NO-GO**：

1. Correct predictor 未在 episode-disjoint/time-embargo holdout 同时胜过 persistence、action-agnostic baseline，或对 action shuffle 不敏感。
2. C 无法做到无泄漏 derangement和 batch-level adapter-gradient norm matching。
3. A−B 或 A−C 的五个 seed 差值不是全部非零且为正。
4. C 出现明显优化崩溃，导致 A>C 只能解释为 placebo 有害。
5. 500-step pilot 尚未稳定，或效果只来自 action-loss/gradient clipping 异常。
6. 300-rollout主门失败却继续做 representation intervention。
7. Predictive removal 未使用 cross-fitting 及 matched-rank、matched-energy orthogonal placebo。
8. 实测总预算外推超过 7.2 GPUh。
9. 仍以 mediation/new method 而不是 causal diagnostic/necessity 作为主要贡献。

最终建议：**按修订方案 CONDITIONAL-GO，作为高门槛、可被快速证伪的诊断实验推进；新颖性为高重叠下的窄协议增量。**
