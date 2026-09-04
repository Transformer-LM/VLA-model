---
type: idea
node_id: idea:task-equivalent-recovery
title: "Task-Equivalent Recovery"
stage: proposed
outcome: pending
added: 2026-08-30T21:11:07Z
based_on: []
target_gaps: ["gap:G7", "gap:G9"]
tags: ["vla", "recovery", "bisimulation", "long-horizon"]
---

# Task-Equivalent Recovery

**stage:** `proposed`  ·  **outcome:** `pending`

Recover to the nearest state with the same supported predicates and feasible continuations instead of an exact checkpoint.

## Thesis
Semantic continuation equivalence can shorten recovery while preserving completed independent task predicates.

## Key risks
Equivalence learning may require a hidden task planner and overlaps goal-conditioned bisimulation plus rollback recovery.

## Connections
_Edges are recorded in `graph/edges.jsonl`; summarize here for human readers._

