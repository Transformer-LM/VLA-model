# Refinement Report

**Problem:** Does a valid predictive world objective shape a VLA action-interface representation that closed-loop control uses?  
**Date:** 2026-08-07  
**Rounds:** 4 / 5  
**Final score:** 9.0 / 10  
**Final verdict:** READY (same-family provisional)

## Outputs

- Final proposal: 'refine-logs/FINAL_PROPOSAL.md'
- Review summary: 'refine-logs/REVIEW_SUMMARY.md'
- Score history: 'refine-logs/score-history.md'
- Round artifacts: 'refine-logs/round-0-initial-proposal.md' through 'round-4-review.md'

## Method Evolution Highlights

1. Replaced raw DINO difference with a blockwise current-nuisance-residualized future target and disjoint D_head/D_adapter/D_post.
2. Replaced vague auxiliary weighting with an exact FP32, detached, common-B-referenced dose under plain SGD.
3. Replaced ambient activation projection with explicit empirical PCA-space projectors, nuisance annihilation, Q equivalence and a locked per-seed eligibility table.
4. Replaced optimistic timing with physical-GPU, full-horizon, wrapper-inclusive accounting.

## Score Evolution

| Round | Overall | Verdict |
|---:|---:|---|
| 1 | 7.1 | REVISE |
| 2 | 8.1 | REVISE |
| 3 | 8.6 | REVISE |
| 4 | 9.0 | READY |

## Pushback / Drift Log

- Rejected simulator action forks because they would broaden cost and change the claim; wording was narrowed instead.
- Rejected new WAM architecture, RL, Diffusion, planning and extra benchmarks.
- Treated PFD overlap and narrow scope as an honest venue limitation rather than contribution-sprawl motivation.

## Remaining Weaknesses

- Same-family review is provisional.
- Novelty is high-overlap and protocol-level.
- Two tasks and one selected host permit only local claims.
- Strict falsification gates may produce a valid NO-RUN or negative result.

## Raw Reviews

Full reviewer outputs are preserved in 'round-1-review.md', 'round-2-review.md', 'round-3-review.md', 'round-4-review.md' and '.aris/traces/method-plan/2026-08-07_run01/'.

## Next Step

Proceed to claim-driven experiment planning, then isolated implementation and measured gates. Do not write a paper.

