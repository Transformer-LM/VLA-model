---
type: paper
node_id: paper:bhardwaj2026_decoding_task_progress
title: "Decoding Task Progress from VLA Representations"
authors: ["Atiksh Bhardwaj", "Edward Weiyi Duan", "Prithwish Dan", "Wei-Chiu Ma", "Preston Culbertson"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2608.13474"
  doi: null
  s2: null
tags: []
added: 2026-08-24T03:48:18Z
---

# Decoding Task Progress from VLA Representations

## One-line thesis
_TODO: fill in after reading._

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

> Vision-language-action models (VLAs) are moving rapidly towards deployment as general-purpose manipulation policies, but we currently lack basic tools for understanding what these models represent internally or for monitoring them at runtime. Leveraging ideas from mechanistic interpretability, we probe the residual stream of $π_{0.5}$ and find that task progress, the normalized time remaining in a trajectory, is linearly readable from the activations. We find that this signal is present in the pretrained PaliGemma backbone prior to training on any robot-specific data. A single linear probe generalizes to unseen tasks and varies under language counterfactuals when trained on multi-prompt data, but does not enable meaningful steering of the policy. These properties make the signal directly useful for instrumenting deployed VLAs. We use the probe as a simple label-free OOD detector, which detects stalled task progress, and find it competitive with state-of-the-art methods. Our results suggest that VLAs have rich, linearly readable internal representations of semantic quantities like task progress, and that learning to read these signals offers a lightweight, interpretable path toward monitoring deployed visuomotor policies.

