# Deterministic pooling runtime-fix review

Verdict: **APPROVE**

Trainer SHA-256: `c2992f68f9485a168254a42def40bf5847388b772dadb777d54b4bf687c6cfe8`.

For registered 96 x 96 inputs, the three stride-2 convolutions produce 12 x 12 features. Reshaping this as `2 x 6 x 2 x 6` and averaging the two six-pixel axes yields `[batch, 96, 2, 2]`, exactly matching adaptive 2 x 2 equal-bin averaging and the unchanged 384-wide linear head input.

The explicit non-overlapping mean is compatible with strict deterministic CUDA execution. Deterministic algorithms, cuDNN, and cuBLAS remain enabled; a finite forward/backward smoke passed on physical GPU 2.

All four modalities must rerun under this hash. V1 PointMap/Oracle cannot be mixed with corrected RGB/Depth even though they did not use the image pooling path.

AST parsing passed. The reviewer made no edits.
