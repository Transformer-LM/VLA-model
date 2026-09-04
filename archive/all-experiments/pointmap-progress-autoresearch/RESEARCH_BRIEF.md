# Research Brief

**Status:** selected idea; autonomous validation authorized  
**Scope:** research only; paper writing and real-robot execution are disabled

## Problem anchor

用户在复现 π0.5 时遇到的核心问题是：长时序任务容易丢失“已经做过什么、当前关系是否仍成立”的进度记忆，并在子步骤失败、物体被碰出容器、堆叠坍塌或遮挡后继续执行，造成 false completion 与不可恢复失败。

## Selected direction

验证以 PointMap/对象相对几何代替完整 Depth 视频是否有决策价值。研究对象不是“让深度预测更准”，而是：对象可寻址的稀疏三维几何证据，能否在 action-conditioned belief update 中验证或撤销任务关系，并改善后续动作选择、停止或恢复。

工作假设：

> 在外观含混、遮挡或已建立关系随后失效的长时操作中，将对象相对 PointMap/metric geometry 作为动作条件的关系证据，比 RGB-only memory 或被动 3D auxiliary loss 更可靠地减少 false completion，并改善恢复决策。

## Minimal mechanism

1. 冻结或复用 VLA；不从头训练完整 RGB-D video diffusion WAM。
2. 从真实观测或仿真真值构造对象地址、目标/容器/末端的稀疏 PointMap 与相对位姿。
3. 预测或直接判定执行 action chunk 后关系 `inside/on/grasp/open` 是否建立、保持或失效，并估计置信度。
4. 用该证据更新持久 progress belief；关系失效时撤销对应进度并触发重新观察、停止或恢复。

## Required gates

1. **Oracle headroom:** ground-truth geometry/relation evidence 必须显著改善 progress/false-completion/recovery；否则停止。
2. **Representation necessity:** PointMap/对象相对几何必须优于匹配容量的 RGB-only verifier、proprio/action-only verifier 与直接 relation classifier。
3. **Mechanism necessity:** 去掉 object address 或 action conditioning 后收益应下降；否则缩小 claim。
4. **Decision relevance:** 只改善 depth/pose RMSE 而不改善决策或闭环结果视为失败。

## Experimental scope

- 首个 pilot 使用服务器个人目录内已安装的 LIBERO、轨迹、StarVLA/OpenPI 资产。
- 任务应覆盖多种关系和扰动，不绑定“双臂搬箱”：容器放置后移出、堆叠后坍塌、抓取后滑落、相似物体交换/遮挡、相机视角变化；纯颜色语义任务作为 geometry-negative control。
- 至少三个 dataset/evaluation seeds；保存逐样本预测、原始日志、配置、checkpoint/hash 与 GPU-hour ledger。

## Constraints

- 远程仅使用 `liu_meng`，仅读写 `<PERSONAL_RESEARCH_ROOT>`。
- 禁止 root/sudo/su、共享/团队目录、`.bashrc`、全局 Conda、系统 CUDA 与远程下载。
- 优先 GPU 2/3；GPU 0/1 仅在逐卡确认空闲时使用；禁止抢占或共享。
- 预算上限：pilot 32 GPUh，总计 400 GPUh；无付费算力。
- 本轮真实机器人 trials 为 0；精确真实机器人方案需另行明确授权。

## Success condition

最小成功证据是：在预注册的关系失效/恢复测试上，PointMap geometry belief 在多种子下减少 false completion、提高 invalidation recall 与 recovery success，并且这些提升不能由匹配容量 RGB 或直接 action scorer 解释。
