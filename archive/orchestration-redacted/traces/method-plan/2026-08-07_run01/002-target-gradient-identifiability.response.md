# Future-target and gradient-treatment audit

**Verdict: NO-GO as written; repairable.**

A/B/C can estimate a controlled algorithmic contrast between correct-pairing gradient, stop-gradient and mismatched gradient, but single-state/single-action demonstrations cannot identify state-dependent action dynamics. The claim must be downgraded to a correspondence-specific predictive association under the behavior policy unless simulator action forks are added; this run will take the downgrade rather than add a new experiment family.

Required fixes:

1. Split episodes into disjoint D_head, D_adapter and D_post. Whitening, projection, nuisance model and head use only D_head; adapter training uses only D_adapter. On untouched D_post, A must improve correct-target nMSE over identity, B and C by at least 5% with a positive lower confidence bound. The main-camera target block must pass separately.
2. Define FP32 manual gradients with create_graph=False and detached scales. Use the common B action-gradient norm as the reference: r_t=0.30*||g_action,B||, and normalize both A/C auxiliary gradients to r_t within 1%. Prefer momentum-free SGD to avoid arm-specific optimizer moments; B computes a detached shadow future VJP and discards it.
3. Match C to A not only on auxiliary-gradient norm but also initial frozen-head loss, Huber saturation rate and target norm. This remains one matched placebo, not a universal generic-regularization control.

