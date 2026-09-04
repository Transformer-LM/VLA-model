from itertools import product


EPS = 0.2
LAMBDA_C = 1.0
R = 0.2
HOLD = (0.0, 0.0)
ACTION0 = (0.5, 0.5)


def score(alpha, interaction=0.6):
    """A valid [0,1] frozen FastWAM+q score on the tested points."""
    d1 = alpha[0] - 1.0
    d2 = alpha[1] - 1.0
    return 0.5 + 0.08 * d1 - 0.04 * d2 + interaction * d1 * d2


def solve_square(matrix, rhs):
    aug = [list(row) + [value] for row, value in zip(matrix, rhs)]
    n = len(aug)
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(aug[row][col]))
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        if abs(scale) < 1e-12:
            raise ValueError("rank deficient")
        aug[col] = [value / scale for value in aug[col]]
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            aug[row] = [a - factor * b for a, b in zip(aug[row], aug[col])]
    return [row[-1] for row in aug]


def clip(value, low, high):
    return max(low, min(high, value))


z_rows = list(product((-1.0, 1.0), repeat=2))
alphas = [(1.0 + EPS * z1, 1.0 + EPS * z2) for z1, z2 in z_rows]
y = [score(alpha) for alpha in alphas]
x = [[1.0, a1, a2, a1 * a2] for a1, a2 in alphas]
beta0, m1, m2, i12 = solve_square(x, y)
d_full = (m1 + i12, m2 + i12)

# Independently constructed, interaction-free baseline: spend the same four
# scores on central one-coordinate probes, estimate only the local gradient,
# and feed that gradient to the identical box/radius QP.
axis_scores = {
    "left_minus": score((1.0 - EPS, 1.0)),
    "left_plus": score((1.0 + EPS, 1.0)),
    "right_minus": score((1.0, 1.0 - EPS)),
    "right_plus": score((1.0, 1.0 + EPS)),
}
d_naive = (
    (axis_scores["left_plus"] - axis_scores["left_minus"]) / (2.0 * EPS),
    (axis_scores["right_plus"] - axis_scores["right_minus"]) / (2.0 * EPS),
)

# With h=0 and a0=0.5, the native [0,1] action box permits delta in [-1,1],
# so the radius r=0.2 is active and the separable QP solution is clip(d/lambda_c).
delta_full = tuple(clip(value / LAMBDA_C, -R, R) for value in d_full)
delta_naive = tuple(clip(value / LAMBDA_C, -R, R) for value in d_naive)
alpha_full = tuple(1.0 + value for value in delta_full)
alpha_naive = tuple(1.0 + value for value in delta_naive)
action_full = tuple(h + a * (a0 - h) for h, a0, a in zip(HOLD, ACTION0, alpha_full))
action_naive = tuple(h + a * (a0 - h) for h, a0, a in zip(HOLD, ACTION0, alpha_naive))
baseline_score = score((1.0, 1.0))
full_score = score(alpha_full)
naive_score = score(alpha_naive)

print("factorial_alphas=", alphas)
print("factorial_scores=", [round(value, 6) for value in y])
print("fitted_raw_coefficients=", tuple(round(v, 6) for v in (beta0, m1, m2, i12)))
print("candidate_d=", tuple(round(v, 6) for v in d_full))
print("naive_axis_scores=", {k: round(v, 6) for k, v in axis_scores.items()})
print("naive_d=", tuple(round(v, 6) for v in d_naive))
print("candidate_delta=", tuple(round(v, 6) for v in delta_full))
print("naive_delta=", tuple(round(v, 6) for v in delta_naive))
print("candidate_action=", tuple(round(v, 6) for v in action_full))
print("naive_action=", tuple(round(v, 6) for v in action_naive))
print("scores_baseline_candidate_naive=", tuple(round(v, 6) for v in (baseline_score, full_score, naive_score)))
print("candidate_accept=", full_score > baseline_score)
print("naive_accept=", naive_score > baseline_score)
print("interaction_is_nonzero=", i12 != 0.0)
max_update_difference = max(abs(a - b) for a, b in zip(delta_full, delta_naive))
print("max_update_difference=", f"{max_update_difference:.3e}")
print("updates_identical_to_1e-12=", max_update_difference < 1e-12)

# A boundary probe required by T3: the signed +epsilon row exceeds a native
# action upper bound when a0 is already at that bound and h is interior.
boundary_h = 0.0
boundary_a0 = 1.0
boundary_alpha_plus = 1.0 + EPS
boundary_action = boundary_h + boundary_alpha_plus * (boundary_a0 - boundary_h)
print("boundary_probe_action=", round(boundary_action, 6), "within_[0,1]=", 0.0 <= boundary_action <= 1.0)

# Parameter-count probe: p=14 groups require 106 unpenalized degree-two
# coefficients including the intercept, before a unique L2 projection exists.
p = 14
parameter_count = 1 + p + p * (p - 1) // 2
print("p14_degree2_parameter_count=", parameter_count)
