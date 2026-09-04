---
type: paper
node_id: paper:zheng2026_memworld_memoryaugmented_actionconditioned
title: "Mem-World: Memory-Augmented Action-Conditioned World Models for Persistent Robot Manipulation"
authors: ["Zirui Zheng", "Jiaqian Yu", "Xiongfeng Peng", "jun shi", "Mingyi Li", "Chao Zhang", "Weiming Li", "Dong Wang", "Huchuan Lu", "Xu Jia"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2606.18960"
  doi: null
  s2: null
tags: ["memory", "partial-observability", "world-model", "robotics"]
added: 2026-08-06T08:35:23Z
---

# Mem-World: Memory-Augmented Action-Conditioned World Models for Persistent Robot Manipulation

## One-line thesis
长期持久操作需要从历史检索被遮挡或离开当前视野的对象与场景状态，而不能只依赖当前帧。

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

> Action-conditioned world models have emerged as a promising paradigm for robot learning, offering a scalable alternative to costly real-world experimentation by generating action-consistent video rollouts. However, persistent world modeling remains challenging in manipulation: frequent end-effector occlusions and rapid wrist-camera motion make the current observation insufficient for predicting future views, causing models to forget or hallucinate scene details seen in earlier frames. Existing memory retrieval strategies often fail to identify informative history in dynamic manipulation scenarios. To address this limitation, we propose Mem-World, a memory-augmented multi-view action-conditioned world model. At its core, we present W-VMem, a 4D wrist-view-centered surfel-indexed memory that anchors historical observations to temporally evolving surface elements. By explicitly modeling when and where scene elements are observed, W-VMem enables geometry-aware retrieval of relevant history frames conditioned on future actions. During generation, relevant history frames are selected via surfel-based rendering and scoring, providing informative and non-redundant context for prediction. Extensive experiments show that Mem-World generates persistent rollouts in complex manipulation scenarios, enables more reliable policy evaluation than Ctrl-World, improving the Pearson correlation with real-world performance by 14.5\%, and supports effective policy improvement through synthetic data generation, increasing success rates from 58\% to 72\% on long-horizon tasks.

