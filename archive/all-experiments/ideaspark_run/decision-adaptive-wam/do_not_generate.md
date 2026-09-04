# Do not generate: the stated mechanism is occupied

**State:** `do_not_generate`

The requested contribution is not defensibly novel as stated. The degraded structured retrieval missed three exact, web-verified recent papers, so their absence from `lit_results.json` cannot be treated as positive novelty evidence:

- **RISE: Adaptive Imagination for World Action Models** (`arXiv:2608.20430`) already makes sequential WAM `Roll/Stop` decisions by comparing expected planning gain with additional compute cost. Moving this mechanism from driving to manipulation is domain transfer.
- **VLA-ATTC: Adaptive Test-Time Compute for VLA Models with Relative Action Critic Model** (`arXiv:2605.01194`) already uses an uncertainty clutch to trigger extra VLA candidate computation and a pairwise Relative Action Critic to select the action; it is evaluated with pi0.5 on LIBERO-LONG.
- **When and How Much to Imagine** (`arXiv:2602.08236`) already decides whether and how much to invoke a world model using evidence sufficiency and a correctness-minus-imagination-cost objective, including embodied navigation.

The structured corpus also contains close partial moves: AHA-WAM amortizes and routes long-horizon world context, tau0-WM samples/ranks candidates and invokes simulator rectification, OneTwoVLA switches between acting and reasoning, and AR-MBPO adapts rollout length from model accuracy. Combining these with the three exact collisions would be a system composition, not a new load-bearing mechanism. `When to Trust Imagination` is a boundary paper on adaptive execution length rather than adaptive generation compute, and the query already excludes that route.

## Remedial pivot

Do not rephrase “expected action-decision change” as another learned gate. A viable re-invocation must change the scientific estimand or failure axis. The most defensible problem-level pivot exposed by this corpus is: **when a WAM changes the proposed action, can that change be calibrated to improvement in the real downstream outcome under model misspecification, observation aliasing, and stochastic candidate turnover?** This remains a diagnosis, not a proposed method.

For a method contribution, specify an independently falsifiable signal that is not the WAM's own uncertainty, score, predicted gain, or evidence-sufficiency estimate; state the frozen VLA/WAM access level, RGB/proprioceptive data, benchmark, and no-tactile constraint. Otherwise pivot the contribution type to an `empirical_reveal` / controlled diagnostic that measures action-change sensitivity versus real success across fixed compute budgets, without claiming a new adaptive controller.

All 11 cached full-text fetches failed, and the mandatory AHA-WAM anchor top-up also failed. Structured-pool residue claims are therefore abstract-level; the exact-collision decision relies on the separate primary-record supplement.
