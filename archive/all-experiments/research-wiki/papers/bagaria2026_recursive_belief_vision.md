---
type: paper
node_id: paper:bagaria2026_recursive_belief_vision
title: "Recursive Belief Vision Language Action Models"
authors: ["Vaidehi Bagaria", "Bijo Sebastian", "Nirav Kumar Patel"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2602.20659"
  doi: null
  s2: null
tags: ["vla-wam", "h4", "belief", "memory"]
added: 2026-08-06T13:10:37Z
---

# Recursive Belief Vision Language Action Models

## One-line thesis
用 action-conditioned latent belief 的世界目标维护部分可观测状态，并将其反馈给语言条件动作策略。

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

> Vision-language-action models must enable agents to execute long-horizon tasks under partial observability. However, most existing approaches remain observation-driven, relying on short context windows or repeated queries to vision-language models (VLMs). This leads to loss of task progress, action repetition under perceptual aliasing, and high inference latency. While semantic grounding is important, long-horizon manipulation fundamentally requires persistent, action-conditioned state representations. Current VLAs lack such representations and exhibit limited temporal and physical reasoning, making them ill-suited for multi-stage control. This paper introduces RB-VLA, a belief-centric architecture trained with self-supervised world-model objectives that maintains a compact latent state encoding task-relevant history, dynamics, and object interactions. Queried once per task, the VLM provides high-level intent, while the belief tracks task progress and enables phase-aware, causally grounded control under partial observability without storing raw observations or scaling memory with time. The belief and intent jointly condition a diffusion policy for robust closed-loop execution. RB-VLA outperforms prior VLAs on long-horizon benchmarks, achieving 52.5 percent and 37.5 percent higher success rates on multi-stage pick-and-place and stacking tasks, respectively, compared to pi_0. It also reduces inference latency by up to five times relative to baselines and eliminates memory growth across timesteps observed in existing VLAs. Ablations show the belief module is the primary driver of performance, increasing success rates from 32.5 percent without belief to 77.5 percent with belief.

