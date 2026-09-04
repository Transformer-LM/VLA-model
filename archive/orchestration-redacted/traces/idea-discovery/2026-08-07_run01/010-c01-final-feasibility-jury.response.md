# C01 final feasibility jury

## 最终裁决：NO-GO

**Score：3/10**  
**Assurance：same-family，provisional**

当前精简协议不能形成 reviewer-defensible 的最终机制诊断；最多只能作为探索性 feasibility pilot，不能据此启动面向最终结论的训练。

## Fatal blocker：past row 不是可比的反事实

- 当前/未来动作不可能因果地产生过去状态，只能称 `past-associated`，不能称 `past-correct`。
- 若输入过去动作，它变成逆动力学任务；若输入当前之后的动作，它只是轨迹阶段、行为策略和状态历史的代理。
- 即使按 task/phase/proprio/action-norm 做 support-matched shuffle，也不能匹配条件联合分布、Bayes risk、梯度噪声或接触不可逆性。
- 正 interaction 因而可能只反映 future-shuffle 比 past-shuffle 遭受更矛盾的监督，而非 future-intact objective 形成有用预测表征。

去掉这一因果解释后，剩下的只是四种 training recipes 的描述性交互；不足以支撑 H1。

## 统计与预算

- 真正的算法级重复单位是训练 seed，不是 rollout。3 个配对 seeds 的单侧符号检验最小 p=1/8=0.125。
- 每任务每格 54 episodes 时，成功率约 50% 的四格 interaction 标准误约 13.6 pp/task；合并两任务仍约 9.6 pp。对 10 pp 效应的乐观功效不足约 40%，加入训练 seed 方差后更差。
- 相邻的 frozen-encoder VLA-JEPA 工作使用 9–13 seeds 才暴露 seed lottery，并发现 world-latent 指标不能预测 closed-loop success。
- 原精简协议保守约 9–13 GPUh；加入最低必要 controls 约 15–22 GPUh；更可信的 >=5 seeds、>=50 starts 约 35–55 GPUh。

## 最近工作后的 novelty delta

VLAFlow 已占据 shared future-latent shaping、受控 objective comparison 与 removable auxiliary；SelfWAM 已占据 demonstrated-action-conditioned future prediction 与 action perturbation；CheckVLA/dWorldEval 已覆盖 shuffled-action controls；Output-Level Regularization 已覆盖 frozen encoders、joint world/action heads、多 seed closed-loop 与 latent/SR 解耦。

C01 只剩“加入 past 行的完整 factorial”。past placebo 一旦无效，novelty delta 基本消失。

## 若未来放宽预算的最低修改

需要将 past cells 明确降为 associated controls；加入 action-only、no-action predictor、dummy/noise target、LowLR/output-level regularization；在 policy outcome 前完成独立 strict future gate；固定 early checkpoint；至少 5、最好 8+ training seeds，每 seed/task 约 50 paired starts；并加入 stop-gradient 或 predictive-subspace intervention，才能讨论 representation mechanism。

结论：当前 8 GPUh 与 cycle-3 边界下应记录 evidence-gated NO-RUN；不要训练一个无法支撑主张的协议。
