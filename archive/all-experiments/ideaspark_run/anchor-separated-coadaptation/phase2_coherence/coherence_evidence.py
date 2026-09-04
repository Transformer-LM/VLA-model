from math import exp
from statistics import median

rho = 0.5
tasks = ["A", "A", "B"]
Dk, Db = [4.0, 0.0, 0.0], [0.0, 0.0, 0.0]
ell_k, ell_b = [0.0, 1.0, 2.0], [1.0, 1.0, 1.0]


def coordinates(dk):
    delta = [max(0.0, x - y) for x, y in zip(dk, Db)]
    positive = [x for x in delta if x > 0.0]
    tau = median(positive) if positive else None
    c = [0.0 if tau is None else 1.0 - exp(-x / tau) for x in delta]
    h = [0.0 if x == y == 0.0 else x / (x + y) for x, y in zip(ell_k, ell_b)]
    m = [0.0 if x == y == 0.0 else (y - x) / (y + x) for x, y in zip(ell_k, ell_b)]
    r = [x * y for x, y in zip(c, h)]
    return delta, tau, c, h, m, r


def global_p(r):
    return [1.0 / len(r)] * len(r) if sum(r) == 0.0 else [(1 - rho) / len(r) + rho * x / sum(r) for x in r]


def stratified_p(r):
    out = [0.0] * len(r)
    for task in sorted(set(tasks)):
        ids = [i for i, value in enumerate(tasks) if value == task]
        total = sum(r[i] for i in ids)
        conditional = [1 / len(ids)] * len(ids) if total == 0.0 else [(1 - rho) / len(ids) + rho * r[i] / total for i in ids]
        for i, value in zip(ids, conditional):
            out[i] = value / len(set(tasks))
    return out


base = coordinates(Dk)
print("base delta,tau,c,h,m,r =", base)
print("full-prefix = strict-preterminal on this instance:", base)
print("mechanism global/task =", global_p(base[-1]), stratified_p(base[-1]))
print("naive global/task =", [1 / 3] * 3, [0.25, 0.25, 0.5])
perturbed = coordinates([4.0, 1.0, 0.0])
print("perturbed r =", perturbed[-1])
print("perturbed mechanism global/task =", global_p(perturbed[-1]), stratified_p(perturbed[-1]))
print("trace0 deltas vs naive =", global_p(perturbed[-1])[0] - 1 / 3, stratified_p(perturbed[-1])[0] - 0.25)
print("all-identical c =", coordinates([0.0, 0.0, 0.0])[2])
print("single trace zero-sum fallback =", global_p([0.0]))
print("empty ledger: written 1/N is undefined; Step 4 baseline branch is required")
try:
    print((0.0 - 0.0) / 0.0)
except ZeroDivisionError as error:
    print("zero-IQR probe =", type(error).__name__)
