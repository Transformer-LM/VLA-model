# WNM-3D: A World Navigation Model with 3D Scene Conditioning for Closed-Loop VLN

paper_id: semanticscholar:74257100ad8c273b90dbaaba190e1f699ec9df0a
tier: T2
source_used: failed
warning: fetch failed across all paths; intro filled with abstract; method empty

## Intro

Recent vision-language navigation (VLN) systems increasingly adapt pretrained vision-language models (VLMs) into vision-language-action (VLA) policies that map egocentric observations and language instructions directly to navigation actions. Although semantically capable, such action-centric training does not explicitly model how the agent's visual observations should evolve under its predicted motion. Generative world-action models (WAMs) jointly predict future observations and actions, yet existing WAMs for continuous VLN do not condition joint future-view and action generation on geometry-aware representations inferred from the observed history. We present WNM-3D, a generative World Navigation Model with 3D scene conditioning for continuous VLN. To consolidate past observations into persistent scene context, a frozen feed-forward geometry encoder extracts geometry-aware representations from the monocular egocentric RGB history, and a trainable 3D Scene-to-Token Adapter converts them into a fixed-length prefix in the token space of the world-action Diffusion Transformer. Through block-causal attention, this prefix conditions every future video-action block, providing a shared geometric context for both future-view and action generation. We train WNM-3D through supervised world-action fine-tuning on A*-generated demonstrations, DAgger-style adaptation on policy-visited states, and Counterfactual DanceGRPO refinement for closed-loop execution. Experiments on GN-Bench show that WNM-3D outperforms strong VLM-based navigation policies and its 2D-conditioned counterpart in closed-loop navigation. Stage-wise ablations further show that DAgger-SFT provides the larger success-rate gain, while Counterfactual DanceGRPO subsequently improves both navigation success and path efficiency.

## Method


