---
type: paper
node_id: paper:du2023_learning_universal_policies
title: "Learning Universal Policies via Text-Guided Video Generation"
authors: ["Yilun Du", "Mengjiao Yang", "Bo Dai", "Hanjun Dai", "Ofir Nachum", "Joshua B. Tenenbaum", "Dale Schuurmans", "Pieter Abbeel"]
year: 2023
venue: "arXiv"
external_ids:
  arxiv: "2302.00111"
  doi: null
  s2: null
tags: ["video-generative-wam", "trajectory-proposal", "inverse-dynamics"]
added: 2026-08-06T07:52:47Z
---

# Learning Universal Policies via Text-Guided Video Generation

## One-line thesis
将文本条件视频计划经逆动力学转为跨任务控制。

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

> A goal of artificial intelligence is to construct an agent that can solve a wide variety of tasks. Recent progress in text-guided image synthesis has yielded models with an impressive ability to generate complex novel images, exhibiting combinatorial generalization across domains. Motivated by this success, we investigate whether such tools can be used to construct more general-purpose agents. Specifically, we cast the sequential decision making problem as a text-conditioned video generation problem, where, given a text-encoded specification of a desired goal, a planner synthesizes a set of future frames depicting its planned actions in the future, after which control actions are extracted from the generated video. By leveraging text as the underlying goal specification, we are able to naturally and combinatorially generalize to novel goals. The proposed policy-as-video formulation can further represent environments with different state and action spaces in a unified space of images, which, for example, enables learning and generalization across a variety of robot manipulation tasks. Finally, by leveraging pretrained language embeddings and widely available videos from the internet, the approach enables knowledge transfer through predicting highly realistic video plans for real robots.

