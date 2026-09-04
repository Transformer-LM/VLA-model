# Multi-critic Learning for Whole-body End-effector Twist Tracking

paper_id: semanticscholar:8932dccd02104715dcfcd622a1659eeb3cc5caa0
tier: T2
source_used: failed
warning: fetch failed across all paths; intro filled with abstract; method empty

## Intro

Learning whole-body control for locomotion and arm motions in a single policy has challenges, as the two tasks have conflicting goals. For instance, efficient locomotion typically favors a horizontal base orientation, while end-effector tracking may benefit from base tilting to extend reachability. Additionally, current Reinforcement Learning (RL) approaches using a pose-based task specification lack the ability to directly control the end-effector velocity, making smoothly executing trajectories very challenging. To address these limitations, we propose an RL-based framework that allows for dynamic, velocity-aware whole-body end-effector control. Our method introduces a multi-critic actor architecture that decouples the reward signals for locomotion and manipulation, simplifying reward tuning and allowing the policy to resolve task conflicts more effectively. Furthermore, we design a twist-based end-effector task formulation that can track both discrete poses and motion trajectories. We validate our approach through a set of simulation and hardware experiments using a quadruped robot equipped with a robotic arm. The resulting controller can simultaneously walk and move its end-effector and shows emergent whole-body behaviors, where the base assists the arm in extending the workspace, despite a lack of explicit formulations. Videos and supplementary material can be found at multi-critic-locomanipulation.github.io.

## Method


