# Review Summary

日期：2026-08-24  
轮数：1  
最终分数：5.2/10  
最终裁决：RETHINK；oracle diagnostic pilot GO

## 评审核心意见

- 方案只覆盖错误进度写入的预防，不能声称解决全部遗忘、纠错和恢复。
- π0.5 是否真正消费持久 progress assertion 必须先验证。
- factual oracle 不可被 regret gate 合法超越；否则是在做 policy steering/deception。
- finding 与 method 必须分开：先证明 harm heterogeneity，再证明部署特征可预测并改善闭环。
- WAM、planner、retraction graph、联合 recovery 均不应加入首轮。

## 已执行修改

- 将主项目改为 diagnostic-first 的 Causal Progress Harm Audit。
- 把 oracle truth 改为 ceiling，而非待击败 baseline。
- 将 regret 用途限制为 false-positive cost weighting，不允许 false-beneficial 写入。
- 分开 admission effect 与 correction effect。
- 增加 P0 progress-interface headroom 查杀。

## 当前剩余风险

- 新颖性主要来自 VLA-specific causal measurement，而不是通用学习原理。
- 若 P1 只有“错误代价不均匀”的平凡结论，论文价值不足。
- 若 harm 无法由部署时可见信息预测，只能保留诊断 finding。
- 若简单 action divergence/value critic 等价，必须删除新方法 claim。
