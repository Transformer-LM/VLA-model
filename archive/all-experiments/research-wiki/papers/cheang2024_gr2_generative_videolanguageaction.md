---
type: paper
node_id: paper:cheang2024_gr2_generative_videolanguageaction
title: "GR-2: A Generative Video-Language-Action Model with Web-Scale Knowledge for Robot Manipulation"
authors: ["Chi-Lam Cheang", "Guangzeng Chen", "Ya Jing", "Tao Kong", "Hang Li", "Yifeng Li", "Yuxiao Liu", "Hongtao Wu", "Jiafeng Xu", "Yichu Yang", "Hanbo Zhang", "Minzhao Zhu"]
year: 2024
venue: "arXiv"
external_ids:
  arxiv: "2410.06158"
  doi: null
  s2: null
tags: ["joint-world-action", "video-pretraining", "vla"]
added: 2026-08-06T07:52:54Z
---

# GR-2: A Generative Video-Language-Action Model with Web-Scale Knowledge for Robot Manipulation

## One-line thesis
GR-2在大规模视频预训练后联合微调视频生成与动作预测。

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

> We present GR-2, a state-of-the-art generalist robot agent for versatile and generalizable robot manipulation. GR-2 is first pre-trained on a vast number of Internet videos to capture the dynamics of the world. This large-scale pre-training, involving 38 million video clips and over 50 billion tokens, equips GR-2 with the ability to generalize across a wide range of robotic tasks and environments during subsequent policy learning. Following this, GR-2 is fine-tuned for both video generation and action prediction using robot trajectories. It exhibits impressive multi-task learning capabilities, achieving an average success rate of 97.7% across more than 100 tasks. Moreover, GR-2 demonstrates exceptional generalization to new, previously unseen scenarios, including novel backgrounds, environments, objects, and tasks. Notably, GR-2 scales effectively with model size, underscoring its potential for continued growth and application. Project page: \url{https://gr2-manipulation.github.io}.

