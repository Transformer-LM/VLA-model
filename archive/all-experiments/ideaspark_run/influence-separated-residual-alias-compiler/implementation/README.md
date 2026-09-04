# ISRAC implementation

Current scope is the M0 engineering substrate:

- `israc/certificate.py`: simulator-agnostic, machine-checkable alias certificate;
- `israc/toy_physics.py`: deterministic physical unit-test fixture only;
- `tests/test_certificate.py`: valid-pair and anti-cheating tests;
- `run_toy_m0.py`: bounded smoke entry point.

The toy environment is explicitly not research evidence. Paper-facing evidence
must come from native MuJoCo/LIBERO and SAPIEN/RoboTwin adapters, with the target
WAM excluded from compilation and consulted only after a pair is frozen.

Run locally:

```bash
python -m unittest discover -s tests -v
python run_toy_m0.py
```
