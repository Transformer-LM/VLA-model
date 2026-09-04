---
type: paper
node_id: paper:bu2025_univla_learning_act
title: "UniVLA: Learning to Act Anywhere with Task-centric Latent Actions"
authors: ["Qingwen Bu", "Yanting Yang", "Jisong Cai", "Shenyuan Gao", "Guanghui Ren", "Maoqing Yao", "Ping Luo", "Hongyang Li"]
year: 2025
venue: "arXiv"
external_ids:
  arxiv: "2505.06111"
  doi: null
  s2: null
tags: ["vla-wam", "h2", "latent-action", "cross-embodiment"]
added: 2026-08-06T13:10:36Z
---

# UniVLA: Learning to Act Anywhere with Task-centric Latent Actions

## One-line thesis
以任务语义约束的潜在动作连接无动作人类视频、多本体机器人数据与可执行 VLA。

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

> A generalist robot should perform effectively across various environments. However, most existing approaches heavily rely on scaling action-annotated data to enhance their capabilities. Consequently, they are often limited to single physical specification and struggle to learn transferable knowledge across different embodiments and environments. To confront these limitations, we propose UniVLA, a new framework for learning cross-embodiment vision-language-action (VLA) policies. Our key innovation is to derive task-centric action representations from videos with a latent action model. This enables us to exploit extensive data across a wide spectrum of embodiments and perspectives. To mitigate the effect of task-irrelevant dynamics, we incorporate language instructions and establish a latent action model within the DINO feature space. Learned from internet-scale videos, the generalist policy can be deployed to various robots through efficient latent action decoding. We obtain state-of-the-art results across multiple manipulation and navigation benchmarks, as well as real-robot deployments. UniVLA achieves superior performance over OpenVLA with less than 1/20 of pretraining compute and 1/10 of downstream data. Continuous performance improvements are observed as heterogeneous data, even including human videos, are incorporated into the training pipeline. The results underscore UniVLA's potential to facilitate scalable and efficient robot policy learning.

