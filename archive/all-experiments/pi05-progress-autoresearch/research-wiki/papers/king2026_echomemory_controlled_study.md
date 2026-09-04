---
type: paper
node_id: paper:king2026_echomemory_controlled_study
title: "Echo-Memory: A Controlled Study of Memory in Action World Models"
authors: ["Wayne King", "Zeyue Xue", "Yuxuan Bian", "Jie Huang", "Haoran Li", "Yaowei Li", "Yaofeng Su", "Yuming Li", "Haoyu Wang", "Shiyi Zhang", "Songchun Zhang", "Yuwei Niu", "Sihan Xu", "Junhao Zhuang", "Haoyang Huang", "Nan Duan"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2606.09803"
  doi: null
  s2: null
tags: []
added: 2026-08-24T06:39:56Z
---

# Echo-Memory: A Controlled Study of Memory in Action World Models

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

> We present \textbf{Echo-Memory}, a controlled study of memory mechanisms in action-conditioned world models. These models generate multi-segment videos from a first frame, text prompt, and camera-action sequence, but their central failure is often memory rather than local image synthesis: after the camera leaves and returns, the scene or salient object may silently change. Existing memory designs are hard to compare because gains are entangled with backbone, training, retrieval, and evaluation differences. Echo-Memory fixes the action-to-video interface and varies only how history is stored and read by the generator. Under a shared video diffusion backbone, optimizer, camera-action representation, sampler, and evaluation pipeline, we compare raw context, compression-based memory, spatial summaries with different read-out paths, and state-space recurrence. This matched matrix separates four otherwise conflated axes: \emph{capacity}, \emph{compression}, \emph{read-out}, and \emph{recurrence}. We also evaluate memory through a three-branch protocol: replay quality, in-domain loop revisit, and open-domain return probes. The branches routinely disagree, showing that replay fidelity is not a sufficient proxy for remembering a world. Three findings follow. Raw context is a strong capacity baseline and improves open-domain return far more than it improves replay metrics. Compactness is not a free substitute for capacity: aggressive spatial and hybrid-compression memories lose the salient evidence needed for return. Finally, block-wise state-space recurrence is the strongest open-domain return mechanism in our matrix, showing that the structure of implicit memory matters as much as the decision to use it. These results provide a compact protocol for studying memory in action world models beyond isolated replay metrics.

