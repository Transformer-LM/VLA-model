# Novelty Trace：GeoRetract

**Date:** 2026-08-30

## Verdict

**Level 2 / high overlap.** 可以作为低成本必要性实验，不得在实验前宣称“没人做过”。

## Direct collisions

- POT-VLA 已有 persistent role-indexed 3D object records 与 geometric predicate checks。
- EA-WM 已有 task-grounded event/predicate prediction and verification。
- CheckVLA 已有 action-conditioned execution verification、intervention 与 repair。
- EvoScene-VLA/ChainVLA 已有 action-updated/revisable scene-progress state。
- ReViP/HELM 已有 false completion、memory、verifier 与 recovery protocol。

## Provisional delta

动作条件的 metric relative-geometry transition 对 **typed relation retraction** 的必要性；输出区分 invalidated 与 unobservable，并要求在 direct 3D predicate、RGB verifier、memory verifier 之上产生决策增益。

## Strongest reviewer rejection

“这是 POT-VLA 的 persistent 3D predicates 加 CheckVLA 的 action-conditioned verifier，再接到 ChainVLA/EvoScene 的 progress memory；组合自然且没有新机制。”

## Required rebuttal evidence

只有以下结果同时成立才可能形成可守 claim：

1. direct current 3D predicate 在 co-motion/occlusion 下系统性失败；
2. action-conditioned transition 明显修复，action shuffle 使收益消失；
3. typed retraction 比 generic failure score 减少错误回滚；
4. learned result而非只依赖 GT simulator geometry；
5. closed-loop recovery/false completion 实际改善。

## Kill interpretation

若 direct 3D predicate 持平，则结果仍有实用价值：PointMap geometry checker 值得用于用户系统；但研究结论应是“不需要 WAM dynamics”，不能包装为新 WAM。

