# LLM-Guided Future Hypotheses for Horizon-Aware Exploration in Multi-Step Robot Manipulation

paper_id: semanticscholar:8a1edd9ea3b3204ecf0aaca675d85c0c06130ba7
tier: T2
source_used: failed
warning: fetch failed across all paths; intro filled with abstract; method empty

## Intro

Multi-step robot manipulation requires acting under uncertainty about how the scene will evolve, making exploration and policy adaptation challenging. We study whether short-horizon, task-consistent future videos can provide useful structured priors for control and reinforcement-learning fine-tuning. We formalize this idea through Future-Experience Conditioning (FEC), a simple interface that conditions closed-loop policies on a latent representation of a short future video. In our simulation setup, future clips are generated in three stages, an LLM reasoner operating over a task ontology initialized from the current scene state, a robot-free digital-twin rollout of the intended object motion, and a mask-free video diffusion model that synthesizes a robot-consistent future clip without requiring segmentation at inference. We instantiate this future-conditioning interface primarily with BC and BC+RL, and compare against a future-conditioned Streaming Flow Policy (SFP) baseline on RoboCasa and CALVIN under NoFuture, GTFuture, GenFuture, and WrongFuture. Generated futures improve performance over no-future conditioning, while mismatched futures degrade it, and our BC+RL instantiation achieves the strongest overall results. An average BC+RL learning-curve analysis across 8 CALVIN tasks further shows that GTFuture improves fastest, GenFuture improves earlier and to a higher level than NoFuture, and WrongFuture remains at zero throughout training. These results suggest that short-horizon future videos can serve as useful structured priors for exploration and policy adaptation under imperfect future predictions. https://enact2026.github.io/

## Method


