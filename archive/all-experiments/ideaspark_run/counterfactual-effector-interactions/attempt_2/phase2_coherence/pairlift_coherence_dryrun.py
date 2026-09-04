from itertools import product


EPS = 0.10
R = 0.20
K = 4
SEED_OFFSETS = (-0.006, -0.002, 0.002, 0.006)
HOLD = (0.20, 0.80)
ACTION0 = (0.60, 0.40)


def clip(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def action(delta):
    return tuple(
        clip(h + (1.0 + shift) * (a0 - h))
        for h, a0, shift in zip(HOLD, ACTION0, delta)
    )


def expected_score(delta, interaction):
    x, y = delta
    return 0.5 + 0.03 * x + 0.02 * y - 0.5 * x * x - 0.5 * y * y + interaction * x * y


def sample_mean(delta, interaction):
    values = [expected_score(delta, interaction) + noise for noise in SEED_OFFSETS]
    return sum(values) / K


def estimate(interaction):
    q0 = sample_mean((0.0, 0.0), interaction)
    qp1 = sample_mean((EPS, 0.0), interaction)
    qm1 = sample_mean((-EPS, 0.0), interaction)
    qp2 = sample_mean((0.0, EPS), interaction)
    qm2 = sample_mean((0.0, -EPS), interaction)
    m1 = (qp1 - qm1) / (2.0 * EPS)
    m2 = (qp2 - qm2) / (2.0 * EPS)
    d1 = (qp1 - 2.0 * q0 + qm1) / (EPS * EPS)
    d2 = (qp2 - 2.0 * q0 + qm2) / (EPS * EPS)
    joint = {
        (s1, s2): sample_mean((s1 * EPS, s2 * EPS), interaction)
        for s1, s2 in product((-1.0, 1.0), repeat=2)
    }
    i12 = (
        joint[(1.0, 1.0)]
        - joint[(1.0, -1.0)]
        - joint[(-1.0, 1.0)]
        + joint[(-1.0, -1.0)]
    ) / (4.0 * EPS * EPS)
    return q0, (m1, m2), (d1, d2), i12, (qp1, qm1, qp2, qm2), joint


def surrogate(point, q0, m, d, interaction):
    x, y = point
    return q0 + m[0] * x + m[1] * y + 0.5 * d[0] * x * x + 0.5 * d[1] * y * y + interaction * x * y


def exact_box_qp(q0, m, d, interaction):
    candidates = {(0.0, 0.0)}
    for x in (-R, R):
        for y in (-R, R):
            candidates.add((x, y))
        if abs(d[1]) > 1e-12:
            y = -(m[1] + interaction * x) / d[1]
            if -R <= y <= R:
                candidates.add((x, y))
    for y in (-R, R):
        if abs(d[0]) > 1e-12:
            x = -(m[0] + interaction * y) / d[0]
            if -R <= x <= R:
                candidates.add((x, y))
    determinant = d[0] * d[1] - interaction * interaction
    if abs(determinant) > 1e-12:
        x = (-d[1] * m[0] + interaction * m[1]) / determinant
        y = (interaction * m[0] - d[0] * m[1]) / determinant
        if -R <= x <= R and -R <= y <= R:
            candidates.add((x, y))
    # Deterministic lexicographic tie break after maximizing the score.
    return max(sorted(candidates), key=lambda p: surrogate(p, q0, m, d, interaction))


def dense_grid_best(q0, m, d, interaction):
    values = [(-R + i * 0.001, -R + j * 0.001) for i in range(401) for j in range(401)]
    return max(values, key=lambda p: surrogate(p, q0, m, d, interaction))


records = {}
for label, true_i in (("Q_plus", 1.5), ("Q_minus", -1.5)):
    q0, m, d, fitted_i, axes, joint = estimate(true_i)
    pairlift = exact_box_qp(q0, m, d, fitted_i)
    axis_proposal = exact_box_qp(q0, m, d, 0.0)
    grid = dense_grid_best(q0, m, d, fitted_i)
    pair_score = sample_mean(pairlift, true_i)
    axis_score = sample_mean(axis_proposal, true_i)
    # Fair deployment baseline: it may use the same final joint verification
    # that PairLift uses, although it cannot use that one score to search all
    # alternative joint signs.
    axis_executed = axis_proposal if axis_score > q0 else (0.0, 0.0)
    pair_executed = pairlift if pair_score > q0 else (0.0, 0.0)
    records[label] = {
        "q0": q0,
        "m": m,
        "d": d,
        "I": fitted_i,
        "axes": axes,
        "pairlift": pairlift,
        "pairlift_action": action(pairlift),
        "pairlift_score": pair_score,
        "pairlift_executed": pair_executed,
        "axis_proposal": axis_proposal,
        "axis_score": axis_score,
        "axis_executed": axis_executed,
        "dense_grid": grid,
        "analytic_grid_gap": abs(surrogate(pairlift, q0, m, d, fitted_i) - surrogate(grid, q0, m, d, fitted_i)),
    }

for label, record in records.items():
    print(label, {key: (tuple(round(x, 6) for x in value) if isinstance(value, tuple) else round(value, 6) if isinstance(value, float) else value) for key, value in record.items()})

print("axis_restrictions_identical=", records["Q_plus"]["axes"] == records["Q_minus"]["axes"])
print("axis_proposals_identical=", records["Q_plus"]["axis_proposal"] == records["Q_minus"]["axis_proposal"])
print("axis_postverify_actions_identical=", records["Q_plus"]["axis_executed"] == records["Q_minus"]["axis_executed"])
print("pairlift_actions_differ=", records["Q_plus"]["pairlift"] != records["Q_minus"]["pairlift"])
print("all_pairlift_actions_in_native_box=", all(0.0 <= coordinate <= 1.0 for record in records.values() for coordinate in record["pairlift_action"]))

# Boundary/hold probe: positive nominal scaling saturates at the native box.
boundary_h, boundary_a0, boundary_delta = 0.2, 1.0, 0.2
raw_boundary = boundary_h + (1.0 + boundary_delta) * (boundary_a0 - boundary_h)
print("boundary_raw_and_clipped=", round(raw_boundary, 6), round(clip(raw_boundary), 6))
print("zero_delta_recovers_a0=", action((0.0, 0.0)) == ACTION0)

# Break the unqualified claim that adding any nonzero c*x*y changes the best
# joint edit: a corner-dominated base response keeps the same maximizer.
base_corner = exact_box_qp(0.5, (1.0, 1.0), (0.0, 0.0), 0.0)
small_interaction_corner = exact_box_qp(0.5, (1.0, 1.0), (0.0, 0.0), 0.01)
print("small_I_changes_argmax=", base_corner != small_interaction_corner, base_corner, small_interaction_corner)
