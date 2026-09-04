# Do Robotic World Models Really Follow Actions? Diagnosing and Aligning Action-Conditioned Generation for Policy Learning

paper_id: arxiv:2608.24885
tier: H
source_used: failed
warning: fetch failed across all paths; intro filled with abstract; method empty

## Intro

Action-conditioned world models are increasingly used as learned simulators for policy evaluation and improvement, yet their effectiveness rests on an unverified assumption: generated futures faithfully reflect arbitrary valid actions. Existing benchmarks are typically confined to expert demonstrations, leaving off-expert action following inadequately evaluated. To address this gap, we introduce WorldEcho, which probes action following over a broader action distribution using visual integrity and SE(3) trajectory alignment. Our diagnosis shows that current world models reasonably execute expert actions but struggle with diverse off-expert trajectories, either ignoring the commanded actions or producing visually invalid rollouts. We further propose WorldSync, which strengthens action following along three complementary axes: distributional coverage, representational grounding, and intervention-effect alignment. It broadens the training distribution over action consequences, grounds intermediate video representations in action-induced robot dynamics through an Action-Forcing Expert, and aligns predicted changes under action interventions with the corresponding changes in ground-truth futures. Experiments on RoboTwin benchmarks and real-robot tasks show that WorldSync improves WorldEcho metrics and serves as a more reliable simulator for iterative policy improvement, enabling policies to achieve higher success rates.

## Method


