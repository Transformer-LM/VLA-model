---
type: paper
node_id: paper:zeng2026_kemo_eventdriven_keyframe
title: "KEMO: Event-Driven Keyframe Memory for Long-Horizon Robot Manipulation with VLA Policies"
authors: ["Yihan Zeng", "Minghao Ye", "Yiyuan Chen", "Yide Shentu", "Philipp Wu", "Zike Yan", "Zhongyu Li"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2606.23589"
  doi: null
  s2: null
tags: []
added: 2026-08-24T03:48:18Z
---

# KEMO: Event-Driven Keyframe Memory for Long-Horizon Robot Manipulation with VLA Policies

## One-line thesis
_TODO: fill in after reading._

## Problem / Gap
_TODO._

## Method
_TODO._

## Key Results
_TODO._

## Assumptions
_TODO._

## Limitations / Failure Modes
_TODO._

## Reusable Ingredients
_TODO._

## Open Questions
_TODO._

## Claims
_TODO._

## Connections
_Edges are recorded in `graph/edges.jsonl`; summarize here for human readers._

## Relevance to This Project
_TODO._

## Abstract (original)

> Long-horizon robot manipulation remains challenging because similar observations may occur at different execution stages, while the appropriate action depends on previously completed operations. Memory can address this ambiguity by enabling policies to infer task progress from execution history. However, existing memory-augmented approaches often either retain dense histories that require compression or rely primarily on recent context that may discard earlier task-relevant events. In this work, we propose propose KEMO, a lightweight plug-in memory framework that automatically selectively preserves keyframes associated with task-relevant state changes for VLA policies. KEMO combines robot kinematics with visual filtering to detect events, encodes the selected keyframes as compact temporally ordered memory tokens, and integrates them with current visual features through cross-attention and gated residual fusion for VLA training. The detected events also define higher-weight training samples near critical transitions. We evaluate KEMO on various real-world dual-arm manipulation tasks spanning 2 to 6 scored subtasks, and trajectory length ranging from 830 steps to 2846 execution steps (durations from 28 to 95 seconds). Compared with the memory-free baseline (e.g., $π_{0.5}$), KEMO improves aggregate Task Success Rate by 23.6\% and Stage Completion Rate by 34.1\%. Ablations show that event-driven keyframe selection outperforms uniform sampling and recent-frame retention, while the proposed gated fusion and keyframe-aligned loss weighting provide complementary gains.

