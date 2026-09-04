# P026 held-out compiler preregistration

Frozen before collecting any episode-1 task-3 through task-9 rollout or
inspecting any compiler outcome. Task-3/4 episode-0 rollouts collected while
hardening provenance are explicitly infrastructure sanity data and excluded.

## Purpose

P025-v5 is an exploratory engineering pilot because its eight boundaries were
used while debugging replay and certificate rules. P026 is the first candidate
confirmatory set. No P025 boundary contributes to its primary statistic.

## Frozen source roster

| LIBERO-GOAL task | Episode | Environment seed |
|---:|---:|---:|
| 3 | 1 | 47 |
| 4 | 1 | 53 |
| 5 | 1 | 59 |
| 6 | 1 | 61 |
| 7 | 1 | 67 |
| 8 | 1 | 71 |
| 9 | 1 | 73 |

Every attempt uses ten wait actions and at most 400 policy steps. All attempts
are logged. A source enters the compiler population only if saved-action
admission independently replays success from the named benchmark state. A
failed policy rollout is not replaced according to compiler yield.

## Frozen policy provenance

Each new source manifest must contain:

- server handshake metadata and announced checkpoint path;
- checkpoint byte size and SHA-256;
- StarVLA git commit, dirty-status hash, diff hash, and critical source hashes;
- collector SHA-256;
- unnormalization key, action-ensemble flag, DDIM flag/steps, image size, action
  chunk size, task instruction, environment seed, and benchmark episode.

The source is rejected if this provenance is missing or if saved actions do not
independently reproduce reward, done, states, RGB, contacts, and boundary states.

## Outcome-blind boundary rule

For every admitted source with `N` saved policy chunks, enumerate indices
`1..N-1`. Rank them by

`SHA256(source_manifest_sha256 | candidate_index)`

and take the first three (or all if fewer than three). This ranking must be
computed before any contact-support selector is run. Candidate horizon is four
chunks, truncated only at the end of the recorded policy support.

## Frozen compiler matrix

- selectors: ISRAC contact subtraction, candidate contact, random scene;
- selector seeds: 0, 1, 2;
- physical family: compliance endpoints `[0.004, 0.020, 0.100]`;
- at most three selected blocks per boundary;
- complete three-endpoint pairwise sweep;
- identical fresh seeded reset, benchmark init, wait actions, policy prefix,
  and candidate suffix for every selector;
- pool-independent priority `SHA256(environment_seed + selector_seed | geom address)`;
- every valid boundary charged for the full three-block execution cap;
- unique geom witnesses, not endpoint pairs, are the sampling unit.

## Decision rule

P026 simple-baseline gate passes only if:

1. all three selectors and all three seeds cover the identical admitted
   boundary set;
2. ISRAC unique-witness yield per charged simulator step is at least 2x the
   strongest simple baseline;
3. boundary/seed-cluster bootstrap 95% lower bound of the ratio is above 1;
4. no source, boundary, parameter, or selector is removed after observing
   witness yield.

Passing P026 does not by itself establish novelty above 7. It authorizes the
pre-registered strong BO/CMA-style search, second physical mechanism, and
held-out WAM harm gates. Failure routes to redesign or kill, not selective
replacement or extra ISRAC-only budget.
