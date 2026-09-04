---
type: paper
node_id: paper:liu2024_rdt1b_diffusion_foundation
title: "RDT-1B: a Diffusion Foundation Model for Bimanual Manipulation"
authors: ["Songming Liu", "Lingxuan Wu", "Bangguo Li", "Hengkai Tan", "Huayu Chen", "Zhengyi Wang", "Ke Xu", "Hang Su", "Jun Zhu"]
year: 2024
venue: "arXiv"
external_ids:
  arxiv: "2410.07864"
  doi: null
  s2: null
tags: ["vla", "diffusion", "bimanual"]
added: 2026-08-06T09:21:16Z
---

# RDT-1B: a Diffusion Foundation Model for Bimanual Manipulation

## One-line thesis
Scales a diffusion foundation model for bimanual manipulation across embodiments.

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

> Bimanual manipulation is essential in robotics, yet developing foundation models is extremely challenging due to the inherent complexity of coordinating two robot arms (leading to multi-modal action distributions) and the scarcity of training data. In this paper, we present the Robotics Diffusion Transformer (RDT), a pioneering diffusion foundation model for bimanual manipulation. RDT builds on diffusion models to effectively represent multi-modality, with innovative designs of a scalable Transformer to deal with the heterogeneity of multi-modal inputs and to capture the nonlinearity and high frequency of robotic data. To address data scarcity, we further introduce a Physically Interpretable Unified Action Space, which can unify the action representations of various robots while preserving the physical meanings of original actions, facilitating learning transferrable physical knowledge. With these designs, we managed to pre-train RDT on the largest collection of multi-robot datasets to date and scaled it up to 1.2B parameters, which is the largest diffusion-based foundation model for robotic manipulation. We finally fine-tuned RDT on a self-created multi-task bimanual dataset with over 6K+ episodes to refine its manipulation capabilities. Experiments on real robots demonstrate that RDT significantly outperforms existing methods. It exhibits zero-shot generalization to unseen objects and scenes, understands and follows language instructions, learns new skills with just 1~5 demonstrations, and effectively handles complex, dexterous tasks. We refer to https://rdt-robotics.github.io/rdt-robotics/ for the code and videos.

