# PATCH: Action-Chunk-Conditioned Latent Patch Innovation Monitoring for Robot Manipulation

paper_id: semanticscholar:60ad2f6f6ce05b12d3c356715f4a79385b2bedff
tier: T2
source_used: failed
warning: fetch failed across all paths; intro filled with abstract; method empty

## Intro

Learning-based manipulation policies have made substantial progress in real-world robot manipulation, particularly for short-horizon action generation. However, deployment in open workspaces remains fragile under unexpected local scene dynamics, such as moving objects, transient occlusions, or disturbances near the intended motion. Existing runtime monitors often rely on global observation anomalies, policy uncertainty, or frame-level visual changes, and struggle to distinguish task-relevant execution risk from benign visual variation. We introduce PATCH, an action-chunk-conditioned latent patch innovation monitor for deployment-time intervention. Given the active action chunk, PATCH defines a projected execution corridor, predicts latent patch evolution inside it, and accumulates persistent residuals unexplained by the robot's own motion. These residuals form a localized intervention signal that allows PATCH-Router to pause execution, select an available recovery source, and resume the original policy once localized innovation subsides. Experiments on real robot rollout data show that PATCH produces more stable and context-relevant triggers than competing runtime monitors. Real-robot deployment further demonstrates monitor-driven intervention and policy resumption for disturbance-aware manipulation. Project Page: https://yananzhou5555.github.io/PATCH/.

## Method


