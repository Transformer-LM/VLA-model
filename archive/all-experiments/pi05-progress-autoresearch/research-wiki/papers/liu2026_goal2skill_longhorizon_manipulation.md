---
type: paper
node_id: paper:liu2026_goal2skill_longhorizon_manipulation
title: "Goal2Skill: Long-Horizon Manipulation with Adaptive Planning and Reflection"
authors: ["Zhen Liu", "Xinyu Ning", "Zhe Hu", "Xinxin Xie", "Weize Li", "Zhipeng Tang", "Chongyu Wang", "Zejun Yang", "Hanlin Wang", "Yitong Liu", "Zhongzhu Pu"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2604.13942"
  doi: null
  s2: null
tags: []
added: 2026-08-24T03:48:18Z
---

# Goal2Skill: Long-Horizon Manipulation with Adaptive Planning and Reflection

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

> Recent vision-language-action (VLA) systems have demonstrated strong capabilities in embodied manipulation. However, most existing VLA policies rely on limited observation windows and end-to-end action prediction, which makes them brittle in long-horizon, memory-dependent tasks with partial observability, occlusions, and multi-stage dependencies. Such tasks require not only precise visuomotor control, but also persistent memory, adaptive task decomposition, and explicit recovery from execution failures. To address these limitations, we propose a dual-system framework for long-horizon embodied manipulation. Our framework explicitly separates high-level semantic reasoning from low-level motor execution. A high-level planner, implemented as a VLM-based agentic module, maintains structured task memory and performs goal decomposition, outcome verification, and error-driven correction. A low-level executor, instantiated as a VLA-based visuomotor controller, carries out each sub-task through diffusion-based action generation conditioned on geometry-preserving filtered observations. Together, the two systems form a closed loop between planning and execution, enabling memory-aware reasoning, adaptive replanning, and robust online recovery. Experiments on representative RMBench tasks show that the proposed framework substantially outperforms representative baselines, achieving a 32.4% average success rate compared with 9.8% for the strongest baseline. Ablation studies further confirm the importance of structured memory and closed-loop recovery for long-horizon manipulation.

