---
type: paper
node_id: paper:kim2024_openvla_opensource_visionlanguageaction
title: "OpenVLA: An Open-Source Vision-Language-Action Model"
authors: ["Moo Jin Kim", "Karl Pertsch", "Siddharth Karamcheti", "Ted Xiao", "Ashwin Balakrishna", "Suraj Nair", "Rafael Rafailov", "Ethan Foster", "Grace Lam", "Pannag Sanketi", "Quan Vuong", "Thomas Kollar", "Benjamin Burchfiel", "Russ Tedrake", "Dorsa Sadigh", "Sergey Levine", "Percy Liang", "Chelsea Finn"]
year: 2024
venue: "arXiv"
external_ids:
  arxiv: "2406.09246"
  doi: null
  s2: null
tags: ["vla", "open-model", "adaptation"]
added: 2026-08-06T09:21:14Z
---

# OpenVLA: An Open-Source Vision-Language-Action Model

## One-line thesis
Open-sources a 7B VLA and efficient downstream adaptation stack.

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

> Large policies pretrained on a combination of Internet-scale vision-language data and diverse robot demonstrations have the potential to change how we teach robots new skills: rather than training new behaviors from scratch, we can fine-tune such vision-language-action (VLA) models to obtain robust, generalizable policies for visuomotor control. Yet, widespread adoption of VLAs for robotics has been challenging as 1) existing VLAs are largely closed and inaccessible to the public, and 2) prior work fails to explore methods for efficiently fine-tuning VLAs for new tasks, a key component for adoption. Addressing these challenges, we introduce OpenVLA, a 7B-parameter open-source VLA trained on a diverse collection of 970k real-world robot demonstrations. OpenVLA builds on a Llama 2 language model combined with a visual encoder that fuses pretrained features from DINOv2 and SigLIP. As a product of the added data diversity and new model components, OpenVLA demonstrates strong results for generalist manipulation, outperforming closed models such as RT-2-X (55B) by 16.5% in absolute task success rate across 29 tasks and multiple robot embodiments, with 7x fewer parameters. We further show that we can effectively fine-tune OpenVLA for new settings, with especially strong generalization results in multi-task environments involving multiple objects and strong language grounding abilities, and outperform expressive from-scratch imitation learning methods such as Diffusion Policy by 20.4%. We also explore compute efficiency; as a separate contribution, we show that OpenVLA can be fine-tuned on consumer GPUs via modern low-rank adaptation methods and served efficiently via quantization without a hit to downstream success rate. Finally, we release model checkpoints, fine-tuning notebooks, and our PyTorch codebase with built-in support for training VLAs at scale on Open X-Embodiment datasets.

