---
type: paper
node_id: paper:hansen2023_tdmpc2_scalable_robust
title: "TD-MPC2: Scalable, Robust World Models for Continuous Control"
authors: ["Nicklas Hansen", "Hao Su", "Xiaolong Wang"]
year: 2023
venue: "arXiv"
external_ids:
  arxiv: "2310.16828"
  doi: null
  s2: null
tags: ["latent-dynamics", "model-based-rl", "mpc"]
added: 2026-08-06T07:52:48Z
---

# TD-MPC2: Scalable, Robust World Models for Continuous Control

## One-line thesis
在任务相关latent中学习隐式动力学并用局部轨迹优化做连续控制。

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

> TD-MPC is a model-based reinforcement learning (RL) algorithm that performs local trajectory optimization in the latent space of a learned implicit (decoder-free) world model. In this work, we present TD-MPC2: a series of improvements upon the TD-MPC algorithm. We demonstrate that TD-MPC2 improves significantly over baselines across 104 online RL tasks spanning 4 diverse task domains, achieving consistently strong results with a single set of hyperparameters. We further show that agent capabilities increase with model and data size, and successfully train a single 317M parameter agent to perform 80 tasks across multiple task domains, embodiments, and action spaces. We conclude with an account of lessons, opportunities, and risks associated with large TD-MPC2 agents. Explore videos, models, data, code, and more at https://tdmpc2.com

