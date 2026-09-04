from statistics import mean

# A grammar can have finitely many productions yet an unbounded language.
generated = ["a" * depth + "b" for depth in range(6)]
print("finite-production grammar prefixes:", generated)
print("candidate count through depths 1..6:", [d for d in range(1, 7)])

# One simultaneous simulator step admits two unspecified event reductions.
sigma_contact_first = "contact>attach|H0"
sigma_attach_first = "attach>contact|H0"
target_feasible = {sigma_attach_first_first for sigma_attach_first_first in [sigma_attach_first]}
q_contact_first = int(sigma_contact_first not in target_feasible and bool(target_feasible))
q_attach_first = int(sigma_attach_first not in target_feasible and bool(target_feasible))
print("q under contact-first / attach-first:", q_contact_first, q_attach_first)

# Identical observables support incompatible causal explanations.
s_q0 = [1, 1, 1, 1]
s_q1 = [1, 0, 0, 1]
tcsg = mean(s_q0) - mean(s_q1)
print("observed TCSG in both causal worlds:", tcsg)
print("true switch effect, world A / world B:", 0.5, 0.0)
print("matched naive TCSG / mechanism TCSG:", tcsg, tcsg)

# Oracle receives the answer-bearing side information in this constructed tie.
truth = ["A", "B"]
ordinary = ["A", "A"]
oracle = truth
acc = lambda p: mean(int(a == b) for a, b in zip(p, truth))
print("ordinary / Oracle accuracy:", acc(ordinary), acc(oracle))
