---
type: paper
node_id: paper:higuera2026_visuotactile_world_models
title: "Visuo-Tactile World Models"
authors: ["Carolina Higuera", "Sergio Arnaud", "Byron Boots", "Mustafa Mukadam", "Francois Robert Hogan", "Franziska Meier"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2602.06001"
  doi: null
  s2: null
tags: ["visuo-tactile", "contact", "world-model", "planning"]
added: 2026-08-06T08:35:29Z
---

# Visuo-Tactile World Models

## One-line thesis
视觉—触觉 world model通过接触信号改善遮挡和歧义条件下的物理 rollout，并把接触动力学连接到规划。

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

> We introduce multi-task Visuo-Tactile World Models (VT-WM), which capture the physics of contact through touch reasoning. By complementing vision with tactile sensing, VT-WM better understands robot-object interactions in contact-rich tasks, avoiding common failure modes of vision-only models under occlusion or ambiguous contact states, such as objects disappearing, teleporting, or moving in ways that violate basic physics. Trained across a set of contact-rich manipulation tasks, VT-WM improves physical fidelity in imagination, achieving 33% better performance at maintaining object permanence and 29% better compliance with the laws of motion in autoregressive rollouts. Moreover, experiments show that grounding in contact dynamics also translates to planning. In zero-shot real-robot experiments, VT-WM achieves up to 35% higher success rates, with the largest gains in multi-step, contact-rich tasks. Finally, VT-WM demonstrates significant downstream versatility, effectively adapting its learned contact dynamics to a novel task and achieving reliable planning success with only a limited set of demonstrations.

