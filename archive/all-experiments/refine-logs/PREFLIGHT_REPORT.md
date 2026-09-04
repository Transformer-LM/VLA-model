# PGR-Audit v2.1 Implementation Preflight

**时间**：2026-08-07 13:43:38 +08:00  
**运行**：`20260806-vla-wam-expanded-field-map`  
**阶段**：`implementation-experiments`  
**结论**：`CONDITIONAL-PASS-FOR-CODE-REVIEW`；尚未授权科学实验或 live robot。

## 用户约束的当前解释

- 不采用 simulation/offline first。仿真与真实机器人是可独立推进的证据线。
- 不采用 2 GPUh pilot 或 8 GPUh 总预算；GPU 时间仅作 telemetry。
- 不购买付费算力；当前远程服务器已足够且离线。
- 物理 GPU 2/3 优先；0/1 在每次 launch 前各自重新证明空闲后也可用。无需等待四卡同时空闲，不抢占、不共享、不终止其他进程。
- live robot 不受仿真结果约束，但首次连接/运动仍需 exact endpoint/interface/embodiment/task/data/control/workspace/velocity/force/safety/operator/E-stop contract、默认关闭的 `RobotAdapter` 审查和单独 hash-bound jury。
- 论文写作不在本运行范围内。

## 远程隔离与权限

| 项目 | 已验证事实 |
|---|---|
| SSH 身份 | 仅 `<REMOTE_USER>@<PRIVATE_SERVER>`，Windows OpenSSH + `<SSH_KEY_NAME>` |
| 逻辑个人根 | `<PERSONAL_RESEARCH_ROOT>` |
| canonical 根 | `<PERSONAL_RESEARCH_ROOT_ALIAS>` |
| 隔离代码仓 | `<PERSONAL_RESEARCH_ROOT>/workspace/h1-predictive-aux-starvla` |
| 干净上游 HEAD | `3422b9f2387b6f682cf02802904a77b23ab13afd` |
| 干净 source bundle | SHA256 `747b10dd8c06fc50fee34459dd6bc4020c85db1c43b3ba6f5884ab0b00f1e597` |
| 私有 prereg bundle | `<PERSONAL_RESEARCH_ROOT>/artifacts/h1-pgr-audit/prereg/v2.1-21267bf7`，十个文件逐一复核 |
| 私有模式 | 新目录 `0700`、新文件 `0600`/`umask 077` |
| 禁止项 | 未使用 root/sudo/su；未改 `.bashrc`、全局 Conda、系统 CUDA、共享目录；未干预其他进程 |

首次 `git bundle verify` 因在非 repository context 调用而安全失败，目标目录当时不存在。随后改用 bundle SHA/list-heads 验证并成功 clone；失败尝试保留为工程 lineage，不计科学运行。

## 输入、模型与环境

- 训练环境：`<PERSONAL_RESEARCH_ROOT>/conda/envs/cf-dynalign`，Python 3.11.15，PyTorch 2.6.0+cu124。
- LIBERO eval 环境：`<PERSONAL_RESEARCH_ROOT>/venvs/libero-eval-py310`。
- Qwen3-VL-4B 与 DINO 的完整树/文件摘要记录在冻结 input manifest。
- LIBERO-10 数据树：3430 files，636,965,952 bytes，SHA256 `a919e10e7e2cff046dde10b2ba0fbe091a91d62a80c2446d073216f5a280ae80`；379 episodes、101,469 frames、10 tasks。
- Checkpoints：step1000 `6e2f5275...d1d4735`、step5000 `4b0067d8...4b277a`、step10000 `1687afbd...dee7b`。每个严格为 730 keys，仅允许 `qwen_vl_interface.*`/`action_model.*`，禁止 predictor/world-model 相关字符串。

## 已实现基础

- canonical hashing、个人根 containment、私有 UUID 输出和不可覆盖 artifact。
- rank-32 exact-identity adapter；A/B/C matched gradient routing；exact split/role seed/retry。
- strict checkpoint loader 与 frozen QwenOFT action-interface facade。
- default-off `LockedRobotAdapter`，没有 live command surface。
- 双 GPU snapshot、物理 UUID、独立空闲判据、优先级 2→3→0→1、原子 reservation。
- 完整 launcher lifecycle：私有 runtime env、PID/PGID 与 selected UUID binding、外来 PID 检测、heartbeat、output allowlist、退出核验与 telemetry。
- engineering-only canary：只使用确定性 synthetic dual-view images 与 instruction，不读 LIBERO target/outcome。

## 确定性验证

- 本地 overlay 与远程部署源码逐文件 SHA256 已记录。
- 远程 CPU/static suite：**23/23 PASS**，0.462 s。
- 冻结 spec runtime verifier：`SPEC_VERIFY=PASS ['A','B','C','D','E']`。
- 测试记录：`implementation-stage/pgr-audit-v21-overlay/FOUNDATION_TEST_20260807_134338.log`，SHA256 `b333369e0092e424e75d836333c6f5c6c23fb73b577b19ca5bd12a79dedabf9b`。
- 05:43:38Z read-only GPU snapshot 显示 0/1/2/3 均无 compute PID、0 MiB、0%；该 snapshot 已过期，只证明当时状态，不授权未来 launch。

## 仍在生效的 gates

1. Fresh secondary context 直接读取原始 plan/protocol/jury/ambiguity audit/overlay/tests，完成 same-family provisional code review。
2. 若有 blocking issue，修复并只重新 review 一次；无 blocker 后才运行 engineering canary。
3. Canary 启动瞬间必须重新获得两次 snapshot、个人 UUID lock 和 child binding proof。
4. Canary 仅验证 model load、direct/interface/repeat/in-memory cache parity、determinism/memory；不产生科学结论。
5. C screen 等待 A/B；C0/ABC/Stage1 等待协议问题 9/10/11/12/20/22 的新版本与新 jury；Stage2 还等待 16/17/18。
6. live robot 继续 `NO-GO`，但离线 robot contract 准备为 `GO`，且不受 simulation gate 限制。

## 当前资源账

- GPU hours：`0.0`
- 完成 GPU jobs / scientific jobs：`0 / 0`
- paid cost：`$0.00`
- real robot trials：`0`

本预检允许进入 fresh code review；不允许跳过审查直接训练、揭示 screen outcome 或触发机器人连接/动作。
