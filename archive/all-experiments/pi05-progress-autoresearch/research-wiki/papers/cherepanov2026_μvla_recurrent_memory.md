---
type: paper
node_id: paper:cherepanov2026_μvla_recurrent_memory
title: "$μ$VLA: On Recurrent Memory for Partially Observable Manipulation in VLA Models"
authors: ["Egor Cherepanov", "Nikita Kachaev", "Daniil Zelezetsky", "Aydar Bulatov", "Artem Pshenitsyn", "Yuri Kuratov", "Alexey Skrynnik", "Aleksandr I. Panov", "Alexey K. Kovalev"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2606.12497"
  doi: null
  s2: null
tags: []
added: 2026-08-24T03:48:18Z
---

# $μ$VLA: On Recurrent Memory for Partially Observable Manipulation in VLA Models

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

> Vision-language-action (VLA) models predict chunks of future actions from the current observation, an assumption that fails under partial observability, where decisions depend on information no longer visible. Existing memory-augmented VLAs simultaneously introduce recurrence, retrieval, compression modules, auxiliary objectives, hierarchical memory, or task-specific architectural changes, so the contribution of recurrence itself remains entangled with surrounding machinery. We present a controlled isolation study of recurrence in a strong pretrained VLA backbone. Our formulation augments the transformer with a small set of learnable memory tokens carried across timesteps and updated through self-attention, trained end to end with truncated backpropagation through time, with no auxiliary losses and no architectural changes. We instantiate this as $μ$VLA, a family of OpenVLA-OFT variants parameterized by memory width m, TBPTT length K, and the memory update rule (cross-step gradients or a detached EMA), so that recurrence is the only varying factor. On MIKASA-Robo, $μ$VLA improves average success rate on five training tasks from 0.42 to 0.84 at the strongest setting and reaches 0.23 on held-out tasks with the same memory structure versus 0.07 for the memoryless baseline. On tasks requiring different memory structure, performance remains near baseline. On LIBERO, the strongest recurrent variant achieves 96.2% average success, indicating no regression under full observability. We interpret these results as a calibration of the capability envelope of minimal in-backbone recurrence, identifying the regime in which it is sufficient and the regime where additional memory structure is required. Demos and videos can be found in https://avanturist322.github.io/mu-vla/.

