---
type: paper
node_id: paper:zeng2026_helm_harnessenhanced_longhorizon
title: "HELM: Harness-Enhanced Long-horizon Memory for Vision-Language-Action Manipulation"
authors: ["Zijian Zeng", "Fei Ding", "Huiming Yang", "Xianwei Li"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2604.18791"
  doi: null
  s2: null
tags: []
added: 2026-08-24T06:39:56Z
---

# HELM: Harness-Enhanced Long-horizon Memory for Vision-Language-Action Manipulation

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

> Vision-Language-Action (VLA) models fail systematically on long-horizon manipulation tasks despite strong short-horizon performance. We show that this failure is not resolved by extending context length alone in the current reactive execution setting; instead, it stems from three recurring execution-loop deficiencies: the memory gap, the verification gap, and the recovery gap. We present HELM, a model-agnostic framework that addresses these deficiencies with three components: an Episodic Memory Module (EMM) that retrieves key task history via CLIP-indexed keyframes, a learned State Verifier (SV) that predicts action failure before execution from observation, action, subgoal, and memory-conditioned context, and a Harness Controller (HC) that performs rollback and replanning. The SV is the core learning contribution: it consistently outperforms rule-based feasibility checks and ensemble uncertainty baselines, and its effectiveness depends critically on access to episodic memory. On LIBERO-LONG, HELM improves task success rate by 23.1 percentage points over OpenVLA (58.4% to 81.5%), while extending the context window to H=32 yields only a 5.4-point gain and same-budget LoRA adaptation remains 12.2 points below HELM. HELM also improves long-horizon performance on CALVIN and substantially boosts recovery success under controlled perturbations. Ablations and mechanism analyses isolate the contribution of each component, and we release LIBERO-Recovery as a perturbation-injection protocol for evaluating failure recovery in long-horizon manipulation.

