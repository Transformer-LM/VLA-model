# Corrected-Physics Hard-ID Definition

在修复 `mj_setConst` 顺序后的独立 300-episode 预审中，随机布局保持二维，settle displacement q99 为 `7.4e-9 m`。corrected heterogeneous test 的 pose-only margin 10/20/30% 分位数为 0.083/0.090/0.095 m。

正式 v5 在任何模型训练前固定：

`hard_id := mean(top2 pose-distance margin) < 0.095 m AND max object movement > 0.025 m`。

0.095 m 与一个 box 的直径同量级，并约选择 corrected distribution 最困难的 30%，兼顾真正歧义与 paired evaluation 的统计功效。该阈值不再引用已判无效的 v3/v4 分布。

同时，layout sampler 删除可能违反 0.10 m 间距的 fallback；无法放置时整组重采。audit 新增所有 context interaction 的 pusher contact rate，要求 query 与 context 均超过 95%。

