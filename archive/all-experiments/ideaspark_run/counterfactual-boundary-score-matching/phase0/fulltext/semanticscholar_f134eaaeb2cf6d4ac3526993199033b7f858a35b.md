# STARRY: Spatial-Temporal Action-Centric World Modeling for Robotic Manipulation

paper_id: semanticscholar:f134eaaeb2cf6d4ac3526993199033b7f858a35b
tier: T2
source_used: failed
warning: fetch failed across all paths; intro filled with abstract; method empty

## Intro

Robotic manipulation requires reasoning about future spatial-temporal interactions and geometric constraints, yet existing Vision-Language-Action (VLA) policies often leave predictive representation weakly coupled with action execution, causing failures in tasks requiring precise spatial-temporal coordination. We propose STARRY, a world-model-enhanced action-generation policy that aligns spatial-temporal prediction and action generation by jointly denoising future spatial-temporal latents and actions through a unified diffusion process. To bridge 2D visual tokens and 3D metric control, STARRY introduces Geometry-Aware Selective Attention Modulation (GASAM), which converts predicted depth and end-effector geometry into token-aligned weights for selective action-attention modulation. On RoboTwin 2.0, STARRY achieves 93.82% / 93.30% average success under Clean and Randomized settings across 50 bimanual tasks. Real-world experiments show that STARRY improves average success from 42.5% to 70.8% compared with $\pi_{0.5}$. These results demonstrate the effectiveness of action-centric spatial-temporal world modeling for spatially and temporally demanding robotic manipulation.

## Method


