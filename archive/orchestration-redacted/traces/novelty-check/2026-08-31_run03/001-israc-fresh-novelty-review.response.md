## 结论

ISRAC **没有被当前可核验文献完整覆盖**，但其组件分别已有强先例；剩余新意是一个较窄的组合贡献：**WAM-blind、action-separated 的 simulator-native twin compiler，加 equality–activation–first-divergence 证书**。当前 24 对 LIBERO pilot 只支持可行性，不支持方法新颖性或 WAM harm。

检索基础设施存在三次 arXiv TLS EOF 和一次 DBLP 503/429，因此“未发现完整同构工作”只能是条件性结论；下述最近邻均通过论文正文或作者存档稿核验。

## 精确最近邻与四轴重叠

四轴为：①问题设定；②核心机制；③关键洞见；④应用域。

| 最近邻 | 问题设定 | 核心机制 | 关键洞见 | 应用域 |
|---|---|---|---|---|
| [Metamorphic Testing of Vision–Language Action–Enabled Robots](https://arxiv.org/html/2602.22579), Valle et al., 2026 preprint | **强重叠**：从成功 VLA source cases 生成 source/follow-up pairs | **部分重叠**：预定义 prompt/scene transformations 与轨迹一致/变化关系；没有 factual-action conditioning、candidate-only activation 或三段证书 | **部分重叠**：关系式 oracle 可暴露单次成功判据漏掉的错误 | **完全重叠**：VLA、仿真机器人、成对轨迹测试；这是整体最近邻 |
| [Feedback World Model Enables Precise Guidance of Diffusion Policy](https://arxiv.org/html/2605.15705), An et al., 2026 preprint | **强重叠**：执行后 residual 修正未来 candidate prediction/guidance | **部分重叠且危险**：式(9–12)把反馈残差带到下一决策，式(14–16)显式计算 action controllability；但不构造物理 twin 或证书 | **部分重叠**：反馈与 action relevance 必须结合；未研究同 residual 的跨 action 不可识别性 | **完全重叠**：LIBERO/Robomimic 操作与 action-conditioned WM |
| [Imperfect World Models are Exploitable](https://arxiv.org/html/2605.15960), Bhamidipaty et al., 2026 preprint | **部分重叠**：代理模型与真实动力学发生排序反转 | **不同**：有限 MDP 上的定义和理论，不是 witness compiler | **完全重叠**：低预测误差不保证 ordinal ranking 正确 | **部分重叠**：一般 RL/MDP，而非 VLA 操作 |
| [Verifying Controllers Against Adversarial Examples with Bayesian Optimization](https://arxiv.org/abs/1802.08678), Ghosh et al., ICRA 2018 | **部分重叠**：在参数化模拟器中自动寻找控制反例 | **部分重叠**：BO 搜环境/物理参数，逻辑轨迹谓词作约束 | **部分重叠**：利用 specification structure 提高每次仿真的发现率 | **部分重叠**：机器人控制器，不是反馈 WAM/VLA |
| [BEACON](https://doi.org/10.1109/ACCESS.2024.3436515), Yancosek & Baheri, IEEE Access 2024 | **部分重叠**：仿真 falsification | **部分重叠**：BO+CMA-ES 搜索并优化反例/调用效率 | **部分重叠**：反例 yield per simulation 是核心贡献指标 | **不同/部分**：一般控制系统 |
| [Using Constraint Solvers to Support Metamorphic Testing](https://doi.org/10.1109/MET.2019.00013), de Castro-Cabrera et al., MET 2019 | **部分重叠**：自动生成 follow-up tests | **强部分重叠**：把 MR 编成约束，检查矛盾并生成测试 | **部分重叠**：机器可检查关系证书 | **不同**：通用软件测试，无物理/VLA/action separation |

最危险的是 Valle et al.：它已经占据“成功 VLA 轨迹 + 成对仿真变换 + 轨迹关系 oracle + 跨模型/机器人测试”四块中的大半。FWM 则精确占据了 ISRAC 想诊断的反馈接口。

## 新颖性分数

- **matched-call 结果之前：6.6/10，合理区间 6.1–7.2。**  
  **不宜主张 >7。** 当前 LIBERO 的 24 对 certified pairs 证明“能生成”，没有证明 influence separation 比约束 MT、BO、CMA-ES 或一般 falsification 更有方法价值。

- **若获得稳健 matched-call 优势后：7.4/10，合理区间 7.0–7.9。**  
  **>7 可以辩护，但必须是**相对最强 random/grid/CMA-ES/**BO/BEACON** 的预注册同预算优势，最好达到计划中的 ≥2×，且在至少两个物理机制族、多个任务及第二模拟器上成立。单一 LIBERO 设置的一次显著胜出仍然偏弱。

## 一句话 delta

> 不同于 Valle et al. 将成功 VLA rollout 施加预定义 prompt/scene 变换后检查整段轨迹应同或应变，ISRAC 在不读取目标 WAM 分数的条件下，从冻结 VLA 的自然轨迹自动搜索对 factual action 全动态转录零影响、却仅被未来 policy-supported candidate 激活的合法物理参数对，并输出 equality–activation–first-divergence 证书，从而把一般行为不一致收窄为可审计的反馈残差跨动作不可识别见证。

## Fatal overlap / kill condition

文献层面的致命重叠是：任何先前工作已经同时实现以下全部条件——成功冻结 VLA 源轨迹、完整 factual 动态转录相等、candidate-only simulator-native 参数激活、未来物理效果分叉、三段机器证书，以及搜索期间不读取目标 WAM 分数。若 Valle et al. 的补充材料或代码实际包含这一组合，ISRAC 基本被 scoop。

实验层面的 kill 是：最佳 matched-call BO/CMA/grid baseline 的 certified-pair yield 与 ISRAC 无显著差异或更高；或者结果依赖 task-specific/action-indexed 开关、低支持候选、宽松阈值或目标 WAM 泄漏。

另有两个必须先修正的定义风险：

- 若“full state”包含静态世界参数，`θ+ ≠ θ−` 与 state equality 逻辑矛盾；应明确为“完整动态 rollout state”，参数配置另行哈希。
- 若 residual 依赖目标 WAM，就不能同时说 compiler 从未读取它并由 compiler 直接认证 residual；应把 model-free compiler certificate 与 pair 冻结后的 post-hoc WAM residual audit 分开。

## 支撑 >7 的最低实验包

1. 用重复 replay 标定噪声上界，逐帧证明 RGB/depth/proprio/完整动态 state 相等，并记录参数首次激活和 candidate 首次分叉；假开关必须 100% 被拒绝。
2. 相同 snapshots、candidate bundle、参数范围和 simulator-call 预算下比较 random、grid、CMA-ES、Ghosh-style BO、BEACON-style BO+CMA；报告 pairs/1k calls、calls/pair、paired bootstrap 95% CI，最佳基线的 yield ratio 下界需明显大于 1，理想为 ≥2。
3. 至少两个真正不同的物理机制族、多个任务、≥3 compiler seeds；要稳守 >7，加入第二模拟器且零任务专用规则。
4. 在加载任何目标 WAM 前冻结 pair、搜索日志和哈希；WAM 分数只允许在冻结后计算。
5. 若论文还主张反馈 WAM 诊断价值，则至少两个未参与编译的 feedback methods 在 alias set 上出现高于 severity-matched 普通扰动的 false transport/ranking harm，同时 feedback-free WAM 不出现同等退化。
