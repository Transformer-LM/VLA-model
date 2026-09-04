# Pipeline Summary

**Problem**：π0.5 长时任务中的遗忘、错误推进、误完成与失败后持续执行。  
**Final Thesis**：先因果测量 false progress writes 对冻结 VLA 的闭环伤害异质性；仅在该 finding 通过后训练 harm-aware truth verifier。  
**Final Verdict**：RETHINK / PILOT GO  
**Date**：2026-08-24

## Deliverables

- Idea：`idea-stage/IDEA_REPORT.md`
- 候选池：`idea-stage/IDEA_CANDIDATES.md`
- 查新：`idea-stage/NOVELTY_REPORT.md`
- 最终 proposal：`refine-logs/FINAL_PROPOSAL.md`
- 实验计划：`refine-logs/EXPERIMENT_PLAN.md`
- Tracker：`refine-logs/EXPERIMENT_TRACKER.md`
- Preflight：`refine-logs/PREFLIGHT_REPORT.md`

## First Runs

1. R000：snapshot/restore 与 assertion carrier 单元测试。
2. R001–R003：no/oracle/corrupted progress state 的 headroom 和生态效度。
3. 只有 P0 通过才运行 R010–R012 配对因果测量。

## Explicitly Rejected Complexity

WAM、视频生成、retraction graph、planner、联合 recovery、action-head replacement 和全量 π0.5 fine-tuning 均不进入首轮。

## Next Action

若用户批准从 plan 转 execution，先只实现 M0–M1；不得直接启动大规模训练。
