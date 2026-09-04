---
type: paper
node_id: paper:liu2026_checkvla_executiontime_verification
title: "CheckVLA: Execution-Time Verification with Action-Conditioned World Model for Long-Horizon Mobile Manipulation"
authors: ["Yushan Liu", "Peibo Sun", "Xintao Chao", "Zhenyang Yang", "Yifan Xie", "Lingfeng Zhang", "Shoujie Li", "Chenyu Tang", "Fang Chen", "Xiao-Ping Zhang", "Wenbo Ding"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2607.26789"
  doi: null
  s2: null
tags: ["vla-wam", "h10", "safety", "runtime-verification"]
added: 2026-08-06T13:10:42Z
---

# CheckVLA: Execution-Time Verification with Action-Conditioned World Model for Long-Horizon Mobile Manipulation

## One-line thesis
动作条件世界模型核验已提交 action chunk 的预期观测演化，并在失配时触发校准式改写。

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

> Vision-language-action (VLA) policies commonly execute long-horizon mobile manipulation through open-loop action chunks, issuing multiple actions without receiving new high-level visual input. A committed chunk therefore implies how observations should evolve, but accidental deviations can violate this expectation while the remaining actions continue to propagate the error: commit-time policy confidence cannot react to a deviation that occurs after dispatch, and observation-only anomaly scores lack an action-conditioned reference for separating expected effects from unexplained changes. We propose CheckVLA, which verifies execution with a separately trained, frozen action-conditioned world model. A conformally calibrated risk threshold bounds the episode-level probability of an unnecessary first intervention and determines when to intervene, its exceedance controls how strongly the rewritten suffix retains the superseded chunk, latency-aware hard prefixing restricts replacement to actions that remain deployable, and an event-driven keyframe bank preserves evidence of prior progress across repairs. On RoboCasa365, under a common training recipe and a matched invocation budget, CheckVLA attains a 36.1% average success rate against 27.6% for periodic replanning (+8.5 points). At a matched 5% episode-level false-alarm target, action conditioning raises timely recall to 77.9%, against 48.6% for an observation-only control and 37.9% for an action-shuffled control. These simulation results support action-conditioned verification as a way to restore feedback during chunked execution while keeping the repair consistent with inference latency.

