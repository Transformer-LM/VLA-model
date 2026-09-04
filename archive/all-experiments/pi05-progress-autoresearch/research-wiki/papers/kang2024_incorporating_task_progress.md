---
type: paper
node_id: paper:kang2024_incorporating_task_progress
title: "Incorporating Task Progress Knowledge for Subgoal Generation in Robotic Manipulation through Image Edits"
authors: ["Xuhui Kang", "Yen-Ling Kuo"]
year: 2024
venue: "arXiv"
external_ids:
  arxiv: "2410.11013"
  doi: null
  s2: null
tags: []
added: 2026-08-24T03:48:18Z
---

# Incorporating Task Progress Knowledge for Subgoal Generation in Robotic Manipulation through Image Edits

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

> Understanding the progress of a task allows humans to not only track what has been done but also to better plan for future goals. We demonstrate TaKSIE, a novel framework that incorporates task progress knowledge into visual subgoal generation for robotic manipulation tasks. We jointly train a recurrent network with a latent diffusion model to generate the next visual subgoal based on the robot's current observation and the input language command. At execution time, the robot leverages a visual progress representation to monitor the task progress and adaptively samples the next visual subgoal from the model to guide the manipulation policy. We train and validate our model in simulated and real-world robotic tasks, achieving state-of-the-art performance on the CALVIN manipulation benchmark. We find that the inclusion of task progress knowledge can improve the robustness of trained policy for different initial robot poses or various movement speeds during demonstrations. The project website can be found at https://live-robotics-uva.github.io/TaKSIE/ .

