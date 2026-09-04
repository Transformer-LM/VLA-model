---
type: paper
node_id: paper:wang2026_incontext_world_modeling
title: "In-Context World Modeling for Robotic Control"
authors: ["Siyin Wang", "Junhao Shi", "Senyu Fei", "Zhaoyang Fu", "Li Ji", "Jingjing Gong", "Xipeng Qiu"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2606.26025"
  doi: null
  s2: null
tags: ["system-identification", "adaptation", "vla", "world-model"]
added: 2026-08-06T08:35:24Z
---

# In-Context World Modeling for Robotic Control

## One-line thesis
把新相机、身体与系统配置的识别转化为短历史中的 in-context world modeling，可在不更新参数时适应新执行环境。

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

> Modern Vision-Language-Action (VLA) models often fail to generalize to novel setups, such as altered camera viewpoints or robot morphologies, because they are typically conditioned only on current observations and language instructions. By ignoring the underlying system configuration as a variable, these models implicitly assume a fixed execution context encountered during training, necessitating data-intensive fine-tuning for any new environment. In this work, we introduce In-Context World Modeling (ICWM), a framework that treats system identification as an in-context adaptation problem. ICWM enables robot policies to autonomously infer essential system variables from a short history of self-generated, task-agnostic interactions. Unlike traditional In-Context Learning that uses demonstrations to specify what task to perform, ICWM leverages the context window to understand how the system operates. By processing these interactions before task execution, the model implicitly captures the world dynamics of the current system, enabling adaptation to novel configurations without parameter updates. Extensive experiments in simulation and on real-world robot platforms demonstrate that ICWM significantly outperforms standard VLA baselines on novel camera viewpoints.

