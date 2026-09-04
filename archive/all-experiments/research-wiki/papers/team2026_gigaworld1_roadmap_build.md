---
type: paper
node_id: paper:team2026_gigaworld1_roadmap_build
title: "GigaWorld-1: A Roadmap to Build World Models for Robot Policy Evaluation"
authors: ["GigaWorld Team", "Angyuan Ma", "Boyuan Wang", "Bohan Li", "Chaojun Ni", "Guo Li", "Guan Huang", "Guosheng Zhao", "Hao Li", "Hengtao Li", "Jingyu Liu", "Jiwen Lu", "Qiuping Deng", "Tingdong Yu", "Xuancheng Xu", "Xinyu Zhou", "Xiuwei Xu", "Xinze Chen", "Xiaofeng Wang", "Xiaoyu Tian", "Yang Wang", "Yifan Chang", "Yukun Zhou", "Yun Ye", "Zhenyu Wu", "Zhanqian Wu", "Zheng Zhu"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2607.02642"
  doi: null
  s2: null
tags: ["vla-wam", "h9", "policy-evaluation", "calibration"]
added: 2026-08-06T13:10:43Z
---

# GigaWorld-1: A Roadmap to Build World Models for Robot Policy Evaluation

## One-line thesis
以配对真实与想象 rollout 系统研究机器人策略评测中的动作编码、记忆、时域与校准。

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

> Evaluating embodied robot foundation models remains a critical bottleneck; unlike large language models efficiently assessed via digital benchmarks, robotic policies require slow, costly real-world rollouts limited by hardware and human supervision, which has driven interest in world models as surrogate policy evaluators, yet the key properties that make a world model reliable for policy assessment remain poorly understood. This work presents a systematic study of world models for robotic policy evaluation and introduces WMBench, a benchmark constructed from real-robot teleoperation data and matched policy rollouts covering diverse manipulation tasks to enable controlled comparisons across model families, action encodings, rollout horizons, and evaluation metrics. Using WMBench, we analyze 7 video world models, 4 action representation schemes, and over 324,000 simulated policy rollouts paired with real robot executions, further enriching our analysis with large-scale community submissions from the CVPR 2026 GigaBrain Challenge, curated synthetic trajectories, and a training videos spanning more than 12,000 hours. Our experiments deliver three core insights: evaluator quality is dominated by long-horizon, action-faithful rollout consistency rather than short-term visual realism; pretraining gains stem not only from data scale but from balancing general world knowledge with robot-specific controllability; and architectural choices including action encoding, memory design, and evaluator-focused post-training strongly determine alignment with real-world robot behavior. Drawing on these results, we derive a practical design roadmap and realize it in \textit{GigaWorld-1}, a world model specially optimized for policy evaluation, and we fully release our code, models, datasets, and toolkits to advance scalable evaluation research for embodied foundation models.

