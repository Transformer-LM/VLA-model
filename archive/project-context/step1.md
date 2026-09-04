# Step 1 — Decompose novelty

Timestamp: 2026-08-29 Asia/Shanghai

- Problem framing: improve VLA/WAM physical grounding by adding future depth to RGB rollouts.
- Core mechanism: estimate or jointly predict future depth, compress RGB and depth into latents, and couple the latent to action learning/control.
- Key insight: RGB appearance under-specifies metric geometry and contact; latent geometry may retain the useful information without dense decoding cost.
- Application domain: language-conditioned robotic manipulation, especially metric/contact-sensitive tasks.
