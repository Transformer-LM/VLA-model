# Preflight Report

日期：2026-08-24

## 状态

`PLAN READY / EXECUTION NOT STARTED`

## 已确认

- 研究问题、查杀条件、统计单位和 baseline 已定义。
- 旧的 2/8 GPU-hour 限制不适用；算力按阶段 gate 使用。
- 远程规则已记录：只用 `liu_meng`，只读写 `<PERSONAL_RESEARCH_ROOT>`，禁止 root/sudo/su、`.bashrc`、全局 Conda、系统 CUDA、共享/团队目录。
- GPU 2、3 优先；GPU 0、1 只有实时确认完全空闲时使用。

## 执行前仍需从代码/环境发现

- 用户当前 π0.5 reproduction 的确切仓库、checkpoint、评测环境和任务列表。
- progress assertion 的现有消费接口；若不存在，P0 的固定 wrapper 接口设计。
- simulator 是否支持完整 snapshot/restore 与 RNG 复现。
- 当前服务器 GPU 占用、个人目录中的代码与数据位置。

## 阻止自动训练的条件

- 当前 autoresearch mode 为 `plan`。
- P0 前不得训练 gate、WAM 或 fine-tune π0.5。
- 真实机器人动作需要单独安全协议与用户批准。
