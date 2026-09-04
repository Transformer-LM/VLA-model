---
type: paper
node_id: paper:he2025_scaling_crossembodiment_world
title: "Scaling Cross-Embodiment World Models for Dexterous Manipulation"
authors: ["Zihao He", "Bo Ai", "Tongzhou Mu", "Yulin Liu", "Weikang Wan", "Jiawei Fu", "Yilun Du", "Henrik I. Christensen", "Hao Su"]
year: 2025
venue: "arXiv"
external_ids:
  arxiv: "2511.01177"
  doi: null
  s2: null
tags: ["cross-embodiment", "action-interface", "world-model", "transfer"]
added: 2026-08-06T08:35:27Z
---

# Scaling Cross-Embodiment World Models for Dexterous Manipulation

## One-line thesis
以跨形态共享的粒子状态和位移动作表示训练 world model，使不同手和机器人能共享环境动力学。

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

> Cross-embodiment learning seeks to build generalist robots that learn from and operate across diverse morphologies, but differences in kinematics and action spaces hinder data sharing and control transfer. We ask: What structure can be shared across embodiments despite these differences? We argue that the physical interactions they induce can be modeled in a shared geometric space, allowing world models to provide a common interface for learning and control. To realize this idea, we represent human and robot hands as sets of 3D particles and define actions as end-effector particle displacement fields. This representation abstracts away embodiment-specific joint spaces while preserving the geometry and motion relevant to physical interaction. We train a graph-based world model on random interaction data from diverse simulated robot hands and real human hands, and integrate it with model-predictive control for deployment on new hardware. Experiments on rigid and deformable manipulation reveal three findings: increasing the diversity of training embodiments improves generalization to unseen hands; appropriately combining simulated and real-world data outperforms either source alone; and the same learned model enables effective control on robotic hands with distinct kinematics and degrees of freedom. These results position particle-based world models as a shared interface for learning from and for heterogeneous embodiments.

