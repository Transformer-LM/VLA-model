---
type: paper
node_id: paper:chen2026_lawam_latent_world
title: "LaWAM: Latent World Action Models for Efficient Dynamics-Aware Robot Policies"
authors: ["Jialei Chen", "Kai Wang", "Kang Chen", "Shuaihang Chen", "Feng Gao", "Wenhao Tang", "Zhiyuan Li", "Weilin Liu", "Zhuyu Yao", "Boxun Li", "Yuanbo Xu", "Chao Yu"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2606.15768"
  doi: null
  s2: null
tags: ["vla-wam", "h2", "h5", "visual-subgoal"]
added: 2026-08-06T13:10:38Z
---

# LaWAM: Latent World Action Models for Efficient Dynamics-Aware Robot Policies

## One-line thesis
潜在动作条件世界模型预测视觉子目标，再由该子目标直接条件化 VLA 控制。

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

> Vision-Language-Action models (VLAs) leverage large-scale vision-language pretraining for semantic robot control, but often lack explicit foresight into how robot actions change the scene. World-Action Models (WAMs) address this limitation by conditioning policies on predicted futures, yet existing approaches typically rely on computationally expensive video generation with substantial pixel-level redundancy. We present LaWAM, a Latent World Action Model that exposes predictive dynamics to robot policies through compact latent visual subgoals instead of reconstructed future video. At the core of LaWAM is a latent-action-conditioned Latent World Model (LaWM). We obtain LaWM by training a latent action model in the latent space of a pretrained vision foundation model and repurposing its forward decoder to predict future observation features for scene evolution. LaWAM then conditions action generation on these predicted latent visual subgoals to enable dynamics-aware robot control. LaWAM achieves state-of-the-art or competitive success rates (SRs) across LIBERO (98.6% SR), RoboTwin (91.22% SR), and real-world manipulation tasks while retaining low-latency inference. LaWAM runs in 187 ms per action-chunk prediction and achieves up to 24x lower wall-clock latency than pixel-space WAMs.

