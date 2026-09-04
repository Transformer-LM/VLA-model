---
type: paper
node_id: paper:ye2026_world_action_models
title: "World Action Models are Zero-shot Policies"
authors: ["Seonghyeon Ye", "Yunhao Ge", "Kaiyuan Zheng", "Shenyuan Gao", "Sihyun Yu", "George Kurian", "Suneel Indupuru", "You Liang Tan", "Chuning Zhu", "Jiannan Xiang", "Ayaan Malik", "Kyungmin Lee", "William Liang", "Nadun Ranawaka", "Jiasheng Gu", "Yinzhen Xu", "Guanzhi Wang", "Fengyuan Hu", "Avnish Narayan", "Johan Bjorck", "Jing Wang", "Gwanghyun Kim", "Dantong Niu", "Ruijie Zheng", "Yuqi Xie", "Jimmy Wu", "Qi Wang", "Ryan Julian", "Danfei Xu", "Yilun Du", "Yevgen Chebotar", "Scott Reed", "Jan Kautz", "Yuke Zhu", "Linxi \"Jim\" Fan", "Joel Jang"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2602.15922"
  doi: null
  s2: null
tags: ["world-action-model", "joint-generation", "cross-embodiment"]
added: 2026-08-06T07:52:55Z
---

# World Action Models are Zero-shot Policies

## One-line thesis
DreamZero以预训练视频扩散骨干联合生成视频与动作并实现闭环WAM控制。

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

> State-of-the-art Vision-Language-Action (VLA) models excel at semantic generalization but struggle to generalize to unseen physical motions in novel environments. We introduce DreamZero, a World Action Model (WAM) built upon a pretrained video diffusion backbone. Unlike VLAs, WAMs learn physical dynamics by predicting future world states and actions, using video as a dense representation of how the world evolves. By jointly modeling video and action, DreamZero learns diverse skills effectively from heterogeneous robot data without relying on repetitive demonstrations. This results in over 2x improvement in generalization to new tasks and environments compared to state-of-the-art VLAs in real robot experiments. Crucially, through model and system optimizations, we enable a 14B autoregressive video diffusion model to perform real-time closed-loop control at 7Hz. Finally, we demonstrate two forms of cross-embodiment transfer: video-only demonstrations from other robots or humans yield a relative improvement of over 42% on unseen task performance with just 10-20 minutes of data. More surprisingly, DreamZero enables few-shot embodiment adaptation, transferring to a new embodiment with only 30 minutes of play data while retaining zero-shot generalization.

