# 实验跟踪表：ISRAC

| Run ID | Milestone | Purpose | System / Variant | Split | Metrics | Priority | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| R001 | M0 | 测 MuJoCo deterministic replay 噪声 | same-parameter ×30 | LIBERO 1 task / 20 snapshots | state/RGB/depth/proprio max drift | MUST | TODO | CPU only |
| R002 | M0 | 测 SAPIEN deterministic replay 噪声 | same-parameter ×30 | RoboTwin 1 task / 20 snapshots | state/RGB/depth/proprio max drift | MUST | TODO | CPU only |
| R003 | M0 | 证书拒绝 action-indexed 假反例 | scripted fake switch | 两平台各 10 cases | rejection rate | MUST | TODO | 应为 100% |
| R004 | M0 | 验证首次物理分歧定位 | single native parameter perturbation | 两平台各 10 cases | first divergence/contact alignment | MUST | TODO | 不涉及 WAM |
| R005 | M1 | ISRAC 摩擦/接触 E0 | full compiler | LIBERO / 20 snapshots / top-8 | certified pairs, calls/pair | MUST | TODO | 禁止手调 |
| R006 | M1 | ISRAC 负载/遮挡 E0 | full compiler | LIBERO / 20 snapshots / top-8 | certified pairs, calls/pair | MUST | TODO | 参数必须有物理语义 |
| R007 | M1 | ISRAC 摩擦/接触 E0 | full compiler | RoboTwin / 20 snapshots / top-8 | certified pairs, calls/pair | MUST | TODO | 禁止手调 |
| R008 | M1 | ISRAC 负载/遮挡 E0 | full compiler | RoboTwin / 20 snapshots / top-8 | certified pairs, calls/pair | MUST | TODO | 参数必须有物理语义 |
| R009 | M1 | random baseline | domain randomization + rejection | 与 R005–R008 同预算 | yield per 1k calls | MUST | TODO | matched calls |
| R010 | M1 | grid/CMA-ES baseline | constrained fuzzing | 与 R005–R008 同预算 | yield per 1k calls | MUST | TODO | 不使用 influence graph |
| R011 | M1 | 删除 influence-zero | ISRAC w/o separation | 与 R005–R008 同预算 | yield, invalid rate | MUST | TODO | 核心 novelty ablation |
| R012 | M1 | 48h E0 gate 汇总 | frozen pair set | 两平台 | gate pass/fail | MUST | TODO | FAIL 则停止全部 GPU |
| R013 | M2 | 冻结 π0.5 candidate bundle | π0.5 top-K | certified snapshots | eligibility, diversity | MUST | TODO | GPU 2/3 优先 |
| R014 | M2 | 无修正 WAM | DreamZero-compatible WAM | normal + alias | ranking/regret | MUST | TODO | common candidate bundles |
| R015 | M2 | FWM baseline | official or clearly labeled replica | normal + alias | prediction error, ranking | MUST | TODO | 不冒充官方 |
| R016 | M2 | FBFM baseline | official or clearly labeled replica | normal + alias | correction harm | MUST | TODO | 强最近邻 |
| R017 | M2 | ReDRAW-style baseline | point residual dynamics | normal + alias | correction harm | MUST | TODO | 机制族基线 |
| R018 | M2 | baseline reproducibility gate | all baselines | ordinary perturbations | expected direction checks | MUST | TODO | 失败则修复，不进入主结果 |
| R019 | M3 | 核心 alias 评测 seed 0 | all frozen methods | alias + controls | false-transfer, regret, harm | MUST | TODO | 可按方法分 GPU |
| R020 | M3 | 核心 alias 评测 seed 1 | all frozen methods | alias + controls | false-transfer, regret, harm | MUST | TODO | 可按方法分 GPU |
| R021 | M3 | 核心 alias 评测 seed 2 | all frozen methods | alias + controls | false-transfer, regret, harm | MUST | TODO | 可按方法分 GPU |
| R022 | M3 | held-out WAM transfer | pair compiler blind to model | alias | harm transfer | MUST | TODO | 排除 target overfit |
| R023 | M3 | 普通扰动负对照 | matched severity | non-alias | harm delta | MUST | TODO | 排除一般 OOD |
| R024 | M3 | 统计汇总 | paired bootstrap | all | 95% CI, effect size | MUST | TODO | 不只报均值 |
| R031 | M4 | 扩至 4 tasks/engine | full compiler | held-out tasks | zero-edit yield | NICE | TODO | C1/C2 通过后 |
| R032 | M4 | 真实机器人小样本 | safe replay only | pre-defined cases | direction agreement | NICE | TODO | 不宣称安全保证 |
