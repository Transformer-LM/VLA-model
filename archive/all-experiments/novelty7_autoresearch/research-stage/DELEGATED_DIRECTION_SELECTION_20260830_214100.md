# Delegated Macro-Direction Selection

**Run**: `20260830-novelty7-vla-wam`  
**Authority**: 用户已明确授权在扩展母方向后自主选择并继续实验，无需再次等待方向确认。  
**Sensor constraint**: 不使用触觉或力传感器。

## Selected macro-direction

**X8 + X14：Source-aware VLA×WAM verification with counterfactual causal evaluation**

中文：**面向 VLA 执行的来源感知世界模型验证：区分机器人执行失败、WAM 自身失配与观测含混。**

## Why selected

1. 这是一个机器人决策问题，而不是“再加一个 head/Depth/memory”。来源不同会要求不同动作：repair、reobserve、或 distrust/update WAM。
2. CheckVLA 与 When to Trust Imagination 已覆盖 mismatch detection；WAV 已覆盖 world-model self-verification；但三者尚未形成执行期 source-aware interface。
3. 可在冻结 π0.5 与冻结/小型 latent WAM 上验证，不依赖触觉；RGB-D、PointMap、proprio 和 execution traces 已足够。
4. 可以用同初态、同命令、近似同 residual 幅度的 paired interventions 做因果识别，能快速证伪。
5. 与用户的实际问题一致：长时任务失败后，系统不应因 WAM 错误而错误修改进度或反复恢复。

## Alternatives retained

- **V11/X9 functional-geometry HOW generalization**：问题自然，初估 novelty 7.4–7.8；但 GEAR-VLA、Lift3D-VLA、DreamWAM、ForeTime-VLA 和非 VLA 的 GIFT/RPDiff/FMB 构成强边界，且此前三版机制因可执行性/可识别性失败。保留为 fallback 1。
- **V12 feasibility-calibrated VLA**：初估 novelty 7.2–7.6；风险是被精确几何 collision/reachability checker 解释掉。保留为 fallback 2。
- **V13 task-effect equivalence VLA**：ForeTime-VLA 已使用 action-equivalence objective，最新边界使独立 novelty 降低，暂不优先。
- **X12 exploit-resistant WAM interface**：价值高，但 WAV、WoVR、PROWL 与 exploitation 理论已使方法空间拥挤。

## Non-negotiable gate

- 候选 Idea 必须经最近邻全文核查和独立 reviewer，novelty 严格 `> 7.0/10`。
- 若 source-aware verification 不过门槛，结构性切换到 functional-geometry 或 feasibility，而不是改名包装。
- 门槛通过前不启动正式训练；允许只读服务器盘点和 GPU 空闲检查。
