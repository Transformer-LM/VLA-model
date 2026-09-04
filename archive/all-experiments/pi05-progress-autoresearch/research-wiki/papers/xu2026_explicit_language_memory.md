---
type: paper
node_id: paper:xu2026_explicit_language_memory
title: "Explicit Language Memory for Long-Horizon Planning in Vision-Language-Action Models"
authors: ["Houze Xu", "Jizhong Li", "Ziyi Ye"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2608.04765"
  doi: null
  s2: null
tags: []
added: 2026-08-24T03:48:18Z
---

# Explicit Language Memory for Long-Horizon Planning in Vision-Language-Action Models

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

> Vision-language-action (VLA) models provide a unified paradigm for connecting visual perception, language understanding, and robotic control. However, existing VLA models still face major challenges in long-horizon tasks: sparse expert demonstrations constrain cross-task compositional generalization; the non-Markovian nature of long-horizon tasks makes it difficult for policies conditioned only on current observations to maintain temporal consistency; limited closed-loop error correction allows execution errors to accumulate; and end-to-end action fine-tuning may weaken the high-level semantic representations of vision-language model (VLM) backbones. To address these issues, we propose a hierarchical long-horizon VLA architecture with an explicit language-memory module. The central idea is to convert discrete temporal observations into a coherent textual memory sequence with temporal logic. The system is decoupled into a high-level VLM and a low-level VLA: the high-level VLM performs semantic reasoning through a visual question answering training paradigm, while the low-level VLA executes precise continuous control conditioned on subtask instructions and visual observations. The high-level VLM recursively updates both language memory and subtask instructions using the previous memory as a contextual anchor, enabling persistent temporal tracking and dynamic correction during long-horizon execution. We evaluate the proposed method in multiple simulation environments and conduct sim-to-real experiments on a real robotic platform. The results demonstrate that explicit language memory improves the success rate and robustness of VLA models on complex long-horizon tasks while providing an interpretable semantic account of the decision process.

