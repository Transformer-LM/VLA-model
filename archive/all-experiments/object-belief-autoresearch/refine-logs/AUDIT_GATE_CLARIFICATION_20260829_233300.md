# Audit Gate Clarification: Homogeneous Episode-Level Correlation

v4 12k audit 在任何模型训练前停止。全部 identity-relevant 项通过：heterogeneous regime0 的 property–position correlations 为 0.015/0.022/0.027，OOD regime2 为 0.048；permutation、contact、mapping、equivariance 均通过，`hard_id=242`。

唯一失败是 homogeneous regime1 的 pooled property–position correlation。该 regime 中同一 episode 内所有对象地址共享完全相同的 mass/friction，因此这一 episode-level nuisance 不能区分 episode 内哪个对象地址是谁；同时把三个共享 property 的对象样本当独立样本会低估相关容差。独立代码审查确认：

- regime1 correlation 继续完整报告，但不作为 identity leakage gate；
- detection permutation 在所有 regime 中保持 gating；
- property–position correlation 在具有对象间物性差异的 regime0/2 中保持 gating；
- 若后续 homogeneous split 出现 property-aware assignment 增益，视为异常，不能支持方法，需 episode-level permutation 或新数据 seed 复查。

该澄清未查看任何模型输出；截至此时没有启动 GPU 正式训练。v4 数据无需重生成，因为修订的是 identity-audit 统计解释，而非数据内容或方法配置。

