---
name: scoop-check
description: Check whether a concrete research contribution is already established by prior work. Use for mechanism-level novelty comparison, nearest-work verification, or a final prior-art check before experiments.
---

# Contribution collision check

Return a bounded, evidence-grounded judgment of the stated contribution. Search
coverage and novelty are separate axes. Never interpret a failed search or zero
hits as proof of novelty.

## Inputs and search

Extract the research question, mechanism, intended benefit, assumptions and
evaluation regime. Infer routine query choices. If the mechanism is unspecified,
search the area and return `unresolved` for the novelty judgment.

Use `paper-search` for complementary problem, broad-domain, mechanism-signature,
alias and nearest-work queries. Include historical sources and citation tracing
when recent search may miss the mechanism. Reuse throttling and caching. Record
queries, date windows, query time, connector errors, counts and coverage gaps.
Deduplicate by DOI, arXiv ID, then normalized title. Database failure differs from
a successful query with zero hits. Model-recalled papers are unverified leads.

## Full-text comparison

Prioritize core mechanism matches, close competitors and ambiguous abstracts.
Read enough full text to resolve setup, method and assumptions. A 3–7 paper
shortlist is an initial budget, not a coverage guarantee. Expand it when a material
collision remains. Do not pad sparse results with unrelated work.

Resolve PDF/HTML URLs from primary sources. Use the bundled cross-platform
`scripts/fetch_paper.py <PDF_URL> <paper-slug> --project-dir <project>` with the
resolved Python launcher. It verifies/downloads PDFs and extracts text. Record
HTML/abstract-only fallback explicitly when full text cannot be accessed.

For each comparison retain verified identifier and URL, problem framing,
mechanism, claimed insight, application, assumptions, demonstrated capability,
and section/equation/table evidence. State which proposed contribution is already
established, changed, or unresolved.

The four axes organize evidence; their match count is not a novelty score.
Mechanism collisions can be decisive across applications. Sharing a benchmark
does not make a different mechanism redundant.

## Decision contract

- `search_status`: complete | partial | failed.
- `evidence_coverage`: sufficient_for_current_claim | insufficient.
- `novelty_status`: contradicted | incremental | potentially_distinct | unresolved.

`complete` means the declared search plan ran and material coverage gaps were
resolved, not that all literature was exhausted.

- **contradicted**: verified work already establishes the proposed contribution.
- **incremental**: a narrower extension remains, with its value stated.
- **potentially_distinct**: full-text comparisons support a concrete capability or
  mechanism difference that still requires experimental validation.
- **unresolved**: unspecified mechanism, empty results, material source failure,
  or full-text uncertainty could change the verdict.

A verified direct collision can contradict a claim under partial coverage.
Incomplete coverage cannot promote a positive novelty judgment into an experiment
gate. Distinguish expected benefits from observed effects.

## Output

Return a concise verdict, closest-work comparison, concrete delta, limitations,
and next discriminating search/experiment. Persist full retrieval records when
the caller stores artifacts; avoid duplicating them in its context.

In embodied-autoresearch, write `idea-stage/NOVELTY_REPORT.json`:

```json
{
  "search_status": "partial",
  "evidence_coverage": "insufficient",
  "novelty_status": "unresolved",
  "verified_prior_work": [],
  "delta": "Not yet established",
  "queries": [],
  "source_failures": [],
  "unresolved_collisions": [],
  "next_action": "Resolve missing primary sources"
}
```

Each verified prior-work entry includes identifier, URL, full-text access status,
evidence pointers and the affected contribution. State how the delta will be
tested; never invent a measured benefit. Preserve superseded reports through the
caller's revision mechanism.
