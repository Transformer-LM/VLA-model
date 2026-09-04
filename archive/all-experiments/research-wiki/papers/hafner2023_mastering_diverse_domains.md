---
type: paper
node_id: paper:hafner2023_mastering_diverse_domains
title: "Mastering Diverse Domains through World Models"
authors: ["Danijar Hafner", "Jurgis Pasukonis", "Jimmy Ba", "Timothy Lillicrap"]
year: 2023
venue: "arXiv"
external_ids:
  arxiv: "2301.04104"
  doi: null
  s2: null
tags: ["latent-dynamics", "imagination", "model-based-rl"]
added: 2026-08-06T07:52:48Z
---

# Mastering Diverse Domains through World Models

## One-line thesis
DreamerV3通过世界模型想象训练策略并以统一配置覆盖多类控制任务。

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

> Developing a general algorithm that learns to solve tasks across a wide range of applications has been a fundamental challenge in artificial intelligence. Although current reinforcement learning algorithms can be readily applied to tasks similar to what they have been developed for, configuring them for new application domains requires significant human expertise and experimentation. We present DreamerV3, a general algorithm that outperforms specialized methods across over 150 diverse tasks, with a single configuration. Dreamer learns a model of the environment and improves its behavior by imagining future scenarios. Robustness techniques based on normalization, balancing, and transformations enable stable learning across domains. Applied out of the box, Dreamer is the first algorithm to collect diamonds in Minecraft from scratch without human data or curricula. This achievement has been posed as a significant challenge in artificial intelligence that requires exploring farsighted strategies from pixels and sparse rewards in an open world. Our work allows solving challenging control problems without extensive experimentation, making reinforcement learning broadly applicable.

