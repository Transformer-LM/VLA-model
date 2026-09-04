from math import isclose


def anchor(points, attention):
    if len(points) != len(attention) or not points:
        raise ValueError("attention requires a non-empty point set of matching length")
    if not isclose(sum(attention), 1.0, abs_tol=1e-12):
        raise ValueError("attention must be normalized")
    return sum(p * w for p, w in zip(points, attention))


target_t0 = [0.0, 0.1, 0.2]
reference_t0 = [1.0, 1.1, 1.2]
token_attention = [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]
stored_target_anchors = [anchor(target_t0, a) for a in token_attention]
stored_reference_anchors = [anchor(reference_t0, a) for a in token_attention]

# The first chunk translates the target by +0.4 m. Step 7 retains the once-compiled Z.
translation = 0.4
target_t1 = [p + translation for p in target_t0]
current_second_anchor = anchor(target_t1, token_attention[1])
stale_second_anchor = stored_target_anchors[1]

# A fair naive has the same current observation and relation, the same two-chunk
# budget, and no compiler/swap head: for this 1-D relation it directly orders the
# target extrema. On the initial instance it makes the same two contact decisions.
naive_initial_anchors = [min(target_t0), max(target_t0)]
naive_current_second_anchor = max(target_t1)

# Architectural counterexample to "changing a token ... therefore [changes] action":
# a permitted zero conditioning projection makes both actions identical.
def toy_action(base_action, conditioning_scale, token_value):
    return base_action + conditioning_scale * token_value


action_z0 = toy_action(0.25, 0.0, 0.0)
action_z1 = toy_action(0.25, 0.0, 2.0)

# Same-relation, same-terminal-pose swap pairs do not rule out identity lookup.
pair_to_program = {("cup", "rack"): "left_then_align", ("mug", "peg"): "right_then_align"}
swap_examples = [
    (("cup", "rack"), "left_then_align", 1),
    (("cup", "rack"), "right_then_align", 0),
    (("mug", "peg"), "right_then_align", 1),
    (("mug", "peg"), "left_then_align", 0),
]
identity_correct = sum(int((pair_to_program[pair] == program) == bool(label)) for pair, program, label in swap_examples)

try:
    anchor([], [])
    empty_behavior = "unexpected-success"
except Exception as exc:
    empty_behavior = f"{type(exc).__name__}: {exc}"

try:
    [][0]
    k0_behavior = "unexpected-success"
except Exception as exc:
    k0_behavior = f"{type(exc).__name__}: {exc}"

tau_adv = 0.5
tie_advances = 0.5 > tau_adv
stall_probs = [0.4] * 12
advances_in_12_chunks = sum(prob > tau_adv for prob in stall_probs)

identical_points = [0.5, 0.5, 0.5]
identical_anchor_first = anchor(identical_points, [1.0, 0.0, 0.0])
identical_anchor_last = anchor(identical_points, [0.0, 0.0, 1.0])

print(f"stored_target_anchors={stored_target_anchors}")
print(f"stored_reference_anchors={stored_reference_anchors}")
print(f"target_after_first_chunk={target_t1}")
print(f"second_anchor_stored={stale_second_anchor:.3f}")
print(f"second_anchor_current={current_second_anchor:.3f}")
print(f"stale_anchor_error={stale_second_anchor - current_second_anchor:.3f}")
print(f"naive_initial_anchors={naive_initial_anchors}")
print(f"initial_program_vs_naive_max_abs_diff={max(abs(a-b) for a,b in zip(stored_target_anchors, naive_initial_anchors)):.3f}")
print(f"naive_current_second_anchor={naive_current_second_anchor:.3f}")
print(f"changed_token_actions=({action_z0:.3f},{action_z1:.3f}), action_difference={action_z1-action_z0:.3f}")
print(f"identity_swap_accuracy={identity_correct / len(swap_examples):.3f}")
print(f"empty_pointmap={empty_behavior}")
print(f"k0_program={k0_behavior}")
print(f"threshold_tie_advances={tie_advances}")
print(f"advances_in_12_chunks_below_threshold={advances_in_12_chunks}")
print(f"identical_point_anchor_difference={identical_anchor_first-identical_anchor_last:.3f}")
