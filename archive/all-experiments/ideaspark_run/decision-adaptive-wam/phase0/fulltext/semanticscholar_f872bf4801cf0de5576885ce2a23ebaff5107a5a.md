# τ0-WM: A Unified Video-Action World Model for Robotic Manipulation

paper_id: semanticscholar:f872bf4801cf0de5576885ce2a23ebaff5107a5a
tier: T2
source_used: failed
warning: fetch failed across all paths; intro filled with abstract; method empty

## Intro

Robotic manipulation requires models that generate executable actions while anticipating and evaluating their future consequences before physical execution. We present $\tau_0$-World Model ($\tau_0$-WM), a unified video-action world model that integrates policy learning, video prediction, and action evaluation within a single future-predictive framework. Built on a shared video diffusion backbone, $\tau_0$-WM provides two complementary interfaces. First, a video action model jointly predicts future visual latents and continuous action chunks from multi-view observations, language instructions, and robot state. Second, an action-conditioned video simulator rolls out candidate action chunks into multi-view futures and predicts dense task-progress scores. The model is trained on approximately $27{,}300$ hours of real-robot teleoperation, UMI-style interaction, egocentric human videos, and rollout or failure trajectories using modality-specific supervision masks. At inference time, $\tau_0$-WM uses test-time computation to sample action candidates, rank them with re-denoising consistency, and invoke simulator-based rectification for low-quality candidates. On challenging long-horizon and fine-grained robotic manipulation tasks, $\tau_0$-WM shows superior performance over other relevant baselines.

## Method


