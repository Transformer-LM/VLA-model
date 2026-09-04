---
type: paper
node_id: paper:assran2025_vjepa_selfsupervised_video
title: "V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning"
authors: ["Mido Assran", "Adrien Bardes", "David Fan", "Quentin Garrido", "Russell Howes", "Mojtaba", "Komeili", "Matthew Muckley", "Ammar Rizvi", "Claire Roberts", "Koustuv Sinha", "Artem Zholus", "Sergio Arnaud", "Abha Gejji", "Ada Martin", "Francois Robert Hogan", "Daniel Dugas", "Piotr Bojanowski", "Vasil Khalidov", "Patrick Labatut", "Francisco Massa", "Marc Szafraniec", "Kapil Krishnakumar", "Yong Li", "Xiaodong Ma", "Sarath Chandar", "Franziska Meier", "Yann LeCun", "Michael Rabbat", "Nicolas Ballas"]
year: 2025
venue: "arXiv"
external_ids:
  arxiv: "2506.09985"
  doi: null
  s2: null
tags: ["latent-dynamics", "video-pretraining", "planning"]
added: 2026-08-06T07:52:51Z
---

# V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning

## One-line thesis
V-JEPA 2以大规模自监督视频latent及少量机器人视频后训练实现零样本图像目标规划。

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

> A major challenge for modern AI is to learn to understand the world and learn to act largely by observation. This paper explores a self-supervised approach that combines internet-scale video data with a small amount of interaction data (robot trajectories), to develop models capable of understanding, predicting, and planning in the physical world. We first pre-train an action-free joint-embedding-predictive architecture, V-JEPA 2, on a video and image dataset comprising over 1 million hours of internet video. V-JEPA 2 achieves strong performance on motion understanding (77.3 top-1 accuracy on Something-Something v2) and state-of-the-art performance on human action anticipation (39.7 recall-at-5 on Epic-Kitchens-100) surpassing previous task-specific models. Additionally, after aligning V-JEPA 2 with a large language model, we demonstrate state-of-the-art performance on multiple video question-answering tasks at the 8 billion parameter scale (e.g., 84.0 on PerceptionTest, 76.9 on TempCompass). Finally, we show how self-supervised learning can be applied to robotic planning tasks by post-training a latent action-conditioned world model, V-JEPA 2-AC, using less than 62 hours of unlabeled robot videos from the Droid dataset. We deploy V-JEPA 2-AC zero-shot on Franka arms in two different labs and enable picking and placing of objects using planning with image goals. Notably, this is achieved without collecting any data from the robots in these environments, and without any task-specific training or reward. This work demonstrates how self-supervised learning from web-scale data and a small amount of robot interaction data can yield a world model capable of planning in the physical world.

