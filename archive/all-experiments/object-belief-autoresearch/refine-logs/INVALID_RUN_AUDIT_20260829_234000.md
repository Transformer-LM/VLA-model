# Invalid-Run Audit: v3/v4 MuJoCo Initialization

## Verdict

v3/v4 数据与 M1a 日志全部 **INVALID / non-evidence**。不得用于支持或否定 Idea，也不得与 v5 汇总。

## Trigger

M1a train NLL 正常下降，但 validation NLL 在约 0.27 与 `1e5–1e6` 之间跳变。monitor 在 M1b 前停止 screen，六个 M1a 中四个完成、两个被中止；GPU 随即归零。

## Root cause

生成器在随机设置 free-joint qpos 后调用 `mujoco.mj_setConst(model,data)`。该 API 把 qpos 重置到模型默认 `qpos0`，使三个对象从同一原点开始碰撞并近似沿一维散开。只读复现显示：随机 layout 在 `mj_setConst` 前正确，调用后三个 qpos 立即全部变为 `(0,0,0.035)`。因此：

- y 位置标准差仅约 `5e-4`；
- 极少数 residual velocity 在以 `~1e-6` 训练标准差归一化后变成 `1e5` 级输入；
- validation NLL 失去解释性。

## Corrective actions

- 先更新 mass/inertia/friction 并调用 `mj_setConst`，之后再设置随机 qpos 和 mocap。
- 静止场景不再输入数值近零的 pre velocity。
- 数据新增 sampled layout 与 settle displacement；audit 要求 settle displacement q99 < 0.02 m。
- 初始对象中心最小距离提高到 0.10 m，避免随机姿态初始互穿。
- 使用全新 v5 数据、结果目录与 code hash；v4 checkpoint 不复用。

## Integrity note

问题由训练监控主动发现，而不是在看到有利/不利 gate 后选择性重跑。v4 未产生任何被接受的 headroom 或 method verdict。

