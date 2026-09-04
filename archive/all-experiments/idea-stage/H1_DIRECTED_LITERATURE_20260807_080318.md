# H1 Directed Literature Map — Predictive World Objectives for VLA Representations

**Run:** `20260806-vla-wam-expanded-field-map`  
**Cutoff:** 2026-08-07 (Asia/Shanghai)  
**Stage:** idea-discovery; no concrete Idea selected  
**Scope:** training-time predictive objectives that may shape a VLA/policy representation; no test-time planning, rollout ranking, synthetic-data generation, or paper writing

## 1. Question being audited

After matching robot data, initialization, trainable parameters, optimizer steps, target tokens, and approximate training FLOPs, does predicting a future world target causally improve closed-loop action quality, rather than merely adding capacity, regularization, video pretraining, or task-progress leakage?

The literature was read on both sides of the intersection:

- **VLA/policy side:** action-only VLA baselines, visuomotor representation pretraining, action heads, and closed-loop manipulation evaluation.
- **WAM/world side:** decoded-video, motion, structured, and latent future targets; action conditioning; coupling and removal of the world branch at inference.

## 2. Primary evidence map

| Work | H1 mechanism | What it establishes | What remains confounded or occupied |
|---|---|---|---|
| [GR-1](https://arxiv.org/abs/2312.13139) | joint future-image and action prediction | large-scale video-generative pretraining can feed robot action learning | extra video, model scale, and joint architecture are not isolated from the predictive objective |
| [GR-2](https://arxiv.org/abs/2410.06158) | web-scale video-language-action generation | extends the scale argument for joint world/action learning | 38M-video scale makes a small-budget causal comparison impossible |
| [DynaMo](https://arxiv.org/abs/2409.12192) | in-domain latent forward/inverse dynamics pretraining | future latent dynamics can improve downstream visuomotor policies without Internet data | not a modern language-conditioned VLA; representation pretraining and policy training are staged |
| [Video Prediction Policy](https://arxiv.org/abs/2412.14803) | representations inside a video diffusion model | predictive visual features support generalist policy learning; reported 18.6% relative CALVIN gain | Internet/human video and VDM pretraining remain scale/data confounds |
| [Unified Video Action Model](https://arxiv.org/abs/2503.00200) | joint video-action latent with decoupled heads | the video decoder can be bypassed for fast action inference | unified architecture and multi-purpose masked training are changed together |
| [WorldVLA](https://arxiv.org/abs/2506.21539) | autoregressive image/action tokens | demonstrates a unified action-world formulation | jointness, autoregressive parameterization, and future supervision are not independently identified |
| [DUST](https://arxiv.org/abs/2510.27607) | dual visual/action streams with joint diffusion/flow learning | future-video co-training can coexist with an action path | architecture, pretraining data, and objective all change |
| [Motion Image Diffusion](https://arxiv.org/abs/2512.18007) | removable optical-flow/motion-image head | motion supervision slightly exceeds action-only on LIBERO | future RGB is *worse* than action-only: pi0 93.6 vs 94.2 and pi0.5 95.7 vs 96.9; motion gives only 94.7 and 97.5, so future supervision is not intrinsically beneficial |
| [VLA-JEPA](https://arxiv.org/abs/2602.10098) | leakage-free future-latent prediction | explicitly targets nuisance-robust predictive representations | occupies the simple “predict frozen future latent” pretraining route |
| [Fast-WAM](https://arxiv.org/abs/2603.16666) | future video as co-training only; action-only deployment | directly occupies “train with futures, remove future generation at inference” | matched token/FLOP controls remain central to attribution |
| [AGRA](https://arxiv.org/abs/2606.12217) | action-grounded representation alignment and causal intervention | occupies generic action-grounded alignment language | a new proposal cannot claim novelty from action grounding alone |
| [SelfWAM](https://arxiv.org/abs/2608.00725) | clean-action-conditioned future RGB plus future robot self-mask | tests directional action perturbations and an action-specific consequence path | action conditioning alone falls from FastWAM 91.84 to 90.80 average; self-mask raises it to 92.62. Generic action conditioning, action perturbation, and “avoid task-progress shortcut” are now occupied |
| [LiLa-WAM](https://arxiv.org/abs/2608.03701) | compact DINOv3 future-feature foresight objective | future latent auxiliary can be trained end-to-end on one 24GB GPU; its 10-task ablation reports 54.4 without foresight vs 70.0 with it | still requires about 110 GPUh; compact latent-head novelty is occupied, and VTT/task-conditioning changes are coupled |
| [DreamWAM](https://arxiv.org/abs/2608.04996) | appearance, motion, geometry, and semantic future targets with target-specific routing | target content and injection route both matter; all-denoise can underperform RGB-only while hybrid routing reaches 98.90 | “choose a better structured target” and generic route compatibility are now crowded |

## 3. Evidence synthesis

### 3.1 What is already established

There is now a dense H1 cluster showing that world prediction can be used only during training while the deployed policy retains an action-only path. Pixel/video, motion, and frozen-feature targets have all been demonstrated. Therefore the following are not viable novelty claims:

- add a future-image or future-latent head to a VLA;
- discard the future head at inference;
- condition future prediction on the demonstrated action;
- use an action perturbation probe;
- replace RGB with one more structured target without a new identification argument;
- claim lightweight novelty merely because the latent head fits one GPU.

### 3.2 Strong negative and contradictory evidence

The most important finding is that predictive supervision is not monotonically helpful:

1. Motion Image Diffusion reports future-RGB variants below their action-only counterparts on two policy bases.
2. SelfWAM reports that action-conditioned future RGB alone is below its FastWAM baseline; the self-mask target is needed to recover and exceed it.
3. DreamWAM reports that using all structured targets through the same denoising route is below RGB-only, while a target-specific hybrid route is better.
4. The personal server's existing CF-DynAlign world predictor passes its standard held-out comparison but fails the strict temporal gate: MSE 0.4415 versus persistence 0.2639. It is not a validated world model and must not train a policy.

These observations reject the assumption `lower/additional world loss => better action representation`.

### 3.3 Open claim spaces that survive the directed search

These are gaps, not selected Ideas:

- **Matched causal identification:** same head shape, target dimension, tokens, update count, trainable parameters, and approximate FLOPs for future, static/current, temporally reversed, shuffled-action, and dummy auxiliary controls.
- **Mechanism intervention:** establish whether action-useful predictive information actually enters a shared policy representation and carries any closed-loop gain, rather than only being probe-decodable.
- **Admissibility/reliability:** determine when a predictive objective is safe to backpropagate into the policy, given predictor validity and action-loss transfer, rather than assuming every future target should shape the policy.
- **Negative-transfer boundary:** explain target/route combinations that damage action learning under a fixed budget.

The first two have the cleanest identification story. The third has the strongest motivation from the contradictory evidence but risks looking like generic auxiliary-task optimization unless its gate is defined using world-model validity and falsified with world-specific controls.

## 4. Local and remote feasibility evidence

### 4.1 Available personal assets

- StarVLA is the least invasive policy host because its action tensor and trainer loss are already exposed.
- A completed action-only StarVLA checkpoint and standard LIBERO evaluation path exist under `<PERSONAL_RESEARCH_ROOT>`.
- Personal LIBERO datasets and a frozen DINOv2 checkpoint are available offline.
- OpenPI is available, but its loss/data interfaces require more invasive modification for future observations.

### 4.2 Hard implementation boundary

The existing StarVLA tree contains uncommitted CF-DynAlign work and must remain untouched. CF-DynAlign nearly duplicates the route “frozen E/F/G predicts the consequence of predicted actions and aligns it to instruction effect,” and its strict F gate fails. Consequently:

- never enable its `lambda_cf`;
- never represent its strict-failed predictor as validated;
- never train from the dirty tree;
- if an Idea passes review, clone the verified personal bundle into a new isolated path under `<PERSONAL_RESEARCH_ROOT>/workspace/`;
- use the same initialization and fixed data split for every treatment/control branch.

### 4.3 Budget consequence

The 8 GPUh ceiling cannot reproduce foundation-scale WAM training. A defensible experiment must use cached/frozen targets and short, matched PEFT branches. The 2 GPUh pilot gate should first kill candidates that fail either their model-validity diagnostic or paired action endpoint. Only the smallest surviving comparison may use the remainder for seeds and rollouts.

## 5. Directed-search decision

**Decision: continue to candidate generation and independent jury; do not start training yet.**

The broad H1 premise survives, but the naïve implementation is crowded and contradicted. Candidate review must prioritize falsifiable identification of when/why a predictive objective carries action performance, and must reject anything that merely adds another future head, target, action condition, or generic gradient surgery.

## 6. Search limitations

- Broad search covered arXiv, OpenAlex, Crossref, Semantic Scholar, OpenReview, and DBLP; Semantic Scholar rate limiting and zero-yield sources were recorded rather than silently ignored.
- Load-bearing claims above were checked against primary arXiv pages/full text. The three newest papers are preprints and their results are provisional.
- No local PDF corpus was available in `papers/` or `literature/`; this map therefore uses the directed online primary-source search plus the existing 69-paper field map.

