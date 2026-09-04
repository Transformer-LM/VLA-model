# Round 4 Normative Corrections

This document incorporates `round-3-refined-proposal_20260830_124100.md` in full and makes the following three normative replacements. If any earlier wording conflicts, this document controls.

## 1. Missing-target geometry rule

If the target cloud is empty, the target 20D block is zero. The reference 20D block retains only its present mask and clipped visible-count fraction; its remaining 18 geometric values are zero. The entire 14D pair block is zero. No fallback coordinate origin, post-action coordinate, or stale target centroid is introduced.

If the target is visible but the reference is empty, the target-centered target block is computed normally, the reference block is zero, and the pair block is zero with both margin-validity masks zero.

## 2. Continue threshold and aliasing set

For the observation-only posterior, define

\[
\mathrm{FCR}=\frac{\#\{invalid\ events\ assigned\ continue\}}{\#\{invalid\ events\}}.
\]

Select \(\theta_r^+\) from validation candidates to maximize the valid-event continue rate subject to FCR \(\le0.05\). An always-non-continue threshold is included, so the constraint is always attainable. Report the achieved validation FCR without interpolation. Together with the already defined retract threshold \(\theta_r^-\), freeze

\[
\mathcal A_r=\{o:\theta^-_r<q^{obs}(o)<\theta^+_r\}
\]

before any transition-model test evaluation.

## 3. Sole claim-bearing gate

On \(\mathcal A_r\), \(\tau^{kin}\) must reduce IMR@FRR5 by at least 10% relative and by at least 5 percentage points absolute versus the strongest observation/no-trace baseline, while achieved test FRR remains at most 5%.

Invalidation recall is reported as the redundant complement \(1-\mathrm{IMR}\), not as an independent gate. Three-way decision cost, NLL/calibration, risk-coverage, latency, and full-distribution results are supporting evidence only.

The deployed-geometry transfer wording is:

> The result must survive PointMaps produced from deployed learned depth and instance masks.

The failure wording remains:

> Execution-trace conditional value was not established on the preregistered aliasing population.
