# Research Brief

**Status:** ready-for-discovery (field-mapping stage)  
**Scope:** research only; paper writing is disabled

## Parent field

Map the broad intersection of embodied Vision-Language-Action models and learned
world models / World Action Models. The first objective is to discover and
compare macro research directions, not to validate a predetermined hypothesis.

## Immediate research questions

1. Where can world models change the VLA lifecycle: representation learning,
   pretraining, data generation, prediction, planning, policy improvement,
   evaluation, reward/critique, safety, or online adaptation?
2. Which combinations of representation, control role, coupling, learning
   regime, embodiment, and task define genuinely distinct research directions?
3. Which five to eight macro directions have the strongest combination of
   scientific importance, unresolved evidence, novelty opportunity, and
   practical testability?
4. What evidence would discriminate among those directions before committing to
   a concrete idea?

## Discovery axes

- World representation: pixels/video, perceptual latents, task-centric latents,
  state-space or structured/3D/multimodal representations.
- Functional role: predictor, planner, critic, reward/evaluator, synthetic-data
  generator, policy trainer, safety model, or representation pretrainer.
- Coupling: frozen auxiliary model, VLA post-training, planning-time use,
  online adaptation, or policy/world-model co-evolution.
- Learning regime: offline data, simulation, online interaction, model-based RL,
  self-supervision, or hybrid regimes.
- Embodiment and task: manipulation, navigation, mobile manipulation, humanoids,
  or other embodied settings justified by evidence.
- Evidence: model-, policy-, and environment-level endpoints, generalization,
  uncertainty, failure modes, and matched-resource comparisons.

## Required first deliverable

Write `research-stage/DIRECTION_LANDSCAPE.md` with a field taxonomy and five to
eight macro directions. For every direction include:

- core problem and why it matters now;
- representative method families and nearest-work density;
- unresolved gap and possible contribution shapes;
- decisive validation evidence, candidate tasks, and baseline families;
- data, compute, implementation burden, risks, and cheap falsification route;
- comparable scores for impact, novelty opportunity, evidence gap, feasibility,
  and time to first reliable result.

A ranked recommendation is welcome, but it is not a selection.

## Non-assumptions and seed topics

Do not preselect long-horizon manipulation, any robot embodiment, LIBERO,
RoboCasa, a particular VLA, or a particular world-model representation. Video-
generative WAMs, latent-dynamics world models, and model-based RL are seed topics
that must be investigated alongside other evidence-supported routes; they are
not mandatory final directions.

## Direction checkpoint

After the landscape and literature map are complete, stop and ask the user to
select or revise a macro direction. Do not begin concrete idea selection,
hypothesis refinement, benchmark commitment, implementation, or experiments
until `research.selected_macro_direction` records that decision.

## Later evidence contract

After a direction is selected, define its falsifiable claim and distinguish
model-, policy-, and environment-level evidence. Prediction quality alone cannot
establish a control benefit. Positive claims require traceable raw evidence,
matched-resource baselines, uncertainty, negative controls, and explicit failure
conditions appropriate to the selected direction.

## Constraints

- Simulation or existing offline data first; real-robot work requires explicit
  approval for an exact protocol.
- Compute backend may remain unconfigured through field mapping, idea discovery,
  and experiment design; execution must block at preflight.
- Paid compute, private-data upload, dataset-license acceptance, and real-robot
  execution require explicit authority.
- Paper writing remains disabled.
