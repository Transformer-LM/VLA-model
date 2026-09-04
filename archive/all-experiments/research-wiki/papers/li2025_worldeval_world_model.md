---
type: paper
node_id: paper:li2025_worldeval_world_model
title: "WorldEval: World Model as Real-World Robot Policies Evaluator"
authors: ["Yaxuan Li", "Yichen Zhu", "Junjie Wen", "Chaomin Shen", "Yi Xu"]
year: 2025
venue: "arXiv"
external_ids:
  arxiv: "2505.19017"
  doi: null
  s2: null
tags: ["policy-evaluation", "world-simulator", "safety"]
added: 2026-08-06T07:52:52Z
---

# WorldEval: World Model as Real-World Robot Policies Evaluator

## One-line thesis
WorldEval把动作跟随视频世界模型用作真实机器人策略排名和安全筛查代理。

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

> The field of robotics has made significant strides toward developing generalist robot manipulation policies. However, evaluating these policies in real-world scenarios remains time-consuming and challenging, particularly as the number of tasks scales and environmental conditions change. In this work, we demonstrate that world models can serve as a scalable, reproducible, and reliable proxy for real-world robot policy evaluation. A key challenge is generating accurate policy videos from world models that faithfully reflect the robot actions. We observe that directly inputting robot actions or using high-dimensional encoding methods often fails to generate action-following videos. To address this, we propose Policy2Vec, a simple yet effective approach to turn a video generation model into a world simulator that follows latent action to generate the robot video. We then introduce WorldEval, an automated pipeline designed to evaluate real-world robot policies entirely online. WorldEval effectively ranks various robot policies and individual checkpoints within a single policy, and functions as a safety detector to prevent dangerous actions by newly developed robot models. Through comprehensive paired evaluations of manipulation policies in real-world environments, we demonstrate a strong correlation between policy performance in WorldEval and real-world scenarios. Furthermore, our method significantly outperforms popular methods such as real-to-sim approach.

