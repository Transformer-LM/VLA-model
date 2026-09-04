---
type: paper
node_id: paper:yin2025_womap_world_models
title: "WoMAP: World Models For Embodied Open-Vocabulary Object Localization"
authors: ["Tenny Yin", "Zhiting Mei", "Tao Sun", "Lihan Zha", "Emily Zhou", "Jeremy Bao", "Miyu Yamane", "Ola Shorinwa", "Anirudha Majumdar"]
year: 2025
venue: "arXiv"
external_ids:
  arxiv: "2506.01600"
  doi: null
  s2: null
tags: ["vla-wam", "h7", "active-perception", "planning"]
added: 2026-08-06T13:10:40Z
---

# WoMAP: World Models For Embodied Open-Vocabulary Object Localization

## One-line thesis
VLM 提议开放词汇探索动作，潜在动力学与奖励世界模型负责物理落地和信息搜集。

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

> Language-instructed active object localization is a critical challenge for robots, requiring efficient exploration of partially observable environments. However, state-of-the-art approaches either struggle to generalize beyond demonstration datasets (e.g., imitation learning methods) or fail to generate physically grounded actions (e.g., VLMs). To address these limitations, we introduce WoMAP (World Models for Active Perception): a recipe for training open-vocabulary object localization policies that: (i) uses a Gaussian Splatting-based real-to-sim-to-real pipeline for scalable data generation without the need for expert demonstrations, (ii) distills dense rewards signals from open-vocabulary object detectors, and (iii) leverages a latent world model for dynamics and rewards prediction to ground high-level action proposals at inference time. Rigorous simulation and hardware experiments demonstrate WoMAP's superior performance in a broad range of zero-shot object localization tasks, with more than 9x and 2x higher success rates compared to VLM and diffusion policy baselines, respectively. Further, we show that WoMAP achieves strong generalization and sim-to-real transfer on a TidyBot.

