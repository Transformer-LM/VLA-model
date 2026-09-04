"""Stdlib-only Phase 2.3 dry-run for the OddFlow candidate."""

from math import ceil


def dot(row, vector):
    return sum(a * b for a, b in zip(row, vector))


def matvec(matrix, vector):
    return [dot(row, vector) for row in matrix]


def euler(e, steps=20, dt=0.025):
    """Nonlinear nominal field plus state-conditioned residual-linear term."""
    z = 0.2
    for _ in range(steps):
        v_base = z * z
        b_of_z = 1.0 + z
        z += dt * (v_base + b_of_z * e)
    return z


def scalar_least_squares(es, targets):
    denom = sum(e * e for e in es)
    return sum(e * y for e, y in zip(es, targets)) / denom


# A post-transition residual source and two candidates.
e = [1.0, -0.5]
d_act = [0.2, 0.6]
q_act = 0.4
q_mode = [0.9, 0.8]
q_mode_min = 0.7
support = [int(d <= q_act and qm >= q_mode_min) for d, qm in zip(d_act, q_mode)]
banks = [
    [[2.0, 0.0], [0.0, 1.0]],
    [[-1.0, 0.0], [0.0, 3.0]],
]
delta_v = [[s * x for x in matvec(bank, e)] for s, bank in zip(support, banks)]
delta_zero = [[s * x for x in matvec(bank, [0.0, 0.0])] for s, bank in zip(support, banks)]
delta_negative_same_state = [
    [s * x for x in matvec(bank, [-v for v in e])] for s, bank in zip(support, banks)
]

print("T2 support", support)
print("T2 delta_v", delta_v)
print("T2 delta_zero", delta_zero)
print("T2 delta_negative_same_state", delta_negative_same_state)

# Literal direct supervision cannot compare flow velocity dimension 3 to DINO target dimension 4.
flow_velocity = [0.1, 0.2, 0.3]
dino_future_target = [0.4, 0.5, 0.6, 0.7]
try:
    assert len(flow_velocity) == len(dino_future_target)
except AssertionError:
    print(
        "UNIT_SHAPE_ERROR",
        f"flow_velocity_len={len(flow_velocity)}",
        f"dino_target_len={len(dino_future_target)}",
    )

# Donor-shuffle reading A: candidate target stays fixed while residual donors are shuffled.
# Centered donors make the least-squares operator collapse to zero.
centered_donors = [-1.0, 1.0]
fixed_candidate_target = [2.0, 2.0]
b_centered = scalar_least_squares(centered_donors, fixed_candidate_target)
print(
    "DONOR_CENTERED",
    f"B={b_centered:.6f}",
    f"predictions={[b_centered * x for x in centered_donors]}",
    f"mse={sum((b_centered*x-y)**2 for x,y in zip(centered_donors,fixed_candidate_target))/2:.6f}",
)

# Identical/nonzero-mean donors let B(candidate) encode an arbitrary candidate target perfectly.
constant_donors = [1.0, 1.0]
candidate_targets = {"k1": [2.0, 2.0], "k2": [-3.0, -3.0]}
for candidate, targets in candidate_targets.items():
    b_candidate = scalar_least_squares(constant_donors, targets)
    print(
        "DONOR_CONSTANT",
        candidate,
        f"B={b_candidate:.6f}",
        f"predictions={[b_candidate * x for x in constant_donors]}",
    )

# A rank-one candidate correction u(x)*(w^T e) is inside the advertised B(x)e class.
w = [1.0, 0.0]
candidate_u = {"k1": [2.0, -1.0], "k2": [-3.0, 4.0]}
for candidate, u in candidate_u.items():
    scalar = dot(w, e)
    rank_one = [value * scalar for value in u]
    print("RANK_ONE_BYPASS", candidate, f"wTe={scalar:.6f}", f"correction={rank_one}")

full_k1 = matvec([[2.0, 0.0], [-1.0, 0.0]], e)
naive_k1 = [value * dot(w, e) for value in candidate_u["k1"]]
print(
    "NAIVE_COMPARISON",
    f"full={full_k1}",
    f"naive={naive_k1}",
    f"max_abs_divergence={max(abs(a-b) for a,b in zip(full_k1,naive_k1)):.6f}",
)

# Same action-distance support and same contact label do not determine response sign/scale.
same_contact = [True, True]
within_action_support = [True, True]
oracle_response_jacobian = [1.0, -1.0]
source_residual_scalar = 1.0
transported_as_source = [source_residual_scalar, source_residual_scalar]
oracle_response = [j * source_residual_scalar for j in oracle_response_jacobian]
print(
    "SAME_CONTACT_COUNTEREXAMPLE",
    f"same_contact={same_contact}",
    f"within_support={within_action_support}",
    f"transported={transported_as_source}",
    f"oracle={oracle_response}",
)

# Pointwise oddness at a fixed z does not imply terminal oddness through a nonlinear ODE.
z_zero = euler(0.0)
z_plus = euler(0.4)
z_minus = euler(-0.4)
dev_plus = z_plus - z_zero
dev_minus = z_minus - z_zero
print(
    "ODE_ODDNESS",
    f"z0={z_zero:.9f}",
    f"zplus={z_plus:.9f}",
    f"zminus={z_minus:.9f}",
    f"dev_plus={dev_plus:.9f}",
    f"dev_minus={dev_minus:.9f}",
    f"oddness_defect={dev_plus + dev_minus:.9f}",
)

# Split-conformal threshold semantics and small/empty calibration edges.
scores = [0.1, 0.2, 0.3, 0.4, 0.5]
alpha = 0.10
raw_index = ceil((len(scores) + 1) * (1 - alpha))
threshold = float("inf") if raw_index > len(scores) else sorted(scores)[raw_index - 1]
print("CONFORMAL_SMALL_N", f"n={len(scores)}", f"index={raw_index}", f"threshold={threshold}")

calibration_options = [
    {"alpha": 0.05, "admitted": 1, "total": 100, "false": 0},
    {"alpha": 0.10, "admitted": 50, "total": 100, "false": 5},
    {"alpha": 0.20, "admitted": 80, "total": 100, "false": 12},
]
chosen = min(
    (o for o in calibration_options if o["admitted"] > 0),
    key=lambda o: o["false"] / o["admitted"],
)
print(
    "NONZERO_COVERAGE_SELECTION",
    f"alpha={chosen['alpha']}",
    f"coverage={chosen['admitted']/chosen['total']:.3f}",
    f"false_admission={chosen['false']/chosen['admitted']:.3f}",
)

# Degenerate probes.
print("DEGENERATE empty_candidates -> fallback_replan (step 8)")
print("DEGENERATE all_rejected ->", [0, 0], "then fallback_replan")
print("DEGENERATE ties_at_threshold -> admitted_by_<=_and_>=")
print("DEGENERATE single_donor_batch -> shuffle_is_factual_not_mismatched")
print("DEGENERATE empty_calibration -> q_act_and_q_mode_min_undefined_as_written")
