# Idea 评审报告：Source-aware VLA×WAM Verification

**日期**：2026-08-30  
**评审性质**：fresh same-family provisional jury  
**严格门槛**：新颖度必须 `> 7.0`，等于 7.0 不通过  
**结论**：**NO-GO；13 个候选无一通过门槛，因此不进入方法细化或 GPU 训练。**

## 方向命题

现有 action-conditioned WAM verifier 往往把“预测未来与真实观察不一致”压缩为单个风险分数。但相近的 discrepancy 可能来自机器人执行失败、WAM 自身失配或部署观测含混；三者应触发不同干预。问题价值高，但宽泛 failure attribution、consistency decomposition 与 category-specific recovery 已有强祖先。

## 陪审排名

| 排名 | 候选 | Novelty | 结论 |
|---:|---|---:|---|
| 1 | C02 SourceBlind residual-matched benchmark | **7.0** | PIVOT / 未通过 |
| 2 | C01 causal residual attribution | 6.8 | PIVOT |
| 3 | C05 progress-memory firewall | 6.6 | PIVOT |
| 4 | C12 minimal-intervention explanation | 6.4 | PIVOT |
| 5 | C11 residual-onset graph | 6.1 | PIVOT |
| 6–13 | C04/C07/C03/C13/C08/C06/C09/C10 | 5.8–4.4 | KILL |

## 决定

本轮最高只有 7.0，不满足用户要求的严格 `>7.0`。不启动 GPU。下一轮排除本轮 13 项和 functional-geometry 旧失败机制，进行结构性换题。完整报告见 `IDEA_REPORT_20260830_220200.md`，原始陪审响应见 `.aris/traces/idea-creator/2026-08-30_run01/001-novelty-jury.response.md`。
