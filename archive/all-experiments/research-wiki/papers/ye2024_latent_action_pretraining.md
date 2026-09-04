---
type: paper
node_id: paper:ye2024_latent_action_pretraining
title: "Latent Action Pretraining from Videos"
authors: ["Seonghyeon Ye", "Joel Jang", "Byeongguk Jeon", "Sejune Joo", "Jianwei Yang", "Baolin Peng", "Ajay Mandlekar", "Reuben Tan", "Yu-Wei Chao", "Bill Yuchen Lin", "Lars Liden", "Kimin Lee", "Jianfeng Gao", "Luke Zettlemoyer", "Dieter Fox", "Minjoon Seo"]
year: 2024
venue: "arXiv"
external_ids:
  arxiv: "2410.11758"
  doi: null
  s2: null
tags: ["latent-action", "video-pretraining", "vla"]
added: 2026-08-06T07:52:50Z
---

# Latent Action Pretraining from Videos

## One-line thesis
LAPA从无动作标签视频学习离散latent actions以预训练VLA。

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

> We introduce Latent Action Pretraining for general Action models (LAPA), an unsupervised method for pretraining Vision-Language-Action (VLA) models without ground-truth robot action labels. Existing Vision-Language-Action models require action labels typically collected by human teleoperators during pretraining, which significantly limits possible data sources and scale. In this work, we propose a method to learn from internet-scale videos that do not have robot action labels. We first train an action quantization model leveraging VQ-VAE-based objective to learn discrete latent actions between image frames, then pretrain a latent VLA model to predict these latent actions from observations and task descriptions, and finally finetune the VLA on small-scale robot manipulation data to map from latent to robot actions. Experimental results demonstrate that our method significantly outperforms existing techniques that train robot manipulation policies from large-scale videos. Furthermore, it outperforms the state-of-the-art VLA model trained with robotic action labels on real-world manipulation tasks that require language conditioning, generalization to unseen objects, and semantic generalization to unseen instructions. Training only on human manipulation videos also shows positive transfer, opening up the potential for leveraging web-scale data for robotics foundation model.

