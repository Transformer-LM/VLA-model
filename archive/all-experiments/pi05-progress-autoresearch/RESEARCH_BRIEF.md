# Research Brief — 长时序 VLA 的可靠进度、验证与恢复

**状态：** ready-for-discovery；已选定方向，自动 Idea 发现与实验规划  
**范围：** 研究与实验设计；论文写作关闭；本轮不启动 GPU 或真实机器人

## 现实问题

用户已经复现 π0.5，并在长时序、多阶段任务中观察到：策略会遗忘已完成步骤、误判动作成功、错误推进任务，以及在失败后无法恢复。需要判断这些失败来自历史缺失、任务进度误判、低层动作能力、固定 action chunk，还是恢复数据不足。

## 研究目标

自动寻找一个不以“再加一个通用 memory module”为创新、能够被严格查新、可由 π0.5 或另一可复现 VLA 验证的研究 Idea。WAM 仅在其能提供普通 VLM、状态机或几何 verifier 无法提供的机制增益时采用。

## 必须避免的重复

- 最近帧拼接、普通 RNN/Transformer history encoder；
- 通用 keyframe memory；
- 仅把执行历史总结成语言；
- 普通高层 VLM 分解任务、低层 VLA 执行；
- 无校准的 verifier + replan；
- 将 MemoryVLA、HAMLET、KEMO、LoHo-Manip、Goal2Skill 或 Explicit Language Memory 做组件替换。

## Idea 通过门槛

1. 明确区分 forgetting、progress misclassification、motor failure 和 recovery failure；
2. 相对最近工作具有可陈述、可查新的机制差异；
3. 有一个廉价 oracle 或反事实实验可在大规模训练前证伪；
4. baseline 至少包含 memory-free VLA、最近记忆方法、oracle progress 和必要的 verifier/recovery 对照；
5. 端到端成功率之外，必须测量任务状态准确率、完成验证、校准、错误回滚和恢复；
6. 额外参数、数据、计算和交互必须匹配或单独核算。

## 资源与权限

- 可使用用户的 π0.5 复现、4 张 A100 和真实机器人作为后续资源；当前阶段只做到 Idea 与实验计划。
- 远程仅允许用户 `liu_meng`，仅允许 `<PERSONAL_RESEARCH_ROOT>`，禁止团队或共享目录、root、sudo、su、修改 `.bashrc`、全局 Conda 和系统 CUDA。
- GPU 2/3 优先；GPU 0/1 只有在每次启动前确认空闲时才可使用，绝不抢占或共享已有实验。
- 真实机器人执行必须在 Idea 和计划通过后，针对精确动作、安全边界和试验次数另行确认。

## 本轮交付

- 候选 Idea 及拒绝理由；
- 最近工作碰撞矩阵；
- 自动选出的一个主 Idea；
- 可证伪假设；
- 分阶段实验矩阵、baseline、oracle、消融、指标、统计与停止条件；
- 是否值得进入实现阶段的明确结论。
