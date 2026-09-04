---
type: paper
node_id: paper:wang2025_latent_policy_steering
title: "Latent Policy Steering with Embodiment-Agnostic Pretrained World Models"
authors: ["Yiqi Wang", "Mrinal Verghese", "Jeff Schneider"]
year: 2025
venue: "arXiv"
external_ids:
  arxiv: "2507.13340"
  doi: null
  s2: null
tags: ["cross-embodiment", "latent-action", "planning", "world-model"]
added: 2026-08-06T08:35:28Z
---

# Latent Policy Steering with Embodiment-Agnostic Pretrained World Models

## One-line thesis
用 embodiment-agnostic optical-flow 动作空间预训练 world model，并在其 latent 中搜索以改善低数据目标机器人策略。

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

> The performance of learned robot visuomotor policies is heavily dependent on the size and quality of the training dataset. Although large-scale robot and human datasets are increasingly available, embodiment gaps and mismatched action spaces make them difficult to leverage. Our main insight is that skills performed across different embodiments produce visual similarities in motions that can be captured using off-the-shelf action representations such as optical flow. Moreover, World Models (WMs) can leverage sub-optimal data since they focus on modeling dynamics. In this work, we aim to improve visuomotor policies in low-data regimes by first pretraining a WM using optical flow as an embodiment-agnostic action representation to leverage accessible or easily collected data from multiple embodiments (robots, humans). Given a small set of demonstrations on a target embodiment, we finetune the WM on this data to better align the WM predictions, train a base policy, and learn a robust value function. Using our finetuned WM and value function, our approach evaluates action candidates from the base policy and selects the best one to improve performance. Our approach, which we term Latent Policy Steering (LPS), improves behavior-cloned policies by 10.6% on average across four Robomimic tasks, even though most of the pretraining data comes from the real world. In the real-world experiments, LPS achieves larger gains: 70% relative improvement with 30-50 target-embodiment demonstrations, and 44% relative improvement with 60-100 demonstrations, compared to a behavior-cloned baseline. Qualitative results can be found on the website: https://yiqiwang8177.github.io/LatentPolicySteering/.

