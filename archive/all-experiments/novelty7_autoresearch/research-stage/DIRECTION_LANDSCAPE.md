# 扩展母方向版图：不受旧 16 条限制

**范围**: VLA-only、WAM-only、VLA×WAM；排除触觉/力传感器。  
**规模**: 13 条 VLA + 10 条 WAM + 14 条强交叉，共 **37 条母方向**。  
**说明**: 母方向不是论文 Idea。换 backbone、加 Depth、加 memory 或把两个模块串起来，都不自动构成创新。

## A. VLA-only（V1–V13）

| ID | 母方向 | 它真正研究什么 | 当前拥挤度 | 对本项目的可做性 |
|---|---|---|---|---|
| V1 | 数据组成、质量与负迁移 | 哪类 robot/human/video 数据、采样和配比真正产生可迁移 action policy | 极高 | 中低，完整 scaling 太贵 |
| V2 | 语义—对象—空间 grounding | 指令中的对象、参照物、属性和空间关系怎样稳定绑定到动作 | 高 | 中高，可用对象/PointMap |
| V3 | 动作表示、tokenization 与 action manifold | continuous/discrete/flow/diffusion 如何表达多峰且可执行的动作 | 极高 | 中，可换 π0.5 action head |
| V4 | 执行频率、异步生成与 chunk 调度 | policy 推理延迟和环境变化下，何时重算、执行多少步 | 中高 | 高，但 AsyncVLA/CheckVLA 是强近邻 |
| V5 | 长时任务进度、记忆与 belief | 过去做了什么、关系是否仍成立、当前应继续哪一步 | 极高增长 | 高；普通 memory 已不新 |
| V6 | 校准、拒绝、可控与 selective autonomy | VLA 何时应该行动、停下、求助或接受 steering | 中高 | 高；需明确校准对象 |
| V7 | RL/post-training 与从经验自改进 | 从成功、失败、纠正和环境反馈继续学习 | 极高增长 | 中高；反馈污染是风险 |
| V8 | 跨具身、跨坐标和技能迁移 | 不同机器人怎样共享意图或 action effect | 高 | 中，严格新 embodiment 验证成本高 |
| V9 | 3D/4D/对象/功能几何泛化 | 当前物体的 metric geometry 怎样改变抓取、接近和放置 HOW | 高 | 高；“加 3D”已不新 |
| V10 | VLA 诊断、shortcut 与因果评测 | 成功来自语言、视觉、历史还是数据捷径，失效的真正瓶颈是什么 | 中 | 很高，适合先做决定性诊断 |
| **V11** | **功能几何与动作策略拓扑泛化** | **同一语义目标、同一最终关系下，新的对象—参照物配对是否迫使抓取、旋转、接近和放置结构改变** | 中 | 高；必须做 terminal-matched counterfactual pairs |
| **V12** | **物理不可行性与 negative competence** | **对象存在且指令清楚，但几何、开口、碰撞或机器人 reachability 使任务不可行时，能否可靠拒绝或换策略** | 低—中 | 高；须证明不只是确定性 collision checker |
| **V13** | **按任务效果定义的 set-valued action learning** | **把产生相同有效物理关系的多条轨迹视为等价集合，而不是把单条示范当唯一答案** | 低—中 | 中高；须胜过 diffusion diversity + success scorer |

## B. WAM-only（W1–W10）

| ID | 母方向 | 它真正研究什么 | 当前拥挤度 | 对本项目的可做性 |
|---|---|---|---|---|
| W1 | action-conditioned RGB/video future | 动作是否真实控制未来视频，而非只生成合理画面 | 极高 | 低，从头训大视频模型昂贵 |
| W2 | control-sufficient latent / endpoint / edit | 什么最小未来表示足够支持控制 | 极高增长 | 中；Fast/LaWAM/ImageWAM/LAWA 已拥挤 |
| W3 | 对象、PointMap、3D/4D 动力学 | 预测对象姿态、point flow、关系与几何未来 | 高 | 高；必须连接决策而非只降 RMSE |
| W4 | action causality 与 controllability | 模型是否真的区分不同 intervention/action effect | 中高 | 高；WAV 是强近邻 |
| W5 | temporal abstraction、多 chunk 与长时 memory | 如何跨秒/分钟保持可控、可延伸的动态状态 | 高 | 中；Next Forcing/WALL-SS 已推进很快 |
| W6 | world-model validity、OOD 与校准 | 何时可以相信 predicted future，何时模型自己错了 | 中高 | 很高 |
| W7 | planner exploitation 与保守世界模型 | 搜索是否利用模型漏洞，如何限制风险与 horizon | 中高 | 高，但理论和方法近邻多 |
| W8 | system ID 与 test-time adaptation | 新相机、负载、几何、动力学下怎样更新模型 | 中 | 中高；安全 probing 较难 |
| W9 | 人类视频、LAM 与跨域 action effect | 从无 robot action 标签视频学习可执行变化 | 高 | 中；映射到执行动作是瓶颈 |
| W10 | 蒸馏、量化、缓存与实时部署 | 让 WAM 满足控制延迟、显存和吞吐约束 | 中高 | 高；偏系统型贡献 |

## C. VLA×WAM 强交叉（X1–X14）

| ID | 母方向 | WAM 在系统中的因果角色 | 当前拥挤度 | 剩余空间 |
|---|---|---|---|---|
| X1 | predictive objective 塑造 VLA | 训练期 future objective 改变 policy 表征 | 极高 | 很窄；DreamWAM/Robust-WAM/ForeTime 已压缩空间 |
| X2 | joint World–Language–Action 模型 | 同一模型联合世界、语言、动作 | 极高 | 规模和 matched-control 门槛高 |
| X3 | 候选动作 rollout/rerank/MPC | 想象候选后选择或修正 | 极高 | 普通 reranking 不再新 |
| X4 | 执行期验证、adaptive chunk 与恢复 | predicted future 对照现实并触发 replanning/repair | 高 | CheckVLA/When-to-Trust 已占检测与修复 |
| X5 | WAM reward/value/progress/evaluator | 输出 progress、success、critic 或 policy ranking | 高 | 需证明超过 direct scorer/VLM judge |
| X6 | imagined data、RL 与 policy–world 共演化 | WAM 生成经验或作为环境训练 VLA | 极高增长 | exploit 与共同漂移仍开放但重 |
| X7 | WAM 支持的 memory/belief/progress | future/observation 更新长时知识状态 | 高增长 | 普通 memory、event、retraction 已拥挤 |
| **X8** | **disagreement 来源归因** | **区分执行失败、WAM 自身失配、观测含混，并采取不同干预** | **低—中** | **新增母方向；问题自然、可做 paired causal test** |
| **X9** | **功能几何驱动的 HOW/策略结构泛化** | **新对象对几何是否要求改变抓取/对准/接近/放置结构** | **中** | **新增母方向；3D祖先强，benchmark delta 尚可防守** |
| X10 | 跨具身 action-effect 接口 | 共享物理效果并翻译回 native action | 中 | 证据薄但验证重 |
| X11 | active perception / information gain | WAM 选择移动视角、等待或重新观察 | 中低 | 空间大；需显式信息收益而非普通重规划 |
| **X12** | **support-aware / exploit-resistant WAM 接口** | **只在有数据支持的动作上使用 WAM，并检测优化器钻漏洞** | 中 | 新母方向拆分自旧安全方向；近邻 WAV/WoVR/PROWL |
| **X13** | **部署时 policy–world 联合适应与独立锚定** | **两者在线更新但用独立 ground truth 防共同学错** | 中低 | 开放但闭环成本高 |
| **X14** | **counterfactual benchmark 与因果可识别性** | **用同初态、干预匹配和 nuisance controls 判断 world path 是否真有用** | 低—中 | 诊断型贡献空间较大 |

## D. 与旧 16 条的关系

- 旧 H1–H16 均被覆盖，但不再是一对一边界。
- 新增且值得单独成母方向的是 **V11、V12、V13、X8、X9、X12、X13、X14**；V3/V4/V6/V10 与 W2/W4/W6/W7/W10 也比旧图拆得更细。
- 旧 H3 中的触觉分支已删除；只保留 RGB-D、PointMap、3D、proprio 与视觉 contact proxy。
- 旧 H10“预测安全/恢复”被拆成 X4（检测与修复）、X8（错误来源）、X12（防利用），因为三者的假设、标签和实验不同。

## E. 第一轮筛选

按问题自然性、最近邻密度、π0.5 适配、非触觉可验证性和四卡 pilot 速度，优先级为：

1. **X8 disagreement 来源归因**：当前最干净；必须和 CheckVLA、When-to-Trust、WAV、旧 failure+OOD monitor 做严格对比。
2. **X9 功能几何 HOW 泛化**：问题真实，但不能再以 PointMap/Depth 为创新；需以“策略结构变化”或新 benchmark 成立。
3. **X14 counterfactual 可识别性 benchmark**：新颖且容易证伪，可与 X8 合并为实验方法论。
4. **X12 exploit-resistant 接口**：价值高，但 WoVR/WAV/PROWL/理论 exploitation 使 novelty 风险更高。
5. **X13 独立锚定的共同适应**：空间大，第一篇工程和数据风险最高。

其余方向不等于不能做，而是在 2026-08-30 的论文边界下，不容易同时满足“新颖度 > 7、问题自然、四卡可快速得到决定性信号”。
