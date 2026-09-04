# P026 protocol amendment v2

This file extends, and does not overwrite, `P026_PROTOCOL_AMENDMENT.md`.

The first final-lock sanity (`P026_COMPILER_LOCK_FINAL.json`) compiled one
candidate-contact cell successfully but its independent verifier rejected the
artifact. The failure exposed a baseline-validity bug: the verifier required
every attempted edited block, including unsuccessful baseline attempts, to
preserve the factual prefix. That would exclude legitimate zero-witness
baseline cells and bias the comparison.

The failed sanity directory, lock, launch record, manifest, evidence, and log
are preserved unchanged. No formal cell was launched.

Version 2 freezes the following correction before a new sanity and formal run:

- any attempted block may remain as a zero-witness failure;
- an endpoint pair can enter `endpoint_strength_curve` only if both edited
  factual traces match the two raw unedited nominal traces frame by frame;
- numeric state/proprio/effect fields use only the measured nominal-repeat
  envelope; RGB, depth, and contact traces must match exactly;
- every accepted certificate binds both raw unedited evidence hashes in
  addition to its edited endpoints and edited repeat;
- the verifier independently recomputes this source-factual fidelity only for
  all three legal endpoint pairs from raw evidence, derives the complete passing
  and failing set, and requires exact equality with the manifest; failed block
  evidence is retained for honest zero-yield accounting;
- a changed physical parameter must remain inactive throughout the factual
  prefix and become activated only by the candidate action.

## Additional pre-formal exposure

The failed final-lock sanity produced one candidate-contact cell for task 3,
candidate index 7, selector seed 0. Its compiler output was inspected only to
diagnose the verifier failure. Together with the two ISRAC debug cells disclosed
in version 1, this makes three unique exposed method-boundary-seed cells. All
three are excluded from formal statistics and all 189 planned cells are rerun
under the new immutable lock.

The version-2 compiler lock hash-binds both this file and the unchanged version-1
amendment; neither disclosure can be replaced independently.
The exact predecessor SHA-256 pinned here is
`fbfa5f55e2b70067468dad178d886e1f6a59154ba7675acf9be00f545ddabcbb`.

The verifier also reconstructs the selector-visible physical block pool from
both raw nominal contact traces and a geom/body topology authenticated by the
simulator-model hash. It requires the visible-pool count and the complete ordered
`(parameter_address, geom_ids)` selection to equal the manifest, so an entire
successful or failed block cannot be silently deleted.

The seven sources, 21 boundary indices, selectors, selector seeds, physical
family/endpoints, budgets, witness-key estimand, bootstrap, and 2x/CI decision
rule remain unchanged. The formal label remains:

`amended confirmatory with disclosed three-cell pre-formal contamination`

The v1 failed lock sanity is an infrastructure failure, not a formal result.
