---
type: paper
node_id: paper:wu2026_tactilewam_touchaware_world
title: "Tactile-WAM: Touch-Aware World Action Model with Tactile Asymmetric Attention"
authors: ["Siyu Wu", "Linjing You", "Junjie Zhu", "Yaozu Liu", "Changhao Zhang", "Jian Liu", "Weiqiang Wang", "Qi Li", "Jituo Li", "Hengshuang Zhao"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2606.26663"
  doi: null
  s2: null
tags: ["vla-wam", "h3", "tactile", "contact"]
added: 2026-08-06T13:10:50Z
---

# Tactile-WAM: Touch-Aware World Action Model with Tactile Asymmetric Attention

## One-line thesis
联合预测视觉与触觉未来，并让动作生成显式消费预测到的接触变化。

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

> World Action Models (WAMs) generate actions together with predicted futures, offering a powerful interface for robot decision making. In contact-rich manipulation, however, visually plausible futures can be physically incomplete: insertion, assembly, search, and reorientation often depend on slip, jamming, contact normals, or small alignment errors that are weakly visible or hidden in RGB. A natural solution is to predict future tactile states, however, we identify tactile pollution, a failure mode where unconstrained tactile-token injection degrades video and action prediction by forcing a visual dynamics model to absorb sparse, local, event-driven contact signals. To address this, we propose Tactile-WAM, a touch-aware WAM with a Tactile Asymmetric Attention Mechanism (TAAM). TAAM combines a VideoClean mask, which blocks video-query access to tactile key/value tokens while preserving action-query access, with a touch-aware bias for action attention. The VideoClean mask protects visual prediction while keeping contact information available for action generation; the touch-aware bias is derived from predicted touch changes and modulates action attention to tactile tokens during denoising. On ManiFeel, Tactile-WAM improves the mean success rate by 38.9% overall and by 86% on contact-rich tasks.

