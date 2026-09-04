# Claims from Results

**Verdict:** `claim_supported: no`  
**Routing:** `kill`  
**Confidence:** high within the pilot scope  
**Integrity:** warn  
**Assurance:** same-family, provisional

## Supported

- In this single MuJoCo oracle-state pilot, the GT mass/friction oracle improves `hard_id` assignment by only **0.5828 percentage points** over shared action-conditioned dynamics.
- The random-address assignment error decreases by **0.8159pp** and NLL by about **0.01575**, but seed 11 degrades by **0.8159pp** in assignment accuracy.
- The preregistered M1a gate correctly kills the idea: the ≥5pp and all-paired-seeds-positive conditions both fail.
- M1b system-ID versus full-history training was correctly not launched.

## Not supported

- No evidence that physical-property system identification improves object binding.
- No evidence that system-ID beats full-history memory; those models were not run.
- No evidence for RGB/RGB-D binding, VLA action quality, long-horizon memory, recovery, or real robots.
- No general conclusion that mass/friction is useless, or that all OA-WAM × EvoScene combinations fail.

## Critical boundary

The shared model already scores 95.5322%. Even a perfect 100% oracle could improve by at most 4.4678pp, below the preregistered 5pp threshold. Therefore this task/threshold pair has a structural ceiling mismatch. The result rejects the current operationalization; it does not establish a universal scientific negative.

## Decision

Kill this exact interaction-fingerprint idea and do not lower the gate post hoc or run M1b on the same dataset. A future pivot must first create a pose-only-unsaturated identity ambiguity task and preregister a feasible oracle-headroom gate on new data.
