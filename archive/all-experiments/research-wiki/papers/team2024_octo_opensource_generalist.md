---
type: paper
node_id: paper:team2024_octo_opensource_generalist
title: "Octo: An Open-Source Generalist Robot Policy"
authors: ["Octo Model Team", "Dibya Ghosh", "Homer Walke", "Karl Pertsch", "Kevin Black", "Oier Mees", "Sudeep Dasari", "Joey Hejna", "Tobias Kreiman", "Charles Xu", "Jianlan Luo", "You Liang Tan", "Lawrence Yunliang Chen", "Pannag Sanketi", "Quan Vuong", "Ted Xiao", "Dorsa Sadigh", "Chelsea Finn", "Sergey Levine"]
year: 2024
venue: "arXiv"
external_ids:
  arxiv: "2405.12213"
  doi: null
  s2: null
tags: ["vla", "generalist-policy", "adaptation"]
added: 2026-08-06T09:21:14Z
---

# Octo: An Open-Source Generalist Robot Policy

## One-line thesis
Provides an open generalist policy trained across heterogeneous robot data.

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

> Large policies pretrained on diverse robot datasets have the potential to transform robotic learning: instead of training new policies from scratch, such generalist robot policies may be finetuned with only a little in-domain data, yet generalize broadly. However, to be widely applicable across a range of robotic learning scenarios, environments, and tasks, such policies need to handle diverse sensors and action spaces, accommodate a variety of commonly used robotic platforms, and finetune readily and efficiently to new domains. In this work, we aim to lay the groundwork for developing open-source, widely applicable, generalist policies for robotic manipulation. As a first step, we introduce Octo, a large transformer-based policy trained on 800k trajectories from the Open X-Embodiment dataset, the largest robot manipulation dataset to date. It can be instructed via language commands or goal images and can be effectively finetuned to robot setups with new sensory inputs and action spaces within a few hours on standard consumer GPUs. In experiments across 9 robotic platforms, we demonstrate that Octo serves as a versatile policy initialization that can be effectively finetuned to new observation and action spaces. We also perform detailed ablations of design decisions for the Octo model, from architecture to training data, to guide future research on building generalist robot models.

