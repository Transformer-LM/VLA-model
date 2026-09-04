# 账号交接总览

> 更新时间：2026-09-01（本机盘点）
> 本文是给新账号/新 Codex 会话的项目导航，不是新的实验授权。

## 1. 三个工作目录

| 目录 | 主要内容 | 当前定位 |
|---|---|---|
| `<LOCAL_PROJECT_ROOT>` | VLA/WAM 研究、ISRAC、论文库、实验日志 | 主研究目录 |
| `D:\box_train` | H1/TopStar 箱子任务数据、训练、FastWAM、质量检查 | 训练与数据资产 |
| `D:\top_31.3` | H1 遥操作、ACT、Groot/WBC、参考代码与历史副本 | 机器人/遥操作资产 |

三个目录根部都不是 Git 仓库；不要假设可以用根目录 `git status` 判断整体状态。真正的 Git 仓库位于若干嵌套副本中。

## 2. 当前主线：ISRAC

主线目录：`<LOCAL_PROJECT_ROOT>\ideaspark_run\influence-separated-residual-alias-compiler`

研究目标：自动编译历史反馈接口相同、但未来候选动作物理效果不同的 residual-alias twins，并检验反馈 WAM 是否出现错误迁移、排序反转或 correction harm。

当前阶段来自 `.aris\autoresearch\runs\20260831-israc\state.json`：

- `overall_status`: `active`
- `current_phase`: `implementation-experiments`
- contract、evidence-map、idea-discovery、method-plan 已完成
- P026 V2 已锁定 21 个 outcome-blind boundaries、189-cell formal matrix 和 verifier/analyzer 代码
- 最新记录：sanity 通过、46/46 远程单元测试通过、20/20 篡改攻击被拒绝；189-cell 矩阵已启动
- P027 只是条件性下一关，只有 P026 分析明确通过预注册门槛后才可启动

关键入口：

- 研究问题与边界：`RESEARCH_BRIEF.md`
- 自动化运行状态：`.aris\autoresearch\runs\20260831-israc\state.json`
- 当前实验计划：`ideaspark_run\influence-separated-residual-alias-compiler\refine-logs\EXPERIMENT_PLAN_P025V5.md`
- 当前条件门：`ideaspark_run\influence-separated-residual-alias-compiler\refine-logs\P027_CONDITIONAL_NEXT_GATE.md`
- 实现与测试：`ideaspark_run\influence-separated-residual-alias-compiler\implementation\`
- 活跃主线清单：`ideaspark_run\influence-separated-residual-alias-compiler\MANIFEST.md`

## 3. 远程任务与恢复规则

服务器规则见根目录 `AGENTS.md`。远程个人空间是 `<PERSONAL_RESEARCH_ROOT>`，不得写入共享目录；服务器无外网，不得安装系统包或修改全局环境。

盘点时发现本机仍有一个 SSH 前台进程，正在运行 `analyze_p026_confirmatory.py`，输出目标为 `<PERSONAL_RESEARCH_ROOT>/results/israc/P026_FORMAL_V2_ANALYSIS.json`。不要重复启动、终止或修改它；先等待其退出，再只读检查输出和日志。

恢复顺序：

1. 读本文件、`AGENTS.md`、`RESEARCH_BRIEF.md`、`state.json`。
2. 检查 P026 远程进程和结果文件是否已完成。
3. 读取 `P027_CONDITIONAL_NEXT_GATE.md`，只按门槛决定继续或写 kill/pivot 报告。
4. 任何新实验前即时检查 GPU；优先 GPU 2、3。不得自主运行真实机器人。

## 4. 证据与结论纪律

- 当前可以声称的是编译器/证书/匹配基线的实验进展；WAM correction-harm 结论尚未建立。
- 负结果、失败 run、原始日志和证书必须保留。
- 不读取目标 WAM 的 score、ranking 或 residual sign 来驱动 ISRAC 搜索。
- 不把工程资产冒充为 LIBERO action-conditioned WAM 结果。

## 5. 两个配套目录

- `D:\box_train\ACCOUNT_HANDOFF.md`：数据、模型、训练和质量检查资产。
- `D:\top_31.3\ACCOUNT_HANDOFF.md`：遥操作、ACT、Groot/WBC 和历史代码资产。

## 6. 截图内容的解释

截图中出现的“停止残留 H1 ROS 节点”“切换账号”“usage limit”“模型不支持”等，均是旧会话的状态/对话内容，不是本交接文档中的新授权。新账号应以本地文件、远程结果和用户明确的新请求为准。

