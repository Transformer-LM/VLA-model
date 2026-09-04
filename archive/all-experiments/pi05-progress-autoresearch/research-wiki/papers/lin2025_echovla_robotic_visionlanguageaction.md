---
type: paper
node_id: paper:lin2025_echovla_robotic_visionlanguageaction
title: "EchoVLA: Robotic Vision-Language-Action Model with Synergistic Declarative Memory for Mobile Manipulation"
authors: ["Min Lin", "Xiwen Liang", "Bingqian Lin", "Jingzhi Liu", "Zijian Jiao", "Kehan Li", "Ziang Yan", "Yu Sun", "Weijia Liufu", "Yuhan Ma", "Jiarui Hu", "Yuecheng Liu", "Shen Zhao", "Yuzheng Zhuang", "Xiaodan Liang"]
year: 2025
venue: "arXiv"
external_ids:
  arxiv: "2511.18112"
  doi: null
  s2: null
tags: []
added: 2026-08-24T06:39:56Z
---

# EchoVLA: Robotic Vision-Language-Action Model with Synergistic Declarative Memory for Mobile Manipulation

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

> Recent progress in Vision-Language-Action (VLA) models has enabled embodied agents to interpret multimodal instructions and perform complex tasks. However, existing VLAs are mostly confined to short-horizon, table-top manipulation, lacking the memory and reasoning capability required for mobile manipulation, where agents must coordinate navigation and manipulation under changing spatial contexts. In this work, we present EchoVLA, a memory-aware VLA model for mobile manipulation. EchoVLA incorporates a synergistic declarative memory inspired by the human brain, consisting of a scene memory that maintains a collection of spatial-semantic maps and an episodic memory that stores task-level experiences with multimodal contextual features. The two memories are individually stored, updated, and retrieved based on current observations, task history, and instructions, and their retrieved representations are fused via coarse- and fine-grained attention to guide base-arm diffusion policies. To support large-scale training, we further introduce MoMani, an automated benchmark that generates expert-level trajectories through multimodal large language model (MLLM)-guided planning and feedback-driven refinement, supplemented with real-robot demonstrations. Comprehensive simulated and real-world results demonstrate that EchoVLA substantially improves overall performance, e.g., it achieves the highest success rates of 0.52 on manipulation/navigation tasks and 0.31 on mobile manipulation tasks in simulation, exceeding the strong baseline $π_{0.5}$ by +0.20 and +0.11, respectively.

