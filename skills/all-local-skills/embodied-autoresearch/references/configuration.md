# Configuration Reference

## Contents

1. Files
2. Execution modes
3. Compute and authority
4. Acceptance settings
5. Safe edits

## Files

- `RESEARCH_BRIEF.md` is the human-readable scientific contract.
- `AUTORESEARCH_CONFIG.json` is the deterministic automation and safety config.
- `.aris/autoresearch/active_run.json` points to the active run state.

The JSON configuration is used so bootstrap and validation need only the Python
standard library.

## Execution modes

`automation.mode` supports:

- `plan`: complete literature, ideas, method, and experiment planning; block
  before code execution.
- `execute`: continue through implementation and experiments when resources and
  authority are configured.
- `dry-run`: validate routing and expected artifacts without external calls,
  code mutations outside bootstrap, or experiments.

Paper writing remains controlled separately by `project.paper_writing` and is
`false` for this skill.

## Exploration levels

`research.exploration_level` supports:

- `field`: map a parent field and compare five to eight macro directions before
  choosing one;
- `direction`: refine a selected macro direction into concrete research ideas;
- `idea`: start from an already specified idea and proceed to novelty and method
  validation.

For `field`, set `automation.require_direction_checkpoint=true`, keep
`automation.auto_select_idea=false`, and leave
`research.selected_macro_direction=null` until the user chooses from
`research-stage/DIRECTION_LANDSCAPE.md`. Seed topics are search prompts, not
scope restrictions. Open embodiment, task, action, and benchmark values must not
be filled by convenience before the checkpoint.

## Compute and authority

`compute.backend` supports:

- `local`: require a detected local NVIDIA GPU unless the selected experiment is
  explicitly CPU-only.
- `remote`: require `remote_host` and a successful read-only SSH preflight.
- `unconfigured`: permit discovery and planning, block experiments.

Budget fields are hard ceilings, not targets. Set `paid_compute_allowed=true`
only after the user authorizes an external provider and cost ceiling. A positive
GPU-hour ceiling does not itself authorize paid compute.

`max_real_robot_trials=0` and `safety.allow_real_robot=false` are independent
gates. Both must be changed with explicit authority before a real-robot plan can
run.

## Acceptance settings

- `minimum_main_seeds`: floor for a main quantitative claim unless a paired or
  deterministic protocol justifies another design.
- `require_confidence_intervals`: require uncertainty, not only means.
- `require_matched_budget_baseline`: block conclusions from unequal-resource
  comparisons.
- `require_model_policy_environment_evidence`: require all three evidence levels
  when the claim spans them; mark a level not applicable only with justification.
- `integrity_warn_blocks_completion`: legacy compatibility field; structured claim adjudication always requires integrity `pass`. Warnings stay visible as limitations.
- `same_family_review_is_provisional`: keep true unless a genuinely independent
  reviewer backend is configured.

## Safe edits

The Agent may refine the direction, benchmark priorities, endpoints, framework
preferences, and budgets when the user supplies new information. It must not
silently enable paid compute, private-data upload, license acceptance, real-
robot execution, paper writing, or a larger resource ceiling.

When no phase has started, the Agent may correct an over-specified active
direction with `research_state.py update-direction`. Once work has begun, record
a deliberate pivot or initialize a new run instead of rewriting history.

## Skill resolution and ideation

`skill_roots` lists explicit installation directories, resolved relative to the
project (absolute user paths are also allowed). Default order is `.agents/skills`,
`skills/all-local-skills`, then `skills`. Archive backups are never auto-installed.
`ideation.provider` selects `idea-spark` or `idea-discovery-robot`. Pass the actual
compute configuration into that provider; standalone defaults cannot expand it.
Stage-specific preflight checks only the current phase's required capabilities.
A missing optional wiki/monitor adapter can use local artifacts with a recorded
limitation. A missing required reviewer blocks review, not literature discovery.

Resource reservations are maximum GPU-count ? walltime allocations. The ledger
does not launch or kill jobs: the runner must enforce the timeout. Paid-compute
configuration records existing user authorization; it is not permission by itself.
Real-robot execution still requires a separate explicit authorization adapter.
