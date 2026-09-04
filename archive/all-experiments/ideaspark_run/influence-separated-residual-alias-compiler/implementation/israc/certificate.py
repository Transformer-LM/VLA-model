"""Machine-checkable certificates for influence-separated residual aliases.

The certifier deliberately knows nothing about a particular WAM.  A compiler
may use simulator state, native physics parameters, contact traces and task
effects, but the target WAM score is admitted only as a post-hoc diagnostic.
This separation is the central anti-overfitting contract of ISRAC.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Mapping, Sequence


Vector = tuple[float, ...]


@dataclass(frozen=True)
class PhysicalParameter:
    """One simulator-native, action-independent physical parameter block."""

    block_id: str
    family: str
    engine_field: str
    value: float
    lower: float
    upper: float
    physical_units: str
    action_conditioned: bool = False
    scripted_failure: bool = False

    def validate(self) -> list[str]:
        failures: list[str] = []
        if not self.block_id or not self.family or not self.engine_field:
            failures.append("parameter_semantics_missing")
        if not self.physical_units:
            failures.append("parameter_units_missing")
        if not math.isfinite(self.value) or not self.lower <= self.value <= self.upper:
            failures.append("parameter_out_of_physical_bounds")
        if self.action_conditioned:
            failures.append("action_conditioned_parameter_forbidden")
        if self.scripted_failure:
            failures.append("scripted_failure_forbidden")
        return failures


@dataclass(frozen=True)
class FrameTrace:
    """One aligned simulator frame.

    RGB and depth are flattened numeric probes rather than hashes so the same
    certifier supports exact deterministic replay and repeat-noise envelopes.
    Production adapters may store full arrays separately and pass stable probe
    vectors here.
    """

    state: Vector
    proprio: Vector
    rgb_sha256: str
    depth_sha256: str
    physical_effect_probe: Vector
    task_effect: Vector
    active_parameter_blocks: tuple[str, ...] = ()
    contact_geom_pairs: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True)
class RolloutTrace:
    world_id: str
    action_id: str
    action_rank: int
    frames: tuple[FrameTrace, ...]
    parameters: tuple[PhysicalParameter, ...]


@dataclass(frozen=True)
class NoiseEnvelope:
    state: float
    proprio: float
    physical_effect_probe: float
    task_effect: float


@dataclass(frozen=True)
class AliasCertificate:
    factual_action_id: str
    candidate_action_id: str
    top_k: int
    search_objective_terms: tuple[str, ...]
    compiler_seed: int
    simulator: str
    task_id: str
    snapshot_id: str
    allowed_activation_lag: int = 0
    factual_action_sha256: str = ""
    candidate_action_sha256: str = ""
    evidence_sha256: tuple[str, ...] = ()
    static_config_sha256: tuple[str, str] = ("", "")
    simulator_model_sha256: str = ""
    task_asset_sha256: str = ""
    engine_identity: str = ""
    parameter_addresses: tuple[str, ...] = ()
    factual_observation_repeat_stable: bool = True


@dataclass(frozen=True)
class CertificateResult:
    passed: bool
    failures: tuple[str, ...]
    measurements: Mapping[str, float | int | str | bool]
    certificate_sha256: str
    canonical_payload: str


def _max_abs(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        return math.inf
    values: list[float] = []
    for x, y in zip(a, b):
        left, right = float(x), float(y)
        if not math.isfinite(left) or not math.isfinite(right):
            return math.inf
        values.append(abs(left - right))
    return max(values, default=0.0)


def _trace_diff(a: RolloutTrace, b: RolloutTrace, field_name: str) -> float:
    if len(a.frames) != len(b.frames):
        return math.inf
    return max(
        (_max_abs(getattr(x, field_name), getattr(y, field_name)) for x, y in zip(a.frames, b.frames)),
        default=0.0,
    )


def _trace_digest_equal(a: RolloutTrace, b: RolloutTrace, field_name: str) -> bool:
    if len(a.frames) != len(b.frames):
        return False
    return all(
        str(getattr(left, field_name)) == str(getattr(right, field_name))
        for left, right in zip(a.frames, b.frames)
    )


def _trace_is_finite(trace: RolloutTrace) -> bool:
    for frame in trace.frames:
        for field_name in ("state", "proprio", "physical_effect_probe", "task_effect"):
            if any(not math.isfinite(float(value)) for value in getattr(frame, field_name)):
                return False
        for field_name in ("rgb_sha256", "depth_sha256"):
            value = str(getattr(frame, field_name))
            if len(value) != 64 or any(char not in "0123456789abcdef" for char in value.casefold()):
                return False
    return True


def _envelope_failures(envelope: NoiseEnvelope, prefix: str) -> list[str]:
    failures: list[str] = []
    for field_name in ("state", "proprio", "physical_effect_probe", "task_effect"):
        value = float(getattr(envelope, field_name))
        if not math.isfinite(value) or value < 0.0:
            failures.append(f"{prefix}_{field_name}_envelope_invalid")
    return failures


def _first_divergence(a: RolloutTrace, b: RolloutTrace, envelope: NoiseEnvelope) -> int | None:
    if len(a.frames) != len(b.frames):
        return 0
    for index, (x, y) in enumerate(zip(a.frames, b.frames)):
        if (
            _max_abs(x.state, y.state) > envelope.state
            or _max_abs(x.proprio, y.proprio) > envelope.proprio
            or _max_abs(x.task_effect, y.task_effect) > envelope.task_effect
        ):
            return index
    return None


def _first_joint_activation(a: RolloutTrace, b: RolloutTrace, changed_blocks: set[str]) -> int | None:
    if len(a.frames) != len(b.frames):
        return None
    for index, (x, y) in enumerate(zip(a.frames, b.frames)):
        if changed_blocks.intersection(x.active_parameter_blocks) and changed_blocks.intersection(
            y.active_parameter_blocks
        ):
            return index
    return None


def _first_any_activation(a: RolloutTrace, b: RolloutTrace, changed_blocks: set[str]) -> int | None:
    """Return the first frame where either world activates a changed block."""

    if len(a.frames) != len(b.frames):
        return None
    for index, (x, y) in enumerate(zip(a.frames, b.frames)):
        if changed_blocks.intersection(x.active_parameter_blocks) or changed_blocks.intersection(
            y.active_parameter_blocks
        ):
            return index
    return None


def _changed_parameter_blocks(a: RolloutTrace, b: RolloutTrace) -> tuple[set[str], list[str]]:
    failures: list[str] = []
    left = {p.block_id: p for p in a.parameters}
    right = {p.block_id: p for p in b.parameters}
    if set(left) != set(right):
        return set(), ["parameter_schema_mismatch"]
    changed: set[str] = set()
    for block_id in sorted(left):
        pa, pb = left[block_id], right[block_id]
        failures.extend(pa.validate())
        failures.extend(pb.validate())
        if (pa.family, pa.engine_field, pa.lower, pa.upper, pa.physical_units) != (
            pb.family,
            pb.engine_field,
            pb.lower,
            pb.upper,
            pb.physical_units,
        ):
            failures.append("parameter_semantics_changed_between_worlds")
        if pa.value != pb.value:
            changed.add(block_id)
    if not changed:
        failures.append("no_physical_parameter_changed")
    return changed, failures


def _canonical_payload(
    certificate: AliasCertificate,
    measurements: Mapping[str, float | int | str | bool],
    failures: Sequence[str],
    factual_envelope: NoiseEnvelope,
    candidate_envelope: NoiseEnvelope,
) -> str:
    def safe_float(value: float) -> float | str:
        converted = float(value)
        return converted if math.isfinite(converted) else "nonfinite"

    payload = {
        "certificate": {
            "factual_action_id": certificate.factual_action_id,
            "candidate_action_id": certificate.candidate_action_id,
            "top_k": certificate.top_k,
            "search_objective_terms": list(certificate.search_objective_terms),
            "compiler_seed": certificate.compiler_seed,
            "simulator": certificate.simulator,
            "task_id": certificate.task_id,
            "snapshot_id": certificate.snapshot_id,
            "allowed_activation_lag": certificate.allowed_activation_lag,
            "factual_action_sha256": certificate.factual_action_sha256,
            "candidate_action_sha256": certificate.candidate_action_sha256,
            "evidence_sha256": list(certificate.evidence_sha256),
            "static_config_sha256": list(certificate.static_config_sha256),
            "simulator_model_sha256": certificate.simulator_model_sha256,
            "task_asset_sha256": certificate.task_asset_sha256,
            "engine_identity": certificate.engine_identity,
            "parameter_addresses": list(certificate.parameter_addresses),
            "factual_observation_repeat_stable": certificate.factual_observation_repeat_stable,
        },
        "factual_envelope": {
            field_name: safe_float(getattr(factual_envelope, field_name))
            for field_name in ("state", "proprio", "physical_effect_probe", "task_effect")
        },
        "candidate_envelope": {
            field_name: safe_float(getattr(candidate_envelope, field_name))
            for field_name in ("state", "proprio", "physical_effect_probe", "task_effect")
        },
        "measurements": dict(sorted(measurements.items())),
        "failures": sorted(set(failures)),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def certify_alias_pair(
    factual_plus: RolloutTrace,
    factual_minus: RolloutTrace,
    candidate_plus: RolloutTrace,
    candidate_minus: RolloutTrace,
    certificate: AliasCertificate,
    envelope: NoiseEnvelope,
    candidate_envelope: NoiseEnvelope | None = None,
) -> CertificateResult:
    """Validate one two-world residual-alias certificate."""

    failures: list[str] = []
    if candidate_envelope is None:
        candidate_envelope = envelope
    traces = (factual_plus, factual_minus, candidate_plus, candidate_minus)
    if any(not _trace_is_finite(trace) for trace in traces):
        failures.append("trace_contains_nonfinite_or_invalid_digest")
    failures.extend(_envelope_failures(envelope, "factual"))
    failures.extend(_envelope_failures(candidate_envelope, "candidate"))
    if certificate.top_k < 1:
        failures.append("top_k_invalid")
    if certificate.allowed_activation_lag < 0:
        failures.append("activation_lag_invalid")
    if not certificate.factual_observation_repeat_stable:
        failures.append("factual_observation_repeat_unstable")
    if factual_plus.action_id != certificate.factual_action_id or factual_minus.action_id != certificate.factual_action_id:
        failures.append("factual_action_mismatch")
    if candidate_plus.action_id != certificate.candidate_action_id or candidate_minus.action_id != certificate.candidate_action_id:
        failures.append("candidate_action_mismatch")
    if candidate_plus.action_rank != candidate_minus.action_rank:
        failures.append("candidate_rank_world_dependent")
    if not (1 <= candidate_plus.action_rank <= certificate.top_k):
        failures.append("candidate_outside_policy_top_k")
    if len({trace.world_id for trace in traces}) != 2:
        failures.append("expected_exactly_two_worlds")
    if not (
        factual_plus.world_id == candidate_plus.world_id
        and factual_minus.world_id == candidate_minus.world_id
        and factual_plus.world_id != factual_minus.world_id
    ):
        failures.append("world_pairing_mismatch")

    forbidden_terms = {term.casefold() for term in certificate.search_objective_terms}
    if forbidden_terms.intersection({"wam_score", "wam_ranking", "target_wam", "residual_sign"}):
        failures.append("target_wam_leaked_into_compiler_objective")

    changed_blocks, parameter_failures = _changed_parameter_blocks(factual_plus, factual_minus)
    failures.extend(parameter_failures)
    candidate_changed, candidate_parameter_failures = _changed_parameter_blocks(candidate_plus, candidate_minus)
    failures.extend(candidate_parameter_failures)
    if changed_blocks != candidate_changed:
        failures.append("parameter_worlds_differ_across_actions")
    if len(changed_blocks) != 1:
        failures.append("expected_exactly_one_changed_parameter_block")

    factual_diffs = {
        "factual_state_max_abs": _trace_diff(factual_plus, factual_minus, "state"),
        "factual_proprio_max_abs": _trace_diff(factual_plus, factual_minus, "proprio"),
        "factual_physical_effect_probe_max_abs": _trace_diff(
            factual_plus, factual_minus, "physical_effect_probe"
        ),
    }
    thresholds = {
        "factual_state_max_abs": envelope.state,
        "factual_proprio_max_abs": envelope.proprio,
        "factual_physical_effect_probe_max_abs": envelope.physical_effect_probe,
    }
    for key, value in factual_diffs.items():
        if value > thresholds[key]:
            failures.append(f"{key}_exceeds_repeat_noise")

    factual_rgb_equal = _trace_digest_equal(factual_plus, factual_minus, "rgb_sha256")
    factual_depth_equal = _trace_digest_equal(factual_plus, factual_minus, "depth_sha256")
    if not factual_rgb_equal:
        failures.append("factual_rgb_digest_mismatch")
    if not factual_depth_equal:
        failures.append("factual_depth_digest_mismatch")

    factual_activation = _first_any_activation(factual_plus, factual_minus, changed_blocks)
    if factual_activation is not None:
        failures.append("changed_parameter_activated_in_factual")

    divergence = _first_divergence(candidate_plus, candidate_minus, candidate_envelope)
    activation = _first_joint_activation(candidate_plus, candidate_minus, changed_blocks)
    if divergence is None:
        failures.append("candidate_has_no_physical_divergence")
    if activation is None:
        failures.append("changed_parameter_never_physically_activated")
    if divergence is not None and activation is not None:
        if divergence < activation:
            failures.append("candidate_diverges_before_physical_activation")
        elif divergence - activation > certificate.allowed_activation_lag:
            failures.append("candidate_divergence_too_late_after_activation")

    candidate_effect_diff = _trace_diff(candidate_plus, candidate_minus, "task_effect")
    if candidate_effect_diff <= candidate_envelope.task_effect:
        failures.append("candidate_task_effect_not_separated")

    measurements: dict[str, float | int | str | bool] = {
        **factual_diffs,
        "factual_rgb_digest_equal": factual_rgb_equal,
        "factual_depth_digest_equal": factual_depth_equal,
        "candidate_task_effect_max_abs": candidate_effect_diff,
        "parameter_first_factual_activation_frame": (
            -1 if factual_activation is None else factual_activation
        ),
        "candidate_first_divergence_frame": -1 if divergence is None else divergence,
        "parameter_first_activation_frame": -1 if activation is None else activation,
        "changed_parameter_blocks": len(changed_blocks),
        "candidate_rank": candidate_plus.action_rank,
        "target_wam_used_in_search": bool(
            forbidden_terms.intersection({"wam_score", "wam_ranking", "target_wam", "residual_sign"})
        ),
    }
    safe_measurements = {
        key: (value if not isinstance(value, float) or math.isfinite(value) else "nonfinite")
        for key, value in measurements.items()
    }
    canonical = _canonical_payload(
        certificate, safe_measurements, failures, envelope, candidate_envelope
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return CertificateResult(
        passed=not failures,
        failures=tuple(sorted(set(failures))),
        measurements=safe_measurements,
        certificate_sha256=digest,
        canonical_payload=canonical,
    )
