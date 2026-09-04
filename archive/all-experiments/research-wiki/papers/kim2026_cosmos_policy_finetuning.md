---
type: paper
node_id: paper:kim2026_cosmos_policy_finetuning
title: "Cosmos Policy: Fine-Tuning Video Models for Visuomotor Control and Planning"
authors: ["Moo Jin Kim", "Yihuai Gao", "Tsung-Yi Lin", "Yen-Chen Lin", "Yunhao Ge", "Grace Lam", "Percy Liang", "Shuran Song", "Ming-Yu Liu", "Chelsea Finn", "Jinwei Gu"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2601.16163"
  doi: null
  s2: null
tags: ["world-action-model", "planning", "value-model"]
added: 2026-08-06T07:52:56Z
---

# Cosmos Policy: Fine-Tuning Video Models for Visuomotor Control and Planning

## One-line thesis
Cosmos Policy把动作、未来状态与价值编码为视频latent帧，支持直接策略与模型式规划。

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

> Recent video generation models demonstrate remarkable ability to capture complex physical interactions and scene evolution over time. To leverage their spatiotemporal priors, robotics works have adapted video models for policy learning but introduce complexity by requiring multiple stages of post-training and new architectural components for action generation. In this work, we introduce Cosmos Policy, a simple approach for adapting a large pretrained video model (Cosmos-Predict2) into an effective robot policy through a single stage of post-training on the robot demonstration data collected on the target platform, with no architectural modifications. Cosmos Policy learns to directly generate robot actions encoded as latent frames within the video model's latent diffusion process, harnessing the model's pretrained priors and core learning algorithm to capture complex action distributions. Additionally, Cosmos Policy generates future state images and values (expected cumulative rewards), which are similarly encoded as latent frames, enabling test-time planning of action trajectories with higher likelihood of success. In our evaluations, Cosmos Policy achieves state-of-the-art performance on the LIBERO and RoboCasa simulation benchmarks (98.5% and 67.1% average success rates, respectively) and the highest average score in challenging real-world bimanual manipulation tasks, outperforming strong diffusion policies trained from scratch, video model-based policies, and state-of-the-art vision-language-action models fine-tuned on the same robot demonstrations. Furthermore, given policy rollout data, Cosmos Policy can learn from experience to refine its world model and value function and leverage model-based planning to achieve even higher success rates in challenging tasks. We release code, models, and training data at https://research.nvidia.com/labs/dir/cosmos-policy/

