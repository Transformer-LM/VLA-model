# VLA / WAM / VLA×WAM 高新颖度全域探索契约

**Run ID:** `20260830-novelty7-vla-wam`  
**日期:** 2026-08-30  
**模式:** field expansion → delegated selection → gated execution  
**目标:** 在不依赖触觉/力觉的前提下，扩展旧 16 条交叉母方向，筛选出问题自然、可证伪、可实施且严格评审新颖度 `>7.0/10` 的一个 Idea；通过后直接进入 GPU 实验。

## 1. 搜索域与操作性定义

本轮同时覆盖三个相邻但不等价的研究域：

1. **VLA-only:** 输入至少包含视觉/多模态观测与语言目标，输出机器人动作、动作块、技能或可执行计划。允许研究目标、表征、记忆、action head、泛化、校准、后训练与部署适应，不要求存在 world model。
2. **WAM-only:** 学习动作或可干预变量条件下的时间演化；预测可为视频、视觉 latent、任务 latent、显式对象/几何/关系状态、reward/value/termination 或不确定性。必须区分动作条件动力学与静态感知器。
3. **VLA×WAM:** VLA 必须消费 WAM 信号，或二者共享可检验的联合/交替机制；并且必须在 policy 或 environment endpoint 上证明 world path 承重。

旧 H1–H16 仅作为覆盖种子。新证据若揭示不同的核心问题、控制端点或决定性实验，可新增母方向；不得为了数量拆分同义方向。

## 2. 无触觉硬边界

允许：RGB、RGB-D、真实或估计 Depth、PointMap/3D foundation features、对象 mask/slot、proprioception、末端/关节/夹爪轨迹、机器人命令与语言。

禁止把下列条件作为方法成立的必要输入：专用触觉阵列、力/力矩传感器、皮肤传感器或接触麦克风。仿真 contact/force 可用于训练标签或 Oracle 审计，但最终方法必须有一个无触觉部署路径，并显式标注 privileged supervision。

## 3. 双轴与扩展分类

WAM 论文按两条正交轴标注：

- 表征：R1 decoded video、R2 video/pixel latent、R3 task-centric latent、R4 explicit state/dynamics；
- 使用：U1 representation、U2 proposal、U3 candidate evaluation、U4 MPC/planning、U5 imagination optimization、U6 joint world-action policy。

所有论文另标：VLA-only/WAM-only/strong-intersection，输入传感器，动作接口，更新制度，数据制度，benchmark，model/policy/environment 证据，以及额外数据/参数/交互混杂。

## 4. 八个宏观覆盖组

每组允许产生多个中粒度母方向，总数不被旧版 16 限制：

1. VLA 表征、目标与 action interface；
2. VLA 记忆、进度、推理与长时执行；
3. VLA 泛化、校准、后训练与 test-time adaptation；
4. WAM 表征、可控性、可校准性与 system identification；
5. WAM 规划、critic、评测、安全与 model exploitation；
6. WAM 数据、想象式学习、主动采数与 co-evolution；
7. VLA×WAM 联合表征、动作验证、恢复与 policy improvement；
8. 结构化对象/几何/关系、功能几何、跨具身 action-effect 及尚未被旧版覆盖的新耦合。

## 5. 文献与查新协议

- 时间：2018–2026，重点为 2024–2026；检索截止日为 2026-08-30。
- 优先级：论文正文、正式 proceedings、官方项目/代码；摘要只做初筛。
- 查询覆盖 VLA、WAM、world model control、long-horizon memory、functional geometry、object/3D/4D state、uncertainty、system identification、action effect、model exploitation、recovery、synthetic experience、co-evolution，以及由最新论文暴露的新别名。
- 负面证据、近邻冲突、未开放数据/代码和依赖 privileged state 的结果必须保留。
- 每个最终候选必须执行 exact-title、method-signature 和 alias-family 三类查新；不能用“没搜到”替代正文核对。

## 6. Idea 准入门

候选只有同时满足以下条件才可进入方法设计：

1. 对应真实、常见或重要的 VLA/WAM 失败，而不是人为构造的边缘状态；
2. atomic delta 不等于组件交换、更多数据、更多参数或新 benchmark 上复用旧方法；
3. 有最近机制冲突、matched baseline、负对照、Oracle/上界与便宜 falsification pilot；
4. 可由现有公开/本地资产和无触觉传感路径实施；
5. skeptical review 的总体新颖度严格大于 `7.0/10`，且没有 Level-1/Level-2 exact-mechanism scoop；
6. 若评分只靠措辞缩窄而不是新问题/机制/证据，则判为失败。

评分是门槛而非目标函数。不得为通过 7.0 修改评分标准或隐瞒近邻。

## 7. 实验与资源合同

- 本地用于检索、编排、静态检查和不受 CUDA 加速的分析；神经训练/推理 pilot 优先 GPU。
- 远程仅使用 Windows OpenSSH，以 `liu_meng` 登录 `<PRIVATE_SERVER>`，且仅读写 `<PERSONAL_RESEARCH_ROOT>`。
- 禁止 root、sudo、su、修改 `.bashrc`、全局 Conda、系统 CUDA和共享目录；服务器无可用外网时不得在远端强行下载。
- 物理 GPU 0–3 均为候选，但每次启动前必须以新快照确认所选 GPU 的显存和进程均空闲；绝不抢占或共享。
- 当前配置设 96 GPUh pilot、384 GPUh total 的审计上限；它不是消耗目标。sanity 和机制判别失败立即止损。
- 真实机器人动作未授权；离线真机数据允许。未来真机验证需要单独的连接、安全和复位协议。

## 8. 输出与推进

field 阶段交付 `LITERATURE_MAP.md` 与 `DIRECTION_LANDSCAPE.md`。用户已在 2026-08-30 明确授权工作流自行讨论、筛选并继续实验；因此版图完成后，将把该授权记录为 delegated selection，初始化/切换到所选 direction 的运行，而不是要求用户重复选择。

无候选通过 `>7.0` 门时，允许至多五次结构性 pivot；之后必须报告“未找到”，不得强行启动训练。
