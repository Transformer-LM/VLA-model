from math import log

EPS = 1e-4
C_SAFE = 0.010
F_MAX = 5.0
TAU_F = -2.0
TAU_I = 2.0


def kl_bernoulli(p, q):
    return p * log(p / q) + (1 - p) * log((1 - p) / (1 - q))


def js_bernoulli(p, q):
    m = 0.5 * (p + q)
    return 0.5 * kl_bernoulli(p, m) + 0.5 * kl_bernoulli(q, m)


models = {
    "axial": {"F": {0: 0.9, 1: 0.1}, "I": {0: 0.1, 1: 0.9}},
    "lateral": {"F": {0: 0.6, 1: 0.4}, "I": {0: 0.4, 1: 0.6}},
}


def llr(probe_type, contact):
    p_i = models[probe_type]["I"][contact]
    p_f = models[probe_type]["F"][contact]
    return log((p_i + EPS) / (p_f + EPS))


def decision(score):
    if score >= TAU_I:
        return "block"
    if score <= TAU_F:
        return "release"
    return "defer"


visible_pointmap = ((0.0, 0.0, 0.0), (0.0, 0.02, 0.0))
visible_clearance = 0.020
safe_set = ["axial", "lateral"] if visible_clearance > C_SAFE else []
js = {t: js_bernoulli(models[t]["F"][1], models[t]["I"][1]) for t in safe_set}
chosen = max(safe_set, key=lambda t: (js[t], t))

print("PARAMS", {"c_safe_m": C_SAFE, "F_max_N": F_MAX, "tau_F": TAU_F, "tau_I": TAU_I})
print("MATCHED_P0", visible_pointmap)
print("U0_FOR_HIDDEN_CLEARANCES_25MM_AND_5MM", safe_set, "identical=", True)
print("JS", {k: round(v, 6) for k, v in js.items()}, "chosen=", chosen)

stable = {"feasible_pair": 0, "infeasible_pair": 1}
for pair, contact in stable.items():
    score = llr(chosen, contact)
    mechanism = decision(score)
    fair_naive = "release" if contact == 0 else "block"
    print(
        "STABLE",
        pair,
        "contact=", contact,
        "llr=", round(score, 6),
        "IFG=", mechanism,
        "same_transcript_fixed_probe_rule=", fair_naive,
    )

print("FAIR_NAIVE_DIVERGENCE", 0, "on both stable pairs")
print("PASSIVE_IDENTICAL_INPUT_DECISIONS", "must_be_equal")
print("PASSIVE_RELEASE_ALL", {"coverage": 1.0, "unsafe_rate": 0.5})
print("IFG_STABLE_PAIRS", {"release_coverage": 0.5, "unsafe_rate_given_release": 0.0})

# The probe response is F-like, but the probe moves the object into an infeasible
# post-probe state. Step 7 scores the old/static hypothesis and Step 8 releases
# the executor in the new state.
state_before = "F"
contact = 0
state_after = "I"
score = llr("axial", contact)
print(
    "STATE_FLIP",
    {"H_before": state_before, "contact": contact, "H_after": state_after,
     "llr": round(score, 6), "decision_on_current_state": decision(score)},
)

# If successive responses are perfectly correlated repeats of one obstruction
# signal, multiplying marginal densities counts the same information three times.
one = llr("axial", 1)
candidate_sum = 3 * one
correct_joint = one
print(
    "DEPENDENT_REPEAT",
    {"candidate_sum_llr": round(candidate_sum, 6),
     "joint_llr_if_perfectly_correlated": round(correct_joint, 6),
     "overcount_factor": round(candidate_sum / correct_joint, 3)},
)

# Adding a dimensionless epsilon to a continuous density is unit-dependent.
p_f_mm, p_i_mm = 1e-5, 2e-5
llr_per_mm = log((p_i_mm + EPS) / (p_f_mm + EPS))
p_f_m, p_i_m = 1000 * p_f_mm, 1000 * p_i_mm
llr_per_m = log((p_i_m + EPS) / (p_f_m + EPS))
print(
    "DENSITY_UNIT_CHANGE",
    {"llr_per_mm_units": round(llr_per_mm, 6),
     "llr_per_m_units": round(llr_per_m, 6)},
)

# Oracle geometric feasibility does not equal frozen-executor safety.
oracle_labels = ["F", "F", "F", "F"]
executor_unsafe = [1, 1, 0, 0]
oracle_label_error = sum(label == "I" for label in oracle_labels) / len(oracle_labels)
downstream_risk = sum(executor_unsafe) / len(executor_unsafe)
print(
    "CALIBRATION_ESTIMAND_MISMATCH",
    {"oracle_infeasible_rate_among_releases": oracle_label_error,
     "frozen_executor_unsafe_rate_among_releases": downstream_risk},
)

# Exact representation matching blocks any passive separator. A tolerance-based
# reading permits a residual cue that perfectly reveals the label in this toy.
approx_features = {"F": +0.001, "I": -0.001}
approx_accuracy = sum((v > 0) == (k == "F") for k, v in approx_features.items()) / 2
print("MATCHED_READING", {"strict_passive_identifiable": False,
                           "tolerance_residual_classifier_accuracy": approx_accuracy})

print("DEGENERATE_EMPTY_U", "defer")
print("DEGENERATE_IDENTICAL_MODELS", {"JS": js_bernoulli(0.5, 0.5),
                                       "argmax": "tie_rule_unspecified"})
print("DEGENERATE_ZERO_EVIDENCE", {"I_0": 0.0, "decision": decision(0.0)})
