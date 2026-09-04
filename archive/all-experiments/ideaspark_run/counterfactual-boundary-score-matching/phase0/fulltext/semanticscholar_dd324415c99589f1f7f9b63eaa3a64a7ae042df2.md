# Can Explicit Physical Feasibility Benefit VLA Learning? An Empirical Study

paper_id: semanticscholar:dd324415c99589f1f7f9b63eaa3a64a7ae042df2
tier: A
source_used: failed
warning: fetch failed across all paths; intro filled with abstract; method empty

## Intro

Vision-Language-Action (VLA) models map multimodal inputs directly to robot actions and are typically trained through large-scale imitation learning. While this paradigm has shown strong performance, prevailing VLA training procedures do not explicitly supervise hard physical constraints such as obstacle avoidance or kinematic feasibility. As a result, the geometric structure underlying physically feasible behavior must be inferred only implicitly from demonstrations. In this paper, we study whether introducing explicit feasibility supervision can provide effective structured guidance for VLA policies. We formulate a simple geometry-grounded feasibility objective and integrate it into the training stage of a diffusion-based VLA policy. To evaluate this idea systematically, we use obstacle-aware manipulation as a controlled probe of geometry-dependent physical feasibility. Empirical results show that augmenting VLA training with feasibility supervision improves both physical reliability and overall task performance, while also enhancing learning efficiency in the low-data regime. These findings indicate that explicit feasibility signals can effectively complement imitation-based VLA learning, highlighting their potential for developing more reliable VLA policies.

## Method


