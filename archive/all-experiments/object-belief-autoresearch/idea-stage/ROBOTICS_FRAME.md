# Robotics Problem Frame

- **Embodiment**：先使用现有个人服务器上的 LIBERO / RoboTwin / RMBench 资产决定；方法不绑定单双臂或固定搬箱场景。
- **Task family**：长时、多阶段、对象状态会被动作改变且可能遮挡/混淆的操作任务。
- **Environment**：桌面/家居操作仿真优先，后续可迁移真实机器人；本轮不自动执行真实机器人。
- **Observation**：RGB 为最低要求；若个人资产已有 RGB-D，可把深度/pose 作为训练教师或 oracle，不把专用触觉作为前提。
- **Action interface**：冻结 VLA（优先 π0.5）输出 action chunks；首轮模块只观察实际执行 chunk，并给下一次调用提供对象 belief 或离散干预信号。
- **Learning regime**：imitation/world-model sidecar；先分离 belief estimation 的因果价值，再考虑端到端微调。
- **Available assets**：4×A100；远程仅个人目录 `<PERSONAL_RESEARCH_ROOT>`；服务器无外网；已知用户复现过 π0.5。
- **Compute**：用户取消旧 2/8 GPUh 科研假设；本运行使用 32 GPUh pilot / 400 GPUh 总量作为行政上限。GPU 2/3 优先，0/1 仅逐卡确认空闲后使用。
- **Safety**：无 root/sudo/su；不改 shell/global conda/CUDA；不访问共享目录；不抢占、不与他人共享 GPU。
- **Contribution**：优先机制诊断 + 小型方法，而不是重训完整 7B OA-WAM/EvoScene。

## 需要被证伪的中心假设

在对象混淆、遮挡和动作失败共存时，地址级 action-effect prediction 与 selective correction 相比匹配参数的 global recurrent memory 或直接 verifier，能更准确地保持/撤销对象进度，并改善下一决策。

