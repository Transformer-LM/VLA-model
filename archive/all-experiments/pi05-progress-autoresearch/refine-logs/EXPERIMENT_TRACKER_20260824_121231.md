# Experiment Tracker

| Run ID | Milestone | Purpose | Variant | Priority | Status | Stop/Go |
|---|---|---|---|---|---|---|
| R000 | M0 | snapshot exact restore | state+RNG+context | MUST | TODO | 不可复现则修基础设施 |
| R001 | M1 | progress headroom | no-state | MUST | TODO | 与 oracle 对照 |
| R002 | M1 | progress headroom | oracle-state | MUST | TODO | +5 pp success 或 -20% invalid |
| R003 | M1 | ecological validity | corrupted-state | MUST | TODO | 目标失败 +15 pp |
| R010 | M2 | admission causal effect | commit vs hold | MUST | TODO | paired CI / stability |
| R011 | M2 | correction causal effect | wrong vs gold | MUST | TODO | paired CI / stability |
| R012 | M2 | simple proxy | step/action-KL/critic | MUST | TODO | proxy 等价则降级 |
| R020 | M3 | deployable predictor | uniform truth | CONDITIONAL | BLOCKED | P1 GO 后解锁 |
| R021 | M3 | deployable predictor | harm-weighted truth | CONDITIONAL | BLOCKED | P1 GO 后解锁 |
| R022 | M3 | deployable predictor | harm ranking | CONDITIONAL | BLOCKED | P1 GO 后解锁 |
| R030 | M4 | held-out closed loop | calibrated truth gate | CONDITIONAL | BLOCKED | P2a GO 后解锁 |
| R031 | M4 | held-out closed loop | harm-aware gate | CONDITIONAL | BLOCKED | P2a GO 后解锁 |
| R040 | M5 | backbone independence | second VLA | NICE | BLOCKED | M4 GO 后解锁 |
| R050 | M5 | real robot validation | approved protocol | NICE | BLOCKED | 用户另行批准 |
