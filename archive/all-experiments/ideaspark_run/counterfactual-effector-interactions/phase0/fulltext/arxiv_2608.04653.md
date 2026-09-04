# Overcoming Statistical Bias in Action-Controllable World Models

paper_id: arxiv:2608.04653
tier: A
source_used: failed
warning: fetch failed across all paths; intro filled with abstract; method empty

## Intro

Action-conditioned world models aim to predict how visual environments evolve under an agent's actions. Yet future frames are often highly predictable from visual inertia and recurring motion patterns alone. This creates a shortcut: models can fit the data by exploiting statistical biases without making their visible dynamics meaningfully depend on the action. As a result, different actions may produce similar futures, while motion may persist even under zero action. The key question is how to reduce reliance on statistical shortcuts from dominating action-conditioned prediction. We argue that action control requires more than injecting action features; it requires enforcing consistency under counterfactual changes to actions and observations. Based on this insight, we introduce CoCo, a Counterfactual Consistency framework to enhance action controllability through two complementary constraints. Multi-step counterfactual consistency constrains reference, inverse-action, and zero-action rollouts, while action-spatial counterfactual consistency enforces consistent predictions under mirrored scenes and transformed actions. Together, they reduce reliance on statistical shortcuts from substituting for action-dependent dynamics. We further introduce Action Response Consistency (ARC) and Drift Energy (DE) to assess action controllability, together with Mini-SSMB for same-state, multi-action counterfactual evaluation. On Mini-SSMB, our full model achieved ARC_inv of 0.412 and ARC_ref of 0.483, while reducing DE by 17.07% relative to the baseline. On VP2 visual planning, it achieves the highest average success rate among SOTA models, at 73.1%. Experiments on BAIR and RoboNet further show that these gains preserve video prediction quality and transfer across model settings.

## Method


