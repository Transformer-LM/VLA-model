# Gap Map

## G1 — Unmeasured oracle-progress headroom

Status: unresolved. Existing papers show average gains from memory or progress modules, but the user's observed π0.5 failures have not been decomposed by giving the executor oracle current subtask, oracle completion, or oracle recovery. Without this test, a memory method may target the wrong bottleneck.

## G2 — Scalar progress is not semantic task state

Status: unresolved. ProgressVLA and task-progress probes use normalized scalar progress or normalized time. Branching, repeated, reversible, and partially completed tasks require a structured state whose components can advance independently or regress.

## G3 — Memory can preserve a wrong conclusion

Status: unresolved. Keyframe, recurrent-token, perceptual-cognitive, and language memories preserve history, but do not generally expose which evidence supports a completion claim or retract only the conclusions invalidated by contradictory evidence.

## G4 — Counterfactual history identifiability

Status: partially covered. MIKASA-Robo and recurrent-memory studies expose partial observability, but current comparisons rarely use paired episodes with matched current observations and different histories requiring different next actions, plus matched different observations representing the same task state.

## G5 — WAM necessity for outcome verification

Status: unresolved. World/action models can predict future effects or guide scalar progress, but it remains unclear whether they beat a matched discriminative postcondition verifier, geometry tracker, or VLM judge at detecting the specific stage errors that matter for control.

## G6 — Detection does not imply recovery competence

Status: unresolved. Runtime monitors can detect stalled progress, while recovery methods often rely on curated recovery data. The causal contribution of state correction versus additional recovery coverage remains entangled.
