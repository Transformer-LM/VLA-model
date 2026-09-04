+# Robotics Idea Discovery Report

**方向**：反馈式 VLA × WAM 的跨动作误差迁移与可审计反例  
**日期**：2026-08-31  
**Pipeline**：research-lit → robotics framing → novelty-check → matched-pilot  
**当前决定**：ISRAC 单一候选，实验门前暂不宣称 novelty > 7

## Robotics Problem Frame

- **Embodiment**：LIBERO Franka 单臂操作为第一平台；RoboTwin 为第二平台候选；不自主启动真实机器人。
- **任务族**：跨任务语言条件操作；从冻结 StarVLA 的自然成功轨迹提取相邻 factual/candidate action chunks。
- **观测/动作接口**：main RGB、wrist RGB、depth、proprio；StarVLA 8×7 continuous action chunks。
- **学习设置**：反馈式 action-conditioned WAM 的执行验证、候选评价或 correction audit；编译器本身不训练 WAM。
- **可用资产**：4×A100-40GB、StarVLA checkpoint、LIBERO rollback、缓存成功轨迹；远端仅可写个人目录。
- **安全约束**：无触觉；当前只做 simulation；不进行真实机器人运动。
- **贡献类型**：methodological diagnostic/compiler，而不是新的 video generator 或 action head。

## 唯一保留 Idea：ISRAC

**全称**：Influence-Separated Residual-Alias Compiler  
**中文**：影响分离的残差别名反事实编译器

### 核心问题

反馈式 WAM 可能把一个已执行 factual action 暴露的 prediction residual，用来修正或排序另一个尚未执行的 candidate action。若同一 factual feedback interface 在两个合法物理世界中完全相同，而 candidate 的真实效果不同，则单一 residual 本身不足以决定候选动作的正确修正方向。

### 核心机制

1. 从冻结 VLA 的自然成功轨迹取得 factual chunk、未来 policy-supported candidate suffix 和可恢复边界；
2. 建立 simulator-native contact/activation trace；
3. 筛出对 factual 动态转录影响为零、但会被 candidate 激活的物理参数块；
4. 在预注册物理范围内生成 `theta+` / `theta-`；
5. 输出两层分离证据：
   - **model-free compiler certificate**：factual RGB/depth/proprio/动态 simulator state 相等，candidate 参数激活与首次物理分歧对齐；
   - **post-hoc WAM audit**：pair 冻结并哈希后，才加载目标 WAM 测 residual transport、ranking inversion 和 correction harm。

这里的“state equality”只指 rollout 的完整动态状态，不包含本来就故意不同的静态物理参数配置；参数配置单独哈希。

### 一句话 novelty delta

> 不同于现有 VLA metamorphic testing 对成功 rollout 施加预定义场景变换后检查整段行为应同或应变，ISRAC 在不读取目标 WAM score 的条件下，自动搜索对 factual action 全动态转录零影响、却仅被未来 policy-supported candidate 激活的合法物理参数对，并输出 equality–activation–first-divergence 证书，以形成反馈残差跨动作不可识别性的可审计 embodied witness。

### Benchmark 与最小 pilot

- **第一平台**：LIBERO Goal，冻结 StarVLA 成功轨迹；
- **现有 feasibility evidence**：8 个自动筛选边界中 6 个通过，产生 24 个 certified pairs；另保留 2 个失败边界；
- **当前运行**：candidate-contact 与 random-scene 各 3 selector seeds、8 个边界、相同物理值与每块 8 次 rollout；
- **后续强 baseline**：grid、CMA-ES、Ghosh-style BO、BEACON-style BO+CMA；
- **指标**：certified pairs / 1k simulator rollouts、calls/pair、passing-block rate、失败原因、paired bootstrap CI；
- **正信号**：ISRAC 相对最强 matched-call baseline 的 yield ratio ≥2，并跨两个物理机制族与第二 simulator 重现；
- **kill**：最佳 matched-call baseline 等效/更好，或 pair 依赖任务脚本、action-indexed 开关、宽阈值、低支持动作、target-WAM leakage。

## Novelty Gate

同家族独立上下文 reviewer 的结论：

- **matched-call 之前**：6.6/10，区间 6.1–7.2；不得宣称 >7；
- **稳健 matched-call 优势后**：7.4/10，区间 7.0–7.9；
- **最危险近邻**：Metamorphic Testing of Vision–Language Action–Enabled Robots；
- **精确被测接口近邻**：Feedback World Model；
- **一般理论近邻**：Imperfect World Models are Exploitable；
- **搜索 baseline 近邻**：controller BO falsification、BEACON、constraint-supported metamorphic testing。

因此 ISRAC 不是已经确定的新方法，而是一个正在通过实验争取 >7 新颖性的候选。

## WAM Role

- **Compiler representation**：privileged simulator-native physics/contact trace，仅用于离线生成证书，不是部署输入；
- **被测 WAM**：优先 latent/action-conditioned feedback interface，后续可扩到 pixel/video WAM；
- **Control use**：U3 candidate evaluation / runtime correction audit；
- **Policy**：冻结 StarVLA；不把 policy finetuning 当第一门；
- **禁止混淆**：compiler yield 与 WAM harm 是两个独立 claim；前者通过后才允许启动后者。

## 已淘汰或降级路线

- **generic WAM prediction-error correction**：被 Feedback World Model、ReDRAW、CheckVLA 等强重叠；
- **candidate-specific residual transport head**：存在 candidate-only bypass，无法识别 residual 的 load-bearing 作用；
- **普通 WAM reranking**：被 tau0-WM、DREAMSTEER、WorldEval 等占据；
- **仅做 paired VLA metamorphic testing**：不足以超过已有 VLA metamorphic testing；
- **Depth/PointMap auxiliary prediction**：可以作为以后 WAM representation ablation，不是当前核心 novelty。

## Evidence Package

- 必须报告所有失败与未筛选边界，不只展示通过样本；
- pair 必须在任何目标 WAM 加载前冻结、哈希；
- 同参数 repeat noise 界必须预先固定；
- 假 action-indexed/scripted switch 必须 100% 被证书拒绝；
- 必须有 matched simulator-call baseline 和至少 3 compiler seeds；
- 若主张 WAM 诊断价值，至少两个 held-out feedback methods 的 harm 必须高于 severity-matched 普通扰动；
- 真实机器人不是当前 gate，后续只能在单独安全协议和操作员批准下进行。

## 当前下一步

1. 完成正在运行的 8-boundary × 2-baseline × 3-seed pilot；
2. 根据 raw JSON 计算 yield ratio 与 CI；
3. 若未过 2× 门，加入强 BO/CMA baseline 后重新判定，不能直接训练大 WAM；
4. 若门通过，再使用空闲 A100 启动 frozen feedback-WAM harm pilot。
