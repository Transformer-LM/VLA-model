# P025-v5 continuous-prefix sanity result

Status: **E0 sanity passed; not yet a paper claim**

P025-v5 reconstructs every twin from a fresh seeded LIBERO reset, applies the
benchmark initial state, replays the ten warmup actions and the complete policy
prefix, then continues directly into the candidate suffix.  It never restores
an intermediate flattened state.

Result on `goal_t0`, candidate boundary step 88:

- saved boundary error: `0.0`;
- nominal repeat error: `0.0`;
- selected geom block: `geom:190:wooden_cabinet_1_g29`;
- fixed charged budget: 780 simulator steps;
- unique witnesses: 1;
- certified endpoint pairs: 1 of 3;
- passing compliance endpoints: 0.02 versus 0.1;
- factual state/proprio/physical-effect differences: exactly 0;
- factual RGB/depth digests: exactly equal;
- candidate first activation frame: 6;
- candidate first divergence frame: 6;
- candidate task-effect maximum difference: 0.0032211;
- target WAM used by compiler: false.

The other two endpoint pairs were rejected because their candidate traces
diverged before the registered contact activation.  This is expected
fail-closed behavior rather than missing data.

Independent verification:

- manifest SHA-256: `fb71e8e35519e16d1dfcef2b286e1c62141c492243b9c87d119aa769faa0bd07`;
- verified blocks: 1;
- verified certificate pairs: 1;
- raw evidence size: approximately 47 MB;
- formal verifier result: pass.

Adversarial audit:

- unchanged real artifact passed the formal loader;
- modified raw pixel rejected;
- modified contact activation rejected;
- modified factual t0 proprio rejected;
- modified certificate measurement plus recomputed payload hash rejected;
- modified non-target static field rejected.

Remote evidence:

- `<PERSONAL_RESEARCH_ROOT>/results/israc/P025V5_SANITY_goal_t0_c11_israc_seed0.json`
- `<PERSONAL_RESEARCH_ROOT>/results/israc/P025V5_SANITY_goal_t0_c11_israc_seed0.json.evidence/`
- `<PERSONAL_RESEARCH_ROOT>/results/israc/P025V5_TAMPER_AUDIT_01/AUDIT.json`

The next gate is eight-boundary coverage followed by fixed-budget comparison
against candidate-contact and random-scene selectors.  This sanity result alone
does not establish the preregistered 2x yield or WAM-harm claims.
