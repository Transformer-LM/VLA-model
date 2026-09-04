# Step 1 — Decompose the novelty

Timestamp: 2026-08-31 Asia/Shanghai

- Research problem: action-conditioned video/latent WAM predictions drift or become wrong under deployment shift, which can misguide VLA action guidance, reranking, verification, or replanning.
- Problem framing: after executing an action and receiving a real observation, use the prediction–observation residual to correct future WAM predictions; evaluate both prediction and downstream control.
- Core mechanism (initial claim): maintain an online residual/feedback state and inject it into subsequent action-conditioned predictions without retraining the base WAM.
- Key insight: execution supplies a free correction signal that an open-loop WAM currently wastes.
- Application domain: vision-based robot manipulation using a WAM and a VLA/diffusion policy.

This initial claim is intentionally the closest faithful formalization of the user's idea; later steps test whether a narrower action-dependent residual field remains open.
