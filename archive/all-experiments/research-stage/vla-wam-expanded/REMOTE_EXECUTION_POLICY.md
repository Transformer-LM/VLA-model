# 远程执行与个人存储硬策略

**适用运行：** `20260806-vla-wam-expanded-field-map` 及其后续 H1 研究阶段  
**策略来源：** 用户于 2026-08-06 明确授权与限制  
**性质：** 硬门禁；服务器指南的一般建议与本文冲突时，以本文为准

## 1. 身份与连接

- 仅允许 Windows OpenSSH：`<OPENSSH_CLIENT>`。
- 仅允许 SSH 用户：`liu_meng`。
- 授权主机：`<PRIVATE_SERVER>`。
- 私钥只从本地 `<SSH_KEY>` 使用，不复制到项目或服务器。
- 必须使用 `BatchMode=yes`、`IdentitiesOnly=yes`；远程身份不是 `liu_meng` 时立即停止。

## 2. 唯一授权文件系统范围

唯一授权的远程读写根目录：

```text
<PERSONAL_RESEARCH_ROOT>
```

下列内容必须全部位于该目录内：

- 项目代码与本次研究的 source snapshot；
- 数据集、预处理数据和抽样索引；
- 基础模型、适配器和实验 checkpoint；
- Conda/venv、pip/uv/Hugging Face/JAX/PyTorch/Triton/CUDA JIT 缓存；
- 临时文件与 tmux socket；
- stdout/stderr、TensorBoard、W&B offline 日志；
- 指标、图表、审计结果和最终实验 artifacts。

即使底层软链接解析到其他物理路径，后续命令仍只使用 `<PERSONAL_RESEARCH_ROOT>/...` 逻辑路径。

## 3. 团队与共享空间禁令

禁止读取、写入、遍历、复制、同步、移动、软链接或发布到任何团队/共享资源，包括但不限于：

```text
<REMOTE_HOME>/datasets
<REMOTE_HOME>/models
<REMOTE_HOME>/team-projects
<REMOTE_HOME>/team-checkpoints
/mnt/data/datasets
/mnt/data/models
/mnt/data/projects
/mnt/data/checkpoints
```

不得将成功 checkpoint、数据、日志或最终结果“提升”为团队资产。只有用户未来对某个精确源和目标重新明确授权后，才可考虑例外；默认永远禁止。

## 4. 系统与环境禁令

- 禁止 root、`sudo`、`su`、`sudo -u` 和任何权限提升。
- 禁止读取、修改或 `source ~/.bashrc`，禁止修改其他 shell profile。
- 禁止使用或修改全局/shared Conda；只可直接调用个人目录中的环境绝对路径。
- 禁止修改 NVIDIA 驱动、系统 CUDA、系统包、挂载、系统服务和共享目录权限。
- 禁止 `git config --global`、`pip install --user` 或任何可能写到 Home 系统盘的默认行为。
- 禁止终止、覆盖或复用未经本次运行创建的进程、tmux 会话、目录和 checkpoint。

## 5. 无外网执行

- 服务器按无可用外网处理，不依赖代理变量、GitHub、Hugging Face、PyPI 或 W&B 云端可用。
- 文献检索和需要联网的下载在本地 Windows 完成。
- 缺失资产只有在获得具体传输授权后，才能传入个人目录；不得借用共享目录中转。
- 训练与评测默认使用本地日志或 W&B offline 模式。

## 6. 运行前强制检查

每个远程作业在启动前必须验证：

1. `whoami` 为 `liu_meng`；
2. 工作目录、输出目录、缓存、临时目录与 tmux socket 均位于 `<PERSONAL_RESEARCH_ROOT>`；
3. 数据、模型和代码输入同样来自个人目录；
4. GPU 当时空闲且不会干扰其他任务；
5. 命令中不含共享目录、权限提升、在线下载或系统级修改；
6. 作业预计资源不超过 autoresearch 配置的 GPU-hour 与并发上限。

任一检查失败即停止，不采用自动降级到团队目录、系统目录或在线资源的替代路径。

## 7. GPU 调度硬规则

- 默认且优先使用物理 GPU `2,3`。
- GPU `0,1` 预留给用户的另一项实验；只要任意一张卡有进程、显存占用或非空闲状态，本运行就不得使用它们。
- 只有在每个作业启动前重新检查并确认 GPU `0,1,2,3` 四张卡全部空闲时，本运行才可临时使用四卡。
- 不得抢占、终止或干扰其他作业，不得在已占用 GPU 上叠加训练。
- 8 GPUh 按物理 GPU 数 × wall-clock 小时累计；四卡运行 1 小时计 4 GPUh。
