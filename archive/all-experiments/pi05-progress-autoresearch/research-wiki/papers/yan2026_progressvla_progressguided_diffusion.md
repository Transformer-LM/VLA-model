---
type: paper
node_id: paper:yan2026_progressvla_progressguided_diffusion
title: "ProgressVLA: Progress-Guided Diffusion Policy for Vision-Language Robotic Manipulation"
authors: ["Hongyu Yan", "Qiwei Li", "Jiaolong Yang", "Yadong Mu"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2603.27670"
  doi: null
  s2: null
tags: []
added: 2026-08-24T03:48:18Z
---

# ProgressVLA: Progress-Guided Diffusion Policy for Vision-Language Robotic Manipulation

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

> Most existing vision-language-action (VLA) models for robotic manipulation lack progress awareness, typically relying on hand-crafted heuristics for task termination. This limitation is particularly severe in long-horizon tasks involving cascaded sub-goals. In this work, we investigate the estimation and integration of task progress, proposing a novel model named {\textbf \vla}. Our technical contributions are twofold: (1) \emph{robust progress estimation}: We pre-train a progress estimator on large-scale, unsupervised video-text robotic datasets. This estimator achieves a low prediction residual (0.07 on a scale of $[0, 1]$) in simulation and demonstrates zero-shot generalization to unseen real-world samples, and (2) \emph{differentiable progress guidance}: We introduce an inverse dynamics world model that maps predicted action tokens into future latent visual states. These latents are then processed by the progress estimator; by applying a maximal progress regularization, we establish a differentiable pipeline that provides progress-piloted guidance to refine action tokens. Extensive experiments on the CALVIN and LIBERO benchmarks, alongside real-world robot deployment, consistently demonstrate substantial improvements in success rates and generalization over strong baselines.

