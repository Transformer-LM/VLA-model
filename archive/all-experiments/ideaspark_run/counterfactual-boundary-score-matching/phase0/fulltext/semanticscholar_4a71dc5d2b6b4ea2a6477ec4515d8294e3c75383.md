# Geometry Guided Self-Consistency for Physical AI

paper_id: semanticscholar:4a71dc5d2b6b4ea2a6477ec4515d8294e3c75383
tier: T2
source_used: failed
warning: fetch failed across all paths; intro filled with abstract; method empty

## Intro

State-of-the-art physical AI models generate a chunk of actions per inference through diffusion or flow matching, iteratively refining an initial noise sample into an action trajectory. Because this inference process is inherently stochastic, committing to a single trajectory per round is brittle, and this brittleness compounds across the many sequential rounds that comprise a complete episode. We introduce KeyStone, an inference-time self-consistency method for diffusion-based action generation that draws $K$ candidate action chunks in parallel from a shared model context, clusters them in continuous action space, and returns the medoid of the largest cluster -- no additional model required. Two properties make this practical. First, the compact nature of action trajectories makes diffusion inference memory-bandwidth bound, leaving spare compute capacity to run $K$ chains in parallel with no additional wall-clock latency. Second, unlike token or pixel spaces where distance carries no semantic meaning and selection requires a learned judge, action chunks are geometrically structured such that Euclidean distance directly reflects physical similarity, making selection principled and judge-free. Across diverse vision-language-action models (VLAs) and world-action models (WAMs), KeyStone improves task success rates by up to \textbf{13.3\%} over single-trajectory sampling with negligible latency overhead, while having on par accuracy with model-based selectors at no training cost. We open source KeyStone at https://github.com/dywsjtu/keystone.

## Method


