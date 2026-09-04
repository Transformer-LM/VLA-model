from __future__ import annotations

import json

from israc.certificate import AliasCertificate, NoiseEnvelope, certify_alias_pair
from israc.toy_physics import make_world, rollout


def main() -> None:
    low = make_world("world_low", 0.10)
    high = make_world("world_high", 1.10)
    result = certify_alias_pair(
        rollout(low, "factual_free", 1),
        rollout(high, "factual_free", 1),
        rollout(low, "candidate_contact", 2),
        rollout(high, "candidate_contact", 2),
        AliasCertificate(
            factual_action_id="factual_free",
            candidate_action_id="candidate_contact",
            top_k=8,
            search_objective_terms=("task_effect_separation", "factual_transcript_constraint"),
            compiler_seed=20260831,
            simulator="toy-only",
            task_id="contact-transfer-unit-test",
            snapshot_id="deterministic-s0",
        ),
        NoiseEnvelope(0.0, 0.0, 0.0, 1e-12),
    )
    print(json.dumps({
        "claim_limit": "Certificate engineering test only; not simulator, VLA, or WAM evidence.",
        "passed": result.passed,
        "failures": result.failures,
        "measurements": result.measurements,
        "certificate_sha256": result.certificate_sha256,
    }, indent=2, sort_keys=True))
    raise SystemExit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
