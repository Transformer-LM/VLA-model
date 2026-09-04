import math


def centered(values):
    mean = sum(values) / len(values)
    return [v - mean for v in values]


def pair_targets(values):
    return {(i, j): values[i] - values[j]
            for i in range(len(values))
            for j in range(len(values)) if i != j}


def pair_loss(corrections, targets):
    return sum(((corrections[i] - corrections[j]) - target) ** 2
               for (i, j), target in targets.items())


def conformal_quantile(scores, alpha):
    rank = math.ceil((len(scores) + 1) * (1 - alpha))
    if rank > len(scores):
        return math.inf, rank
    return sorted(scores)[rank - 1], rank


def robust_decision(base, corrections, width, q):
    intervals = {}
    lower_by_candidate = []
    for i in range(len(base)):
        lowers = []
        for j in range(len(base)):
            if i == j:
                continue
            center = (base[i] - base[j]) + (corrections[i] - corrections[j])
            intervals[(i, j)] = (center - width - q, center + width + q)
            lowers.append(intervals[(i, j)][0])
        lower_by_candidate.append(min(lowers))
    margin = max(lower_by_candidate)
    winner = max(range(len(base)), key=lambda i: (lower_by_candidate[i], -i))
    return intervals, lower_by_candidate, margin, winner if margin > 0 else None


# Minimal same-snapshot training bundle.
s0_train = [0.55, 0.45, 0.25]
y_train = [0.0, 1.0, 0.0]
u_direct = [y - s for y, s in zip(y_train, s0_train)]
c_direct = centered(u_direct)
r_pair = pair_targets(u_direct)
max_pair_equivalence_error = max(
    abs(r_pair[i, j] - (c_direct[i] - c_direct[j])) for i, j in r_pair
)

# A head with zero dependence on e_t is an admissible zero-loss witness.
loss_if_e_minus_7 = pair_loss(c_direct, r_pair)
loss_if_e_plus_11 = pair_loss(c_direct, r_pair)

# Bundle-level split conformal example, after alpha is fixed elsewhere.
calibration_scores = [
    0.01, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06,
    0.065, 0.07, 0.075, 0.08, 0.085, 0.09, 0.095, 0.10, 0.11, 0.12,
]
q_alpha, q_rank = conformal_quantile(calibration_scores, 0.10)

# Deployment bundle. The direct centered scorer and quotient scorer use identical c.
s0_test = [0.55, 0.45, 0.25]
c_test = [-0.05, 0.10, -0.05]
intervals_q, lowers_q, margin_q, selected_q = robust_decision(
    s0_test, c_test, 0.03, q_alpha
)
intervals_direct, lowers_direct, margin_direct, selected_direct = robust_decision(
    s0_test, c_test, 0.03, q_alpha
)

# Boundary-unit probe: clipping marginal scores disagrees with the un-clipped D center.
s0_boundary = [0.95, 0.05]
c_boundary = [0.20, -0.20]
clipped = [min(1.0, max(0.0, s + c)) for s, c in zip(s0_boundary, c_boundary)]
clipped_difference = clipped[0] - clipped[1]
unclipped_pair_center = ((s0_boundary[0] - s0_boundary[1])
                         + (c_boundary[0] - c_boundary[1]))

print("u_direct=", [round(x, 6) for x in u_direct])
print("c_direct_centered=", [round(x, 6) for x in c_direct],
      "mean=", round(sum(c_direct) / len(c_direct), 12))
print("max_pair_equivalence_error=", max_pair_equivalence_error)
print("pair_loss_if_e=-7=", loss_if_e_minus_7)
print("pair_loss_if_e=+11=", loss_if_e_plus_11)
print("q_rank=", q_rank, "q_alpha=", q_alpha)
print("D01=", tuple(round(x, 6) for x in intervals_q[0, 1]))
print("lower_by_candidate=", [round(x, 6) for x in lowers_q],
      "M_t=", round(margin_q, 6), "selected=", selected_q)
print("direct_vs_quotient_same_intervals=", intervals_direct == intervals_q)
print("direct_vs_quotient_same_M=", margin_direct == margin_q,
      "same_selected=", selected_direct == selected_q)
print("clipped_difference=", clipped_difference,
      "unclipped_D_center=", unclipped_pair_center,
      "mismatch=", unclipped_pair_center - clipped_difference)
try:
    min([])
except ValueError as exc:
    print("K1_min_over_empty=", type(exc).__name__, str(exc))

# Remaining T3 probes.
try:
    robust_decision([], [], 0.03, q_alpha)
except ValueError as exc:
    print("K0_empty_bundle=", type(exc).__name__, str(exc))

identical_intervals, identical_lowers, identical_margin, identical_selected = robust_decision(
    [0.5, 0.5, 0.5], [0.0, 0.0, 0.0], 0.03, q_alpha
)
print("all_identical_lowers=", [round(x, 6) for x in identical_lowers],
      "M_t=", round(identical_margin, 6), "selected=", identical_selected)

_, tie_lowers, tie_margin, tie_selected = robust_decision(
    [0.5, 0.5], [0.0, 0.0], 0.0, 0.0
)
print("exact_threshold_tie_lowers=", tie_lowers,
      "M_t=", tie_margin, "selected=", tie_selected)

base16 = [i / 20.0 for i in range(16)]
c16 = [0.0] * 16
intervals16, lowers16, margin16, selected16 = robust_decision(base16, c16, 0.0, 0.0)
print("K16_ordered_pairs=", len(intervals16),
      "M_t=", round(margin16, 6), "selected=", selected16)

try:
    _ = (0.2 - 0.1) / 0.0
except ZeroDivisionError as exc:
    print("zero_sigma_p=", type(exc).__name__, str(exc))
