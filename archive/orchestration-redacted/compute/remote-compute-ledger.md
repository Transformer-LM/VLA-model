# Direct SSH compute ledger: <PRIVATE_SERVER>

### env: israc-libero-m0@1ca07264

- how: existing personal venv `<PERSONAL_RESEARCH_ROOT>/venvs/libero-eval-py310`; source checkout injected from `<PERSONAL_RESEARCH_ROOT>/workspace/third_party/LIBERO`
- tier: `{cpus: 2, mem_gib: 4, gpus: 0}`
- weights: none
- spec: `ideaspark_run/influence-separated-residual-alias-compiler/env-spec-libero-m0.json`
- spec_sha256: `1ca0726458d5ec3f5322ff83a2c47c05b61c88859618673e10dc83d2cfba2981`
- validated: 2026-08-31 tier 1 import passed; real deterministic LIBERO M0 passed in `R002_libero_native_friction_m0_v2.json`; fresh agent-follows-doc passed with exit code 0 and the documented witness
- gotcha: `libero-render` conda prefix is incomplete; use the registered venv. Headless rendering requires the personal OSMesa runtime and both `MUJOCO_GL=osmesa` and `PYOPENGL_PLATFORM=osmesa`. A dormant friction change produces about `2e-12` MuJoCo state drift, below the pre-existing `1e-10` exact-replay numerical floor. SSH MOTD precedes stdout, so match the witness line-wise; successful execution also emits non-fatal robosuite private-macro and Gym deprecation warnings on stderr.

Documented repeatable invocation (read-only with respect to experiment artifacts):

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=<PERSONAL_RESEARCH_ROOT>/workspace/israc/implementation:<PERSONAL_RESEARCH_ROOT>/workspace/third_party/LIBERO \
LIBERO_CONFIG_PATH=<PERSONAL_RESEARCH_ROOT>/config/libero \
MUJOCO_GL=osmesa \
PYOPENGL_PLATFORM=osmesa \
LD_LIBRARY_PATH=<PERSONAL_RESEARCH_ROOT>/renderer-runtime/osmesa/prefix/usr/lib/x86_64-linux-gnu:<PERSONAL_RESEARCH_ROOT>/renderer-runtime/osmesa/prefix/lib/x86_64-linux-gnu \
MESA_SHADER_CACHE_DIR=<PERSONAL_RESEARCH_ROOT>/renderer-runtime/osmesa/cache \
XDG_CACHE_HOME=<PERSONAL_RESEARCH_ROOT>/renderer-runtime/osmesa/cache \
<PERSONAL_RESEARCH_ROOT>/venvs/libero-eval-py310/bin/python \
<PERSONAL_RESEARCH_ROOT>/workspace/israc/implementation/smoke_libero_env.py
```

Expected witness regex, applied line-wise (not to the whole SSH stdout buffer):

```text
^WITNESS_LIBERO state=.* rgb=\(32, 32, 3\)/uint8 depth=\(32, 32, 1\)/float32$
```

### env: starvla-libero-inference@4abcaace

- how: existing personal Conda prefix `<PERSONAL_RESEARCH_ROOT>/conda/envs/cf-dynalign`; StarVLA checkout at `<PERSONAL_RESEARCH_ROOT>/workspace/cf-dynalign-starvla/source/starVLA`
- tier: `{cpus: 4, mem_gib: 24, gpus: 1}`
- weights: `<PERSONAL_RESEARCH_ROOT>/checkpoints/starvla/Qwen3-VL-OFT-LIBERO-4in1/checkpoints/steps_50000_pytorch_model.pt`; local base VLM `<PERSONAL_RESEARCH_ROOT>/checkpoints/qwen/Qwen3-VL-4B-Instruct`
- spec: `ideaspark_run/influence-separated-residual-alias-compiler/env-spec-starvla-libero-inference.json`
- spec_sha256: `4abcaaceac7da3c458ac81b18ca0ce512b3b2a513f2f81bb43b42cf223a5b760`
- validated: 2026-08-31 tier 1 imports passed (`torch 2.6.0+cu124`, CUDA 12.4, NumPy 1.26.4, Transformers 4.57.0); tier 2 CUDA matmul passed on an immediately checked idle GPU 2
- gotcha: the official checkpoint stores the base VLM as relative path `playground/Pretrained_models/Qwen3-VL-4B-Instruct`; a personal symlink under the personal StarVLA checkout resolves it to the personal Qwen checkpoint. No server-side internet access is used.

Documented single-GPU inference-server invocation:

```bash
cd <PERSONAL_RESEARCH_ROOT>/workspace/cf-dynalign-starvla/source/starVLA
PYTHONDONTWRITEBYTECODE=1 \
TOKENIZERS_PARALLELISM=false \
PYTHONPATH=<PERSONAL_RESEARCH_ROOT>/workspace/cf-dynalign-starvla/source/starVLA \
CUDA_VISIBLE_DEVICES=2 \
<PERSONAL_RESEARCH_ROOT>/conda/envs/cf-dynalign/bin/python \
deployment/model_server/server_policy.py \
--ckpt_path <PERSONAL_RESEARCH_ROOT>/checkpoints/starvla/Qwen3-VL-OFT-LIBERO-4in1/checkpoints/steps_50000_pytorch_model.pt \
--port 17778 --use_bf16
```

Expected readiness witness:

```text
PolicyServerWrapper ready
```
