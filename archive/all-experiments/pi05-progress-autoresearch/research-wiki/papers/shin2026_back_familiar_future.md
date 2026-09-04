---
type: paper
node_id: paper:shin2026_back_familiar_future
title: "Back to the Familiar Future: Failure Recovery for VLA Policies via Pre-Imagined Milestone Selection"
authors: ["Suyeon Shin", "Juwon Kim", "Hyeonbin Park", "Hyunseo Kim", "Hyundo Lee", "Hyung-Sin Kim", "Byoung-Tak Zhang"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2606.09258"
  doi: null
  s2: null
tags: []
added: 2026-08-24T06:39:56Z
---

# Back to the Familiar Future: Failure Recovery for VLA Policies via Pre-Imagined Milestone Selection

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

> Vision-language-action (VLA) policies can deviate from nominal trajectories during manipulation, even when tasks remain physically feasible. Recovering from these deviations is challenging, as they push the policy into unfamiliar state spaces where direct re-planning frequently destabilizes action sequences. We propose Back to the Familiar Future (B2FF), a recovery framework for foresight-driven VLAs that leverages future visual conditioning as a recovery interface. Before execution, the VLA generates a milestone bank of familiar future states conditioned on the clean initial observation. At recovery time, a recoverability-aware selector selects a recovery milestone from this bank and enforces it as a fixed visual goal. This enables the VLA to robustly map off-trajectory observations back to a familiar future. On failure-injected LIBERO, under controlled recovery timing aligned with the injected failure, B2FF increases the average success rate of a baseline VLA from 56.3% to 74.0%, demonstrating that pre-imagined milestones can guide recovery without fine-tuning the low-level action generator.

