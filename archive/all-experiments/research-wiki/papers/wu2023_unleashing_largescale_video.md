---
type: paper
node_id: paper:wu2023_unleashing_largescale_video
title: "Unleashing Large-Scale Video Generative Pre-training for Visual Robot Manipulation"
authors: ["Hongtao Wu", "Ya Jing", "Chilam Cheang", "Guangzeng Chen", "Jiafeng Xu", "Xinghang Li", "Minghuan Liu", "Hang Li", "Tao Kong"]
year: 2023
venue: "arXiv"
external_ids:
  arxiv: "2312.13139"
  doi: null
  s2: null
tags: ["joint-world-action", "video-pretraining", "vla"]
added: 2026-08-06T07:52:53Z
---

# Unleashing Large-Scale Video Generative Pre-training for Visual Robot Manipulation

## One-line thesis
GR-1联合预测未来图像和动作，检验大规模视频生成预训练对操控泛化的作用。

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

> Generative pre-trained models have demonstrated remarkable effectiveness in language and vision domains by learning useful representations. In this paper, we extend the scope of this effectiveness by showing that visual robot manipulation can significantly benefit from large-scale video generative pre-training. We introduce GR-1, a straightforward GPT-style model designed for multi-task language-conditioned visual robot manipulation. GR-1 takes as inputs a language instruction, a sequence of observation images, and a sequence of robot states. It predicts robot actions as well as future images in an end-to-end manner. Thanks to a flexible design, GR-1 can be seamlessly finetuned on robot data after pre-trained on a large-scale video dataset. We perform extensive experiments on the challenging CALVIN benchmark and a real robot. On CALVIN benchmark, our method outperforms state-of-the-art baseline methods and improves the success rate from 88.9% to 94.9%. In the setting of zero-shot unseen scene generalization, GR-1 improves the success rate from 53.3% to 85.4%. In real robot experiments, GR-1 also outperforms baseline methods and shows strong potentials in generalization to unseen scenes and objects. We provide inaugural evidence that a unified GPT-style transformer, augmented with large-scale video generative pre-training, exhibits remarkable generalization to multi-task visual robot manipulation. Project page: https://GR1-Manipulation.github.io

