"""Phase-2.3 stdlib trace; 0=failure-free, 1=failure."""
from collections import defaultdict
import random

T = ("held", "aligned")

def act(prompt, q):
    q = dict(q)
    if prompt == "grasp": q["held"] = True
    if prompt == "align" and q["held"]: q["aligned"] = True
    return q

def common(schedule, H=4):
    q, i = {"held": False, "aligned": False}, 0
    for _ in range(H):
        if i >= len(schedule): return "UNDEFINED_NO_PHASE_TEXT"
        q = act(schedule[i], q)
        if i < len(T) and q[T[i]]: i += 1
        if q["held"] and q["aligned"]: return "SUCCESS"
    return "TIMEOUT"

def schedule_specific(schedule):
    q = {"held": False, "aligned": False}
    for prompt in schedule:
        q = act(prompt, q)  # one chunk then advance: a different transition rule
    return "SUCCESS" if q["held"] and q["aligned"] else "FAIL"

def rate(v): return sum(v) / len(v)

def score(cal, ev, order):
    xs = sorted(cal)
    star = {x: min(order, key=lambda s: (rate(cal[x][s]), order.index(s))) for x in xs}
    fix = min(order, key=lambda s: (sum(rate(cal[x][s]) for x in xs), order.index(s)))
    terms = [rate(ev[x][fix]) - rate(ev[x][star[x]]) for x in xs]
    return star, fix, sum(terms) / len(terms)

def permute(star, transform):
    groups = defaultdict(list)
    for x, t in transform.items(): groups[t].append(x)
    out = dict(star)
    for xs in groups.values():
        vals = [star[x] for x in xs]
        for x, v in zip(xs, vals[1:] + vals[:1]): out[x] = v
    return out

for name, s in {"ref": ("grasp","align"), "rev": ("align","grasp"),
                "short": ("grasp",), "extra": ("grasp","align","verify")}.items():
    print("schedule", name, "common=", common(s), "schedule_specific=", schedule_specific(s))

cal = {"A":{"s0":[0]*20,"s1":[1]*20}, "B":{"s0":[1]*20,"s1":[0]*20}}
ev  = {"A":{"s0":[0]*20,"s1":[1]*20}, "B":{"s0":[1]*20,"s1":[0]*20}}
star, fix, G = score(cal, ev, ["s0","s1"])
print("reversal", "star=", star, "fix=", fix, "G_E=", G)
flat = {x:{s:[0,1]*10 for s in ("s0","s1")} for x in ("A","B")}
print("flat-null", "star/fix/G_E=", score(flat, flat, ["s0","s1"]))
single = {x:{"s0":[0,1]*10} for x in ("A","B")}
print("singleton", "star/fix/G_E=", score(single, single, ["s0"]))
try: cal["C"]
except KeyError: print("heldout-C", "s_star(C)=UNDEFINED without C-specific calibration")
print("permute-unique", permute(star, {"A":"T_A","B":"T_B"}))
print("permute-shared", permute(star, {"A":"T","B":"T"}))
print("physical-reset", "same fiducial hash; hidden histories [0,1]; outcomes [1,0]")

rng, gs = random.Random(2305), []
for _ in range(10000):
    c, e = {}, {}
    for x in range(6):
        c[x], e[x] = {}, {}
        for s in ("s0","s1"):
            c[x][s] = [rng.random()<.5 for _ in range(20)]
            e[x][s] = [rng.random()<.5 for _ in range(20)]
    gs.append(score(c, e, ["s0","s1"])[2])
print("null-MC-instance-contingent", "mean_G_E=", round(sum(gs)/len(gs), 6))
