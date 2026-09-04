**严格新颖性分数：6.8/10 — FAIL**  
门槛要求 `>7.0`，因此不授权 E0。

**Naturalness：中等。** 系统动机自然，但核心研究对象高度工程化：固定五步 suffix、command-only envelope、族特定的可见性/投影分离阈值和 two-frame persistence 共同定义了 `τ_protocol`。它更像经过严密审计的监督标签与归纳偏置，而非自然产生的新验证原语。

**最近的精确机制/组合：**

- [POT-VLA](https://arxiv.org/html/2607.18016) 已在 action-chunk boundary 用 containment/support/grasp 等几何谓词更新任务进度；不可见、低置信或不稳定证据返回 `uncertain`，并驱动 continue/reobserve/replan。它最接近 WitnessWAM 的 relation、三值状态和 consumer。
- [CheckVLA](https://arxiv.org/html/2607.26789) 已组合 committed action chunk、action-conditioned world model、到达中的真实观测、first-crossing trigger、历史 keyframe evidence 与执行期验证；差别是它修改 suffix，而 WitnessWAM 只暂存关系信念。
- [Foresight](https://arxiv.org/html/2606.23085) 已使用 action-conditioned future latents、完整因果历史和首次阈值交叉做长时执行失败监测；其监督只有 terminal success/failure。
- [PATCH](https://arxiv.org/html/2606.16690) 已从 active chunk 投影 evidence corridor，预测局部 latent evolution，并以 persistence/latching 过滤瞬时遮挡后触发 intervention。
- 三值 `true/false/inconclusive` 和“尽早给出可确定 verdict”本身属于经典 [LTL3 runtime verification](https://www.isp.uni-luebeck.de/research/publications/runtime-verification-ltl-and-tltl-0)；带系统假设和部分可观测性的 unknown verdict 也已有 [ABRV](https://link.springer.com/chapter/10.1007/978-3-030-32079-9_10)。
- [ConditionNET](https://arxiv.org/html/2502.01167) 已逐观测验证动作 precondition/effect；[ETL](https://arxiv.org/html/2605.12651) 已在视觉 embedding trace 上监测 grasp 等感知谓词。二者没有 suffix-conditioned opportunity survival target。
- [Silent Manipulation Failures](https://arxiv.org/html/2606.03134) 研究终局真假成功的感知可恢复性；[IntentVLA/AliasBench](https://arxiv.org/html/2605.14712)、[EvoScene-VLA](https://arxiv.org/html/2605.21862) 和 [Mem-World](https://arxiv.org/html/2606.18960) 的 consumer 分别是动作生成、政策内 scene belief 和 imagined rollout，并不直接更新外部关系记忆。

**Fatal reviewer objection：**  
`τ_protocol` 并非新发现的物理事件，而是 privileged geometry、visibility、pairwise projected separation、noise floor 与 persistence 阈值共同规定的首个规则交叉点。由于 WitnessWAM 与完整历史 verifier 都只在相同 chunk boundary 影响同一 FSM，显式 `τ` 不增加可用信息或决策能力；它只告诉模型该注意哪一帧。POMDP observation models、三值 monitorability、POT-VLA 的 `uncertain` predicate gating，以及 CheckVLA/Foresight 的 action-conditioned first-crossing monitoring 已覆盖其原则性组成。因此 reviewer 可将贡献降格为“手工机会标签辅助的 temporal-attention supervision”，而不是新的 WAM/执行验证机制。

**不可约 delta：**  
与 POT-VLA/CheckVLA 不同，WitnessWAM 用自然反事实关系对和 interval-censored privileged labels，学习在不可修改的五步 VLA suffix 下，两种保持不变的物理关系状态首次能被被动 RGB/proprio 区分的时间，并只将该时刻取得的证据暂存给 boundary-level 外部关系记忆更新。

**Claim ceiling：**  
最多可声称：**在预注册五步、关系保持的模拟 continuation contract 内，显式 earliest-opportunity supervision 是外部 relation-memory verification 的一种有效归纳偏置，并优于可见性调度和 capacity-matched buffered-history verification。**  
不能声称新的部分可观测性原理、通用三值 runtime monitor、新 WAM 范式、物理真值认证或一般 VLA execution verification。
