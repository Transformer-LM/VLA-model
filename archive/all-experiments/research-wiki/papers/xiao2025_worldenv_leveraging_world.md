---
type: paper
node_id: paper:xiao2025_worldenv_leveraging_world
title: "World-Env: Leveraging World Model as a Virtual Environment for VLA Post-Training"
authors: ["Junjin Xiao", "Yandan Yang", "Xinyuan Chang", "Ronghan Chen", "Feng Xiong", "Mu Xu", "Wei-Shi Zheng", "Qing Zhang"]
year: 2025
venue: "arXiv"
external_ids:
  arxiv: "2509.24948"
  doi: null
  s2: null
tags: ["vla-wam", "h12", "post-training", "imagined-rl"]
added: 2026-08-06T13:10:44Z
---

# World-Env: Leveraging World Model as a Virtual Environment for VLA Post-Training

## One-line thesis
将动作条件视频世界模型、奖励与终止模型组成学习环境，对 VLA 做模拟后训练。

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

> Vision-Language-Action (VLA) models trained via imitation learning suffer from significant performance degradation in data-scarce scenarios due to their reliance on large-scale demonstration datasets. Although reinforcement learning (RL)-based post-training has proven effective in addressing data scarcity, its application to VLA models is hindered by the non-resettable nature of real-world environments. This limitation is particularly critical in high-risk domains such as industrial automation, where interactions often induce state changes that are costly or infeasible to revert. Furthermore, existing VLA approaches lack a reliable mechanism for detecting task completion, leading to redundant actions that reduce overall task success rates. To address these challenges, we propose World-Env, an RL-based post-training framework that replaces physical interaction with a low-cost world model-based virtual simulator. World-Env consists of two key components: (1) a physically-consistent world simulator that generates temporally consistent future visual observations, and (2) a vision-language model (VLM)-guided instant reflector that provides continuous reward signals and predicts action termination. This simulated environment enables VLA models to safely explore and generalize beyond their initial imitation learning distribution. Our method achieves notable performance gains with as few as five expert demonstrations per task. Experiments on complex robotic manipulation tasks demonstrate that World-Env effectively overcomes the data inefficiency, safety constraints, and inefficient execution of conventional VLA models that rely on real-world interaction, offering a practical and scalable solution for post-training in resource-constrained settings. Our code is available at https://github.com/amap-cvlab/world-env.

