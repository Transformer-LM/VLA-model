# Step 2 — Search and deduplicate

Timestamp: 2026-08-31 Asia/Shanghai

Queries, 2023–2026, max 5 per source:

1. `action conditioned video world model prediction error correction robot manipulation`
2. `robot world model online adaptation calibration`
3. `residual correction observed rollout future video world model VLA`

Connector status:

- arXiv API: SSL `UNEXPECTED_EOF_WHILE_READING` on all three queries.
- Semantic Scholar: HTTP 429 after bounded retries on all three queries.
- OpenAlex: partial success with intermittent 504.
- Crossref: success but substantial lexical noise.
- DBLP/OpenReview: zero hits through the installed search route.

API union contained 27 unique records. Mechanism-level web search added seven verified arXiv papers: Feedback World Model, ReDRAW, Say Dream and Act, When to Trust Imagination, CheckVLA, DreamX-Phi 1.0, and tau0-WM. No unverified model-recall citation was added.
