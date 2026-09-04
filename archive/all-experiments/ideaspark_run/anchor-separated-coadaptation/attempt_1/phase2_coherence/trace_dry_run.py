import math

# T2 instance: low-energy axis 0 is strongly amplifying; high-energy axis 1 is benign.
E = [[0.1, 1.2], [-0.1, -1.2], [0.1, 0.8], [-0.1, -0.8]]
axis_energy = [sum(row[j] ** 2 for row in E) for j in range(2)]
total_energy = sum(axis_energy)
order = sorted(range(2), key=lambda j: axis_energy[j], reverse=True)
alpha = 0.90
cum = 0.0
selected = []
for j in order:
    selected.append(j)
    cum += axis_energy[j]
    if cum / total_energy >= alpha:
        break

true_loop_gain = {0: 2.0, 1: -0.2}
A = [j for j in selected if true_loop_gain[j] > 0.0]
ordinary_update = 1.0
projected_update = 0.0 if A else ordinary_update
naive_ordinary_update = ordinary_update

# Literal Step 7: the already measured scalar g is not a function of a proposed update.
g_measured = 2.0
def g_literal(proposed_update):
    return g_measured

h = 1e-4
c_literal = (g_literal(ordinary_update + h) - g_literal(ordinary_update - h)) / (2 * h)
constraint_feasible = not (g_measured > 0.0 and c_literal == 0.0)

# The two defensible meanings of "centered difference" have incompatible scales.
rms = math.sqrt(total_energy / (len(E) * len(E[0])))
eta = 0.01 * rms
delta = 0.05
raw_policy_difference = 2 * eta
raw_physical_difference = 2 * delta * 2.0
g_raw = raw_policy_difference * raw_physical_difference
g_derivative = (raw_policy_difference / (2 * eta)) * (raw_physical_difference / (2 * delta))
g_raw_10x = (2 * (10 * eta)) * (2 * (10 * delta) * 2.0)

# Degenerate/boundary probes.
zero_energy = sum(x * x for row in [[0.0, 0.0], [0.0, 0.0]] for x in row)
base_action = 0.98
action_range = 2.0
eps_action = 0.05 * action_range

print(f"axis_energy={axis_energy}, fractions={[round(x/total_energy, 6) for x in axis_energy]}")
print(f"selected_axes={selected}, selected_gains={[true_loop_gain[j] for j in selected]}, A={A}")
print(f"mechanism_update={projected_update:.6f}, naive_ordinary_update={naive_ordinary_update:.6f}, divergence={projected_update-naive_ordinary_update:.6f}")
print(f"literal_g={g_measured:.6f}, c_literal={c_literal:.6f}, positive_gain_constraint_feasible={constraint_feasible}")
print(f"rms={rms:.6f}, eta={eta:.6f}, delta={delta:.6f}")
print(f"g_raw={g_raw:.9f}, g_raw_10x_each={g_raw_10x:.9f}, raw_scale_ratio={g_raw_10x/g_raw:.1f}")
print(f"g_central_derivative={g_derivative:.6f}")
print(f"zero_energy={zero_energy:.1f}, explained_fraction=undefined_0_over_0")
print(f"boundary_actions=({base_action-eps_action:.3f},{base_action+eps_action:.3f}), valid=[-1,1]")
