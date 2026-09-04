# Digital Twin-Assisted Causal Multi-Agent Reinforcement Learning for Large-Scale Network Service Migration

paper_id: semanticscholar:787ead55968d4fd7503bb7d27c7c2e526c3e6dae
tier: T2
source_used: failed
warning: fetch failed across all paths; intro filled with abstract; method empty

## Intro

Dynamic service migration is essential for guaranteeing quality of service (QoS) for mobile users in multi-access edge computing (MEC). However, conventional reinforcement learning and other strategies frequently result in suboptimal policies. These methods are unable to differentiate between actual cause-and-effect relationships and fake patterns due to their reliance on correlational data, resulting in inefficient and expensive migrations. This paper introduces a novel digital twinassisted causal multi-agent reinforcement learning (DT-CausalMARL) framework to address this fundamental limitation. We change the optimization objective from minimizing direct system cost to maximizing the causal gain of migration actions. This is accomplished by employing a digital twin as a counterfactual analysis engine to assess the actual consequences of decisions in comparison to a baseline policy. This causal gain is subsequently employed as a robust reward signal by a causal multi-agent deep deterministic policy gradient (Causal-MADDPG) algorithm to train cooperative agents. Our framework outperforms standard MARL baselines by reducing harmful ‘regretful migrations' and improving system stability under dynamic traffic loads.

## Method


