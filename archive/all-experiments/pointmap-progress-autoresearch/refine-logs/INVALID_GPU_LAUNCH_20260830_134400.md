# Invalid E0 GPU launch v1

Status: **INVALID / NON-EVIDENCE**.

All four physical GPUs were individually idle at launch. RGB and Depth then failed immediately because PyTorch reports no deterministic CUDA backward implementation for `adaptive_avg_pool2d`. PointMap and simulator-pose Oracle completed, but their result payloads use the pre-fix trainer hash.

No v1 result may enter G0 aggregation. The trainer will replace adaptive pooling with an explicit deterministic equal-bin spatial reduction. Because that changes the trainer hash, all four modalities must be relaunched under one new hash; old PointMap/Oracle outputs are retained only as runtime diagnostics.

Failure is implementation compatibility, not an empirical result about RGB, Depth, PointMap, or Oracle.
