# Pointing-VLA: Typed Spatial Grounding Interfaces for Vision-Language-Action Manipulation

paper_id: semanticscholar:aaef4e8a3bd4a3a4f6673b2d4bce0a3237783cb9
tier: T2
source_used: failed
warning: fetch failed across all paths; intro filled with abstract; method empty

## Intro

Vision-language-action (VLA) models often expose spatial grounding through autoregressive text coordinates or opaque action tokens, creating brittle interfaces between multimodal reasoning and robot execution. We present Pointing-VLA, a typed hidden-state spatial readout built on Embodied-R1. Geometry-specific heads predict normalized points, object-functional grounding (OFG) heatmaps, and visual trajectories without serializing geometry as text. For the evaluated Bridge/WidowX and physical pick-place deployments, an explicit execution contract assigns PICK to source-conditioned OFG and PLACE to Pointing, providing direct stage-aligned spatial targets. Pointing-VLA achieves SOTA performance on Bridge/WidowX, averaging 72.9\% across the evaluated four-task set without Bridge-specific finetuning under collision-enabled CuRobo execution. Pointing and OFG show complementary strengths across native and cross-dataset evaluations. The OFG/contact readout transfers to NORA-1.5, preserving or improving success while reducing recorded controller time by more than 20$\times$; typed heads are also 6.68--6.90$\times$ faster than Embodied-R1 text decoding on a shared external suite. When integrated as spatial guidance for a $\pi_{0.5}$ action policy, Pointing-VLA raises autonomous real-robot success from 52.7\% to 80.7\% across three visual contexts. These results establish typed spatial readouts as an efficient, inspectable interface between embodied reasoning and robot execution.

## Method


