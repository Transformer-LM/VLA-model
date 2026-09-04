---
type: paper
node_id: paper:li2026_learning_actionable_manipulation
title: "Learning Actionable Manipulation Recovery via Counterfactual Failure Synthesis"
authors: ["Dayou Li", "Jiuzhou Lei", "Hao Wang", "Lulin Liu", "Yunhao Yang", "Zihan Wang", "Bangya Liu", "Minghui Zheng", "Zhiwen Fan"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2603.13528"
  doi: null
  s2: null
tags: []
added: 2026-08-24T06:39:56Z
---

# Learning Actionable Manipulation Recovery via Counterfactual Failure Synthesis

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

> While recent foundation models have significantly advanced robotic manipulation, these systems still struggle to autonomously recover from execution errors. Current failure-learning paradigms rely on either costly and unsafe real-world data collection or simulator-based perturbations, which introduce a severe sim-to-real gap. Furthermore, existing visual analyzers predominantly output coarse, binary diagnoses rather than the executable, trajectory-level corrections required for actual recovery. To bridge the gap between failure diagnosis and actionable recovery, we introduce Dream2Fix, a framework that synthesizes photorealistic, counterfactual failure rollouts directly from successful real-world demonstrations. By perturbing actions within a generative world model, Dream2Fix creates paired failure-correction data without relying on simulators. To ensure the generated data is physically viable for robot learning, we implement a structured verification mechanism that strictly filters rollouts for task validity, visual coherence, and kinematic safety. This engine produces a high-fidelity dataset of over 120k paired samples. Using this dataset, we fine-tune a vision-language model to jointly predict failure types and precise recovery trajectories, mapping visual anomalies directly to corrective actions. Extensive real-world robotic experiments show our approach achieves state-of-the-art correction accuracy, improving from 19.7% to 81.3% over prior baselines, and successfully enables zero-shot closed-loop failure recovery in physical deployments.

