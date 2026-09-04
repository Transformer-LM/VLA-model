---
type: paper
node_id: paper:liu2026_worldvlaloop_closedloop_learning
title: "World-VLA-Loop: Closed-Loop Learning of Video World Model and VLA Policy"
authors: ["Xiaokang Liu", "Zechen Bai", "Hai Ci", "Kevin Yuchen Ma", "Mike Zheng Shou"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2602.06508"
  doi: null
  s2: null
tags: ["vla-wam", "h12", "h13", "co-evolution"]
added: 2026-08-06T13:10:45Z
---

# World-VLA-Loop: Closed-Loop Learning of Video World Model and VLA Policy

## One-line thesis
用 VLA 失败轨迹更新世界模型，再在更新后的想象环境中继续策略学习，形成双向闭环。

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

> Reinforcement learning (RL) can refine Vision-Language-Action (VLA) policies beyond behavior cloning, but real-world RL remains expensive due to extensive rollouts, resets, supervision, and safety risks. Action-conditioned video world models offer an option to train in virtual environments, yet they exhibit imprecise action following, particularly on subtle near-success failures. Besides, they lack native reward signals for RL. Computing rewards based on inaccurate visual predictions remain unreliable. We introduce World-VLA-Loop, structured around two foundational designs and a higher-level co-evolving paradigm. We first curate SANS, dedicatedly mixing successful and near-success trajectories to improve action-outcome alignment. Then, we train a state-aware video world model that jointly predicts future frames and binary rewards from diffusion latents. It couples reward estimation to the generator rather than a separate module, and in turn, benefits visual prediction. Since VLA behavior shifts during RL, a fixed simulator can misalign with the updated policy, World-VLA-Loop therefore closes the loop by using the refined world model for iterative VLA post-training while feeding rollouts from each improved policy back to augment and fine-tune the world model. Across simulation and real-robot experiments, World-VLA-Loop substantially improves VLA performance while reducing reliance on costly physical interaction.

