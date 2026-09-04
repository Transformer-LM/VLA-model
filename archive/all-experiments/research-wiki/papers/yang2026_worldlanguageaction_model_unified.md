---
type: paper
node_id: paper:yang2026_worldlanguageaction_model_unified
title: "World-Language-Action Model for Unified World Modeling, Language Reasoning, and Action Synthesis"
authors: ["Yi Yang", "Zhihong Liu", "Siqi Kou", "Yiyang Chen", "Yanzhe Hu", "Jianbo Zhou", "Boyuan Zhao", "Zhijie Wei", "Xiao Xia", "Xueqi Li", "Pengfei Liu", "Zhijie Deng"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2606.05979"
  doi: null
  s2: null
tags: ["vla-wam", "h1", "h14", "joint-model"]
added: 2026-08-06T13:10:48Z
---

# World-Language-Action Model for Unified World Modeling, Language Reasoning, and Action Synthesis

## One-line thesis
在统一 World–Language–Action 系统中联合建模语义物理未来、语言推理与动作合成。

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

> We propose world-language-action (WLA) models as a new class of embodied foundation models. WLA takes textual instructions, images, and robot states as inputs to jointly predict textual subtasks, subgoal images, and robot actions, conjoining the \emph{world modeling interface} to learn from extensive egocentric videos as in the world-action model (WAM) and the \emph{language reasoning} capacities to solve complex long-horizon tasks as in vision-language-action (VLA) models. At the core of WLA lies an \emph{autoregressive (AR)} Transformer backbone, instead of a bidirectional diffusion Transformer as in WAMs, to predict the \emph{next state}, comprising the \emph{semantic-level} textual intention and complementary \emph{fine-grained} physical dynamics. The physical dynamics are supervised by the world modeling objective based on a dedicated World Expert, and are leveraged to ease the characterization of the state-action correlation for the Action Expert. WLA leverages meta-queries to make the world prediction \emph{implicitly} impact the action generation so that the former can be disabled during inference. The world prediction can also be activated to enable test-time scaling for improved robot control. Our WLA-0 prototype, with 2B active parameters, achieves 40 ms per inference on an NVIDIA RTX 5090. Evaluations across simulated and real-world environments demonstrate that WLA-0 achieves state-of-the-art multi-task and long-horizon learning abilities, e.g., 92.94\% success rate on RoboTwin2.0 Clean and 56.5\% success rate on RMBench. WLA-0 also holds the promise to learn novel tasks directly from \emph{cross-embodiment robot videos} without action annotations.

