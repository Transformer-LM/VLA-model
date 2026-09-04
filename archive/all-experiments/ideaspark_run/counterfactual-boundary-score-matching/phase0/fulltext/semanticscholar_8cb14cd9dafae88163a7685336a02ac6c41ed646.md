# Learning Action Manifold with Multi-view Latent Priors for Robotic Manipulation

paper_id: semanticscholar:8cb14cd9dafae88163a7685336a02ac6c41ed646
tier: T2
source_used: failed
warning: fetch failed across all paths; intro filled with abstract; method empty

## Intro

This paper tackles spatial perception and manipulation challenges in Vision-Language-Action (VLA) models. To address depth ambiguity from monocular input, we leverage a pre-trained multi-view diffusion model to synthesize latent novel views and propose a Geometry-Guided Gated Transformer (G3T) that aligns multi-view features under 3D geometric guidance while adaptively filtering occlusion noise. To improve action learning efficiency, we introduce Action Manifold Learning (AML), which directly predicts actions on the valid action manifold, bypassing inefficient regression of unstructured targets like noise or velocity. Experiments on LIBERO, RoboTwin 2.0, and real-robot tasks show our method achieves superior success rate and robustness over SOTA baselines. Project page: https://junjxiao.github.io/Multi-view-VLA.github.io/.

## Method


