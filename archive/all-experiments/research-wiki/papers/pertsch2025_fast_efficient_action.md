---
type: paper
node_id: paper:pertsch2025_fast_efficient_action
title: "FAST: Efficient Action Tokenization for Vision-Language-Action Models"
authors: ["Karl Pertsch", "Kyle Stachowicz", "Brian Ichter", "Danny Driess", "Suraj Nair", "Quan Vuong", "Oier Mees", "Chelsea Finn", "Sergey Levine"]
year: 2025
venue: "arXiv"
external_ids:
  arxiv: "2501.09747"
  doi: null
  s2: null
tags: ["vla", "action-tokenization", "control"]
added: 2026-08-06T09:21:17Z
---

# FAST: Efficient Action Tokenization for Vision-Language-Action Models

## One-line thesis
Introduces frequency-space action tokenization for high-rate dexterous VLA control.

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

> Autoregressive sequence models, such as Transformer-based vision-language action (VLA) policies, can be tremendously effective for capturing complex and generalizable robotic behaviors. However, such models require us to choose a tokenization of our continuous action signals, which determines how the discrete symbols predicted by the model map to continuous robot actions. We find that current approaches for robot action tokenization, based on simple per-dimension, per-timestep binning schemes, typically perform poorly when learning dexterous skills from high-frequency robot data. To address this challenge, we propose a new compression-based tokenization scheme for robot actions, based on the discrete cosine transform. Our tokenization approach, Frequency-space Action Sequence Tokenization (FAST), enables us to train autoregressive VLAs for highly dexterous and high-frequency tasks where standard discretization methods fail completely. Based on FAST, we release FAST+, a universal robot action tokenizer, trained on 1M real robot action trajectories. It can be used as a black-box tokenizer for a wide range of robot action sequences, with diverse action spaces and control frequencies. Finally, we show that, when combined with the pi0 VLA, our method can scale to training on 10k hours of robot data and match the performance of diffusion VLAs, while reducing training time by up to 5x.

