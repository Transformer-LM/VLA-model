from math import ceil

def ls(es, ys):
    return sum(e*y for e, y in zip(es, ys)) / sum(e*e for e in es)

def ode(e):
    z = 0.2
    for _ in range(20):
        z += 0.025 * (z*z + (1+z)*e)
    return z

# Literal B e (flow velocity, dim 3) versus r* (DINO residual, dim 4).
try:
    assert len([.1, .2, .3]) == len([.4, .5, .6, .7])
except AssertionError:
    print("UNIT_SHAPE_ERROR", 3, 4)

# Donor shuffling: centered donors collapse; constant donors let B(x) encode targets.
b0 = ls([-1., 1.], [2., 2.])
print("DONOR_CENTERED", b0, [b0*-1, b0*1], "mse", 4.0)
for name, ys in [("k1", [2., 2.]), ("k2", [-3., -3.])]:
    b = ls([1., 1.], ys)
    print("DONOR_CONSTANT", name, b, [b, b])

# Full B(x)e contains the simpler candidate correction u(x)*(w^T e).
e = [1., -.5]
u = [2., -1.]
full = [2.*e[0], -1.*e[0]]
naive = [x*e[0] for x in u]
print("NAIVE", full, naive, "divergence", max(abs(a-b) for a,b in zip(full,naive)))

# Same support/contact label does not determine response sign.
print("SAME_CONTACT", "transported", [1., 1.], "oracle", [1., -1.])

# Pointwise odd additive velocity does not make a nonlinear ODE terminal map odd.
z0, zp, zm = ode(0.), ode(.4), ode(-.4)
print("ODE", z0, zp, zm, "oddness_defect", (zp-z0)+(zm-z0))

# At n=5 and alpha=.1, the finite-sample split-conformal index is n+1.
n, alpha = 5, .1
idx = ceil((n+1)*(1-alpha))
print("CONFORMAL", "index", idx, "threshold", "inf" if idx > n else "finite")
print("DEGENERATE", "single donor is not mismatched; empty calibration leaves thresholds undefined")
