# OA-WAM × EvoScene-VLA 邻近文献地图

**检索截止**：2026-08-29  
**问题**：能否把持久对象地址与动作更新、观测纠正的 scene belief 结合，用于长时 VLA 的对象进度保持、异常归因与恢复？

## 检索范围与证据质量

- 本地全文：OA-WAM、EvoScene-VLA、CheckVLA。
- 官方 arXiv HTML 全文：RB-VLA、Embodied-SlotSSM、POT-VLA、AtlasVLA、EventVLA、ChainVLA、HELM、ReViP、MemoryVLA++、Chameleon、ReMem-VLA、VPWEM、HarnessWAM、HiMem-WAM、MemoryWAM、Reflective VLA。
- 跨库关键词检索：object-centric / persistent identity / action-updated belief / action consequence / execution verification / long-horizon memory；2024–2026。
- 搜索器共返回 103 条去重记录，绝大部分是跨领域噪声。arXiv API 多次出现 SSL EOF，Semantic Scholar 出现 429，OpenAlex 出现 504，DBLP 出现 429/SSL 错误；因此最终判断以官方 arXiv HTML 和本地全文核验为主，不把空命中解释为“没有先例”。

## 直接相关工作

| 工作 | 已解决的问题 | 表示与更新机制 | 没有解决的部分 | 与候选命题的冲突 |
|---|---|---|---|---|
| OA-WAM (2605.06481) | 语言指定对象在背景/布局变化下的稳定绑定 | 冻结 episode 内 `addr`；逐帧 `content/pose`；next-slot 与 16-step action 联训 | 地址初始化错误不可恢复；无跨 chunk belief 后验；无执行失败归因/恢复 | 占据“对象地址 + 对象未来辅助预测” |
| EvoScene-VLA (2605.21862) | chunk 之间缺少被动作更新的场景先验 | action expert 预测下一 recurrent scene prior；新图像纠正全局 prior；训练期 3D/depth anchor | scene state 匿名且全局；不能指出哪个对象/关系被纠正；无显式不确定性 | 占据“动作更新 + 观测纠正 scene belief” |
| RB-VLA (2602.20659) | 长时、部分可观测任务中的进度和动作重复 | 紧凑 action-conditioned latent belief + intent + diffusion policy | belief 为全局 latent；无持久对象地址、关联后验或局部创新 | 占据“action-conditioned persistent belief” |
| Embodied-SlotSSM (2511.11478) | 遮挡、相似对象与对象级非马尔可夫任务 | 持久对象 slots、关系编码和时序 identity 约束 | 主要从观测历史递推；无 executed-action transition/innovation attribution | 占据“对象 slot 持久身份记忆” |
| POT-VLA (2607.18016) | 长时执行中的对象记录、谓词验证与恢复 | RGB-D role-indexed 3D object records；短 chunk 后刷新；谓词 verifier；retry/replan | 不是 learned action-conditioned object transition；没有 prior–observation innovation；任务角色/谓词较手工 | 对“对象记录 + 验证 + 恢复”的广义表述构成最强冲突 |
| Reflective VLA (2606.25215) | 部署变化下，仅当前观测无法辨识动作效果映射 | 把 `(O,A,O')` triplets 放入上下文；以已执行动作结果适应下一动作 | 整体 RGB 历史；不预测结果；无对象地址、选择性纠正或错误归因 | 占据“action consequence context 改善 VLA” |
| CheckVLA (2607.26789) | 执行后的预测–观测偏差与风险干预 | action-conditioned latent WAM + conformal intervention + suffix repair | 偏差主要是全局 outcome；不维护对象 belief/身份；不解决错写长期进度 | 占据“预测–观测比较触发纠错” |
| Chameleon (2603.24576) | observation–action delay 下的可寻址、前瞻控制记忆 | 事件 token、control-indexed recall、Control-JEPA | “地址”是控制检索地址，不是物理对象地址；无 action-effect innovation | 占据“addressable/prospective memory”措辞 |
| HarnessWAM (2608.09516) | WAM 的规划、跨阶段状态、验证与恢复 | 外部 scene belief/task graph/evidence memory；事件驱动 continue/reobserve/replan/recover | 不是对象级 learned predictive filter；不更新 WAM 内部对象 posterior | 占据“WAM + belief + recovery”系统级组合 |
| ChainVLA / HiMem-WAM / MemoryWAM / ReMem-VLA | 长时历史、阶段和执行连续性 | progress context、边界记忆、gist/anchor cache、recurrent queries | 主要压缩/检索历史；不显式进行对象级动作预测—创新—纠正 | 占据一般“长期记忆增强 VLA/WAM” |

## 不能再主张的新意

1. 给 VLA 加长期记忆。
2. 用 WAM 预测 future latent，并让新观测纠正它。
3. 把场景拆成对象 slots 或保存对象记录。
4. 把已执行动作及其结果放入上下文。
5. 用 verifier 中断、重试或重规划。
6. 单纯组合 OA-WAM 的地址与 EvoScene 的 recurrent prefix。

## 仍可检验的结构性缺口

### G1：对象地址级的 action-effect innovation

现有工作分别维护对象或维护 action-conditioned global belief，但缺少统一的：

`per-address prior --executed action--> predicted object effect --new observation--> per-address innovation`

它要求模型回答“哪个对象的哪一项状态与预期不符”，而不是只输出整幅场景差异。

### G2：选择性 belief 修正，而不是整段记忆覆盖

当目标被遮挡、检测器换 ID、动作 no-op 或物体被扰动时，系统应分别选择：保持预测并增大不确定性、重新关联对象、撤销某个关系/进度，或认定执行失败。现有全局 latent 更新无法审计错误污染到哪些对象。

### G3：等误差条件下的偏差归因

相似 prediction error 可能来自：执行失败、错误对象关联、相机/感知变化，或根本不可观测。若不区分，verifier 会错误撤销正确进度或在真实失败时继续执行。

### G4：对象级 belief 的决策价值

必须证明对象级 factorization 改变了下一决策（continue/reobserve/retry/replan 或动作选择），而不是只提升 slot/pose prediction 指标。

## 当前最可守的命题

**Object-Addressed Predict–Compare–Correct Belief (OAPCC)**：对每个持久对象地址维护状态、关系和不确定性；根据实际执行的 action chunk 预测下一对象 belief；将新观测与地址级预测做关联和 innovation；只纠正受证据支持的对象/关系，并把执行失败、身份错配和不可观测分开，供下一次 VLA 决策使用。

这不是“OA-WAM + EvoScene”的模块拼接，而是把二者之间缺失的 Bayesian-filter-like 接口变成可监督、可归因、可消融的学习问题。

## 参考链接

- https://arxiv.org/html/2605.06481
- https://arxiv.org/html/2605.21862
- https://arxiv.org/html/2602.20659
- https://arxiv.org/html/2511.11478
- https://arxiv.org/html/2607.18016
- https://arxiv.org/html/2606.25215
- https://arxiv.org/html/2607.26789
- https://arxiv.org/html/2603.24576
- https://arxiv.org/html/2608.09516
- https://arxiv.org/html/2606.20562
- https://arxiv.org/html/2606.10363

