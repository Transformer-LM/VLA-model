# Research Brief — ISRAC

**状态：** ready-for-discovery / selected-idea execution  
**语言：** 中文  
**论文写作：** 关闭

## 研究问题

反馈式 World Action Model（WAM）会根据已经执行动作暴露的预测误差，
修正、重排或否决尚未执行的 VLA 候选动作。单个 factual residual 可能
无法识别误差对不同动作的响应：两个合法物理世界可以产生完全相同的
历史观测与 residual，却让同一个未来候选动作产生不同的真实效果。

## 当前 Idea

**Influence-Separated Residual-Alias Compiler（ISRAC）** 自动寻找两个
simulator-native 物理世界，使：

1. 冻结 VLA 的 factual action 和完整反馈接口在两世界中相同；
2. 未执行候选动作会激活此前零影响的物理参数块；
3. 候选未来的物理效果显著分离；
4. 编译搜索不读取目标 WAM 的 score、ranking 或 residual sign；
5. 每个 pair 附带参数语义、历史同一性、首次激活与首次分歧证书。

## 可证伪主张

主张 C1：相对随机/网格/CMA-ES 等预算物理扰动，influence-separated
compiler 能在多个任务和平台上更高效地产生 certified residual-alias
twins。

辅助主张 C2：在编译器未读取目标模型分数时，这些 twins 仍能让至少
两类冻结反馈 WAM 方法出现比普通物理扰动更高的 false transport、
ranking inversion 或 correction harm。

## 当前证据与限制

- 强 StarVLA 已在四个 LIBERO 成功轨迹上提供冻结候选。
- 三个新增任务的 8 个自动边界中，6 个通过并产生 24 对 certified
  compliance aliases。
- 原始单任务闭环测试中两个世界都成功，84 对 85 步；因此尚无任务
  成功率伤害证据。
- 摩擦机制只有约 0.074 mm 分离，作为负结果保留。
- 还缺少匹配预算基线、第二机制/平台、多种子以及冻结反馈 WAM 评测。

## 关键停止条件

- 自动 compiler 不优于最佳匹配预算基线：停止 C1 或结构性修改。
- 只能通过手工任务规则、action-indexed switch 或目标 WAM score 搜索：
  停止 Idea。
- alias set 不会提高反馈 WAM 的错误迁移，或普通扰动同样有效：停止 C2。
- 同一性、激活或原始数据审计失败：不进入 claim gate。

## 执行与安全

- 远程仅使用 `<REMOTE_USER>@<PRIVATE_SERVER>` 与 `<PERSONAL_RESEARCH_ROOT>`。
- 服务器无外网；不修改 root、系统 CUDA、全局 Conda、`.bashrc` 或共享目录。
- GPU 2、3 优先；每次启动即时检查，GPU 0、1 仅在同样空闲时使用。
- 不自主运行真实机器人。真实机器人实验需要独立安全协议和操作者批准。
- 负结果、失败 run、原始日志和证书全部保留。
