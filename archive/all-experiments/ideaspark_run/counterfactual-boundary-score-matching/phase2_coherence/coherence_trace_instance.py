import math


def masks_from_violation(v):
    first = next((i for i, flag in enumerate(v) if flag), None)
    if first is None:
        return [], [], []
    last = first
    while last + 1 < len(v) and v[last + 1]:
        last += 1
    p = [i for i in range(first)]
    m = [i for i in range(first, last + 1)]
    s = [i for i in range(last + 1, len(v))]
    return p, m, s


def denoising_errors(theta, action):
    return [(theta * value) ** 2 for value in action]


def score(theta, action, mask):
    errors = denoising_errors(theta, action)
    return -sum(errors[i] for i in mask) / len(mask)


def delta_score(theta, theta0, action, mask):
    return score(theta, action, mask) - score(theta0, action, mask)


def margin(theta, theta0, positive, invalid, mask):
    return delta_score(theta, theta0, positive, mask) - delta_score(theta, theta0, invalid, mask)


def logistic_loss(value):
    return math.log1p(math.exp(-value))


def centered_grad(function, value, h=1e-6):
    return (function(value + h) - function(value - h)) / (2.0 * h)


theta0 = 0.5
learning_rate = 0.1
beta = 1.0
g_plus = 1.0
g_minus = 0.9
delta_g = g_minus - g_plus
a0 = [0.0, 1.0, 0.0]
p1 = [1.0, 0.0, 0.0]
p2 = [2.0, 0.0, 0.0]
violation = [False, True, False]
p_mask, m_mask, s_mask = masks_from_violation(violation)

errors = denoising_errors(theta0, a0)
e_p = sum(errors[i] for i in p_mask)
e_m = sum(errors[i] for i in m_mask)
e_s = sum(errors[i] for i in s_mask)
e_full = sum(errors)

masked_loss = lambda theta: logistic_loss(beta * margin(theta, theta0, p1, a0, m_mask))
full_mask = list(range(len(a0)))
naive_loss = lambda theta: logistic_loss(beta * margin(theta, theta0, p1, a0, full_mask))

masked_grad = centered_grad(masked_loss, theta0)
naive_grad = centered_grad(naive_loss, theta0)
theta_masked = theta0 - learning_rate * masked_grad
theta_naive = theta0 - learning_rate * naive_grad

def complement_distillation(theta):
    complement = p_mask + s_mask
    compared = [a0, p1]
    terms = []
    for action in compared:
        for index in complement:
            terms.append(((theta * action[index]) - (theta0 * action[index])) ** 2)
    return sum(terms) / len(terms)


l_out_at_init = complement_distillation(theta0)
l_out_grad_numeric = centered_grad(complement_distillation, theta0)
# Analytic derivative of mean((theta - theta0)^2 * a_t^2) at theta=theta0.
l_out_grad_at_init = 0.0
try:
    lambda_out_ratio = 1.0 / abs(l_out_grad_at_init)
except ZeroDivisionError:
    lambda_out_ratio = "division_by_zero"

alt_losses = {
    "p1": sum(denoising_errors(theta0, p1)) / len(p1),
    "p2": sum(denoising_errors(theta0, p2)) / len(p2),
}

print(f"S1 g_plus={g_plus:.1f} g_minus={g_minus:.1f} delta_g={delta_g:.1f}")
print(f"S2 violation={violation} P={p_mask} M={m_mask} S={s_mask}")
print(f"S2 decomposition E_full={e_full:.6f} E_P+E_M+E_S={e_p + e_m + e_s:.6f} parts=({e_p:.6f},{e_m:.6f},{e_s:.6f})")
print(f"S3 roster p1={p1} p2={p2}")
print(f"S4 batch_shape actions=3x1 roster_size=2 noise_draws=1")
print(f"S5 margin_at_init={margin(theta0, theta0, p1, a0, m_mask):.6f} masked_loss={masked_loss(theta0):.6f} masked_grad={masked_grad:.6f} theta_after={theta_masked:.6f}")
print(f"S5 complement_prediction_p1_t0_before={theta0 * p1[0]:.6f} after={theta_masked * p1[0]:.6f} drift={abs((theta_masked - theta0) * p1[0]):.6f}")
print(f"S5 masked_positive_scores_p1={score(theta_masked, p1, m_mask):.6f} p2={score(theta_masked, p2, m_mask):.6f}")
print(f"S6 L_out_at_init={l_out_at_init:.6f} analytic_grad_L_out_at_init={l_out_grad_at_init:.6f} numeric_check={l_out_grad_numeric:.3e} lambda_out_gradient_match={lambda_out_ratio}")
print(f"S6 full_chunk_alt_losses={alt_losses} max_mode={max(alt_losses, key=alt_losses.get)}")
print(f"S7 zero_gap_std_beta=1/0 -> division_by_zero")
print(f"S8 panel_proxy complement_drift={abs((theta_masked - theta0) * p1[0]):.6f} roster_modes=2")
print(f"S9 mask_permutation_to_t0 margin_at_init={margin(theta0, theta0, p1, a0, [0]):.6f}")
print(f"T5 naive_full_loss={naive_loss(theta0):.6f} naive_grad={naive_grad:.6f} theta_after={theta_naive:.6f} candidate_minus_naive_update={theta_masked - theta_naive:.6f}")
