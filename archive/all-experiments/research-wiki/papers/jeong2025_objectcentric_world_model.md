---
type: paper
node_id: paper:jeong2025_objectcentric_world_model
title: "Object-Centric World Model for Language-Guided Manipulation"
authors: ["Youngjoon Jeong", "Junha Chun", "Soonwoo Cha", "Taesup Kim"]
year: 2025
venue: "arXiv"
external_ids:
  arxiv: "2503.06170"
  doi: null
  s2: null
tags: ["object-centric", "structured-world-model", "language", "manipulation"]
added: 2026-08-06T08:35:25Z
---

# Object-Centric World Model for Language-Guided Manipulation

## One-line thesis
对象中心的语言条件 latent world model用紧凑实体表征预测未来，连接组合世界状态与机器人控制。

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

> A world model is essential for an agent to predict the future and plan in domains such as autonomous driving and robotics. To achieve this, recent advancements have focused on video generation, which has gained significant attention due to the impressive success of diffusion models. However, these models require substantial computational resources. To address these challenges, we propose a world model leveraging object-centric representation space using slot attention, guided by language instructions. Our model perceives the current state as an object-centric representation and predicts future states in this representation space conditioned on natural language instructions. This approach results in a more compact and computationally efficient model compared to diffusion-based generative alternatives. Furthermore, it flexibly predicts future states based on language instructions, and offers a significant advantage in manipulation tasks where object recognition is crucial. In this paper, we demonstrate that our latent predictive world model surpasses generative world models in visuo-linguo-motor control tasks, achieving superior sample and computation efficiency. We also investigate the generalization performance of the proposed method and explore various strategies for predicting actions using object-centric representations.

