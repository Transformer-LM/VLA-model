import math
import statistics


rho = 0.5
tasks = ["A", "A", "B"]
recorded_actions = [
    [[0.0], [0.0]],
    [[0.0], [0.0]],
    [[0.0], [0.0]],
]
source_actions = [
    [[0.0], [0.0]],
    [[0.0], [0.0]],
    [[0.0], [0.0]],
]
current_actions = [
    [[2.0], [2.0]],
    [[0.0], [0.0]],
    [[0.0], [0.0]],
]
scale = [1.0]
ell_source = [1.0, 1.0, 1.0]
ell_current = [0.0, 1.0, 2.0]


def divergence(policy_actions, logged_actions, scale_vector, prefix_len=None):
    pairs = list(zip(policy_actions, logged_actions))
    if prefix_len is not None:
        pairs = pairs[:prefix_len]
    squared = []
    for policy_chunk, logged_chunk in pairs:
        squared.append(
            sum(
                ((policy_value - logged_value) / scale_value) ** 2
                for policy_value, logged_value, scale_value in zip(
                    policy_chunk, logged_chunk, scale_vector
                )
            )
        )
    return sum(squared) / len(squared)


def coordinates(prefix_len, current_action_set=None):
    if current_action_set is None:
        current_action_set = current_actions
    d_current = [
        divergence(cur, logged, scale, prefix_len)
        for cur, logged in zip(current_action_set, recorded_actions)
    ]
    d_source = [
        divergence(src, logged, scale, prefix_len)
        for src, logged in zip(source_actions, recorded_actions)
    ]
    deltas = [max(0.0, dk - db) for dk, db in zip(d_current, d_source)]
    positives = [delta for delta in deltas if delta > 0.0]
    tau = statistics.median(positives) if positives else None
    c = [
        0.0 if tau is None else 1.0 - math.exp(-delta / tau)
        for delta in deltas
    ]
    h = [
        0.0 if ek == 0.0 and eb == 0.0 else ek / (ek + eb)
        for ek, eb in zip(ell_current, ell_source)
    ]
    repair = [
        0.0 if ek == 0.0 and eb == 0.0 else (eb - ek) / (eb + ek)
        for ek, eb in zip(ell_current, ell_source)
    ]
    r = [ci * hi for ci, hi in zip(c, h)]
    return d_current, d_source, deltas, tau, c, h, repair, r


def global_probabilities(priority):
    total = sum(priority)
    n = len(priority)
    if total == 0.0:
        return [1.0 / n] * n
    return [(1.0 - rho) / n + rho * value / total for value in priority]


def task_stratified_marginals(priority):
    unique_tasks = sorted(set(tasks))
    task_mass = 1.0 / len(unique_tasks)
    marginals = [0.0] * len(priority)
    conditionals = {}
    for task in unique_tasks:
        indices = [index for index, item_task in enumerate(tasks) if item_task == task]
        total = sum(priority[index] for index in indices)
        n = len(indices)
        if total == 0.0:
            probs = [1.0 / n] * n
        else:
            probs = [
                (1.0 - rho) / n + rho * priority[index] / total
                for index in indices
            ]
        conditionals[task] = probs
        for index, probability in zip(indices, probs):
            marginals[index] = task_mass * probability
    return conditionals, marginals


full = coordinates(prefix_len=2)
strict_preterminal = coordinates(prefix_len=1)
labels = [
    "D_current",
    "D_source",
    "positive_delta",
    "tau",
    "c",
    "h",
    "m",
    "r",
]
print("FULL_PREFIX_COORDINATES")
for label, value in zip(labels, full):
    print(label, value)
print("STRICT_PRETERMINAL_COORDINATES")
for label, value in zip(labels, strict_preterminal):
    print(label, value)

global_p = global_probabilities(full[-1])
task_conditionals, task_marginals = task_stratified_marginals(full[-1])
uniform_global = [1.0 / len(tasks)] * len(tasks)
uniform_task_marginals = [0.25, 0.25, 0.5]
print("GLOBAL_P", global_p, "SUM", sum(global_p))
print("TASK_CONDITIONAL_P", task_conditionals)
print("TASK_MARGINAL_P", task_marginals, "SUM", sum(task_marginals))
print("NAIVE_UNIFORM_GLOBAL", uniform_global)
print("NAIVE_UNIFORM_TASK_MARGINAL", uniform_task_marginals)
print(
    "TRACE_0_GLOBAL_DELTA_FROM_NAIVE",
    global_p[0] - uniform_global[0],
)
print(
    "TRACE_0_TASK_DELTA_FROM_NAIVE",
    task_marginals[0] - uniform_task_marginals[0],
)
print(
    "STRUCTURAL_ZERO_GATE",
    "c0=", full[4][0],
    "h0=", full[5][0],
    "r0=", full[7][0],
)

perturbed_actions = [
    [[2.0], [2.0]],
    [[1.0], [1.0]],
    [[0.0], [0.0]],
]
perturbed = coordinates(prefix_len=2, current_action_set=perturbed_actions)
perturbed_global_p = global_probabilities(perturbed[-1])
perturbed_conditionals, perturbed_task_marginals = task_stratified_marginals(
    perturbed[-1]
)
print("PERTURBED_R", perturbed[-1])
print("PERTURBED_GLOBAL_P", perturbed_global_p)
print("PERTURBED_TASK_CONDITIONAL_P", perturbed_conditionals)
print("PERTURBED_TASK_MARGINAL_P", perturbed_task_marginals)
print(
    "PERTURBED_TRACE_0_DELTAS",
    perturbed_global_p[0] - uniform_global[0],
    perturbed_task_marginals[0] - uniform_task_marginals[0],
)

all_identical_actions = [
    [[0.0], [0.0]],
    [[0.0], [0.0]],
    [[0.0], [0.0]],
]
print(
    "DEGENERATE_ALL_IDENTICAL_C",
    coordinates(prefix_len=2, current_action_set=all_identical_actions)[4],
)
print("DEGENERATE_TIE_AT_ZERO", "delta=0 -> c=0")
single_r = [0.0]
print("DEGENERATE_SINGLE_TRACE_P", global_probabilities(single_r))
print("DEGENERATE_EMPTY_LEDGER", "N=0 makes the written global formula undefined; Step 4 invokes the baseline branch")
print("DEGENERATE_MAXIMUM", "no maximum ledger size is declared; arithmetic stays defined but per-cycle work grows with N")
try:
    divergence([[0.0]], [[0.0]], [0.0])
except ZeroDivisionError as error:
    print("DEGENERATE_ZERO_IQR", type(error).__name__, str(error))
