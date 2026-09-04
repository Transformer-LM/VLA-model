import random


def interaction(cells):
    return 0.5 * ((cells["AA"] - cells["AB"]) + (cells["BB"] - cells["BA"]))


def recipient_outcome(recipient, action):
    required = {"A": -1, "B": 1}
    return int(action == required[recipient])


aware_actions = {"A": -1, "B": 1}
aware_cells = {
    recipient + source: recipient_outcome(recipient, aware_actions[source])
    for recipient in "AB"
    for source in "AB"
}
print("aware_cells", aware_cells, "I_MS", interaction(aware_cells))

blind_actions = {"A": -1, "B": -1}
blind_cells = {
    recipient + source: recipient_outcome(recipient, blind_actions[source])
    for recipient in "AB"
    for source in "AB"
}
print("blind_exact_cells", blind_cells, "I_MS", interaction(blind_cells))
print("blind_endpoint_scene_gap", 1 - 0)

# A non-geometry checkpoint mismatch changes a geometry-blind state-feedback action.
mismatched_state = {"A": -0.01, "B": 0.01}
mismatch_actions = {source: (-1 if mismatched_state[source] < 0 else 1) for source in "AB"}
mismatch_cells = {
    recipient + source: recipient_outcome(recipient, mismatch_actions[source])
    for recipient in "AB"
    for source in "AB"
}
print("blind_mismatched_state", mismatch_actions, mismatch_cells, "I_MS", interaction(mismatch_cells))

# Setting one seed once is not the same as resetting it before both queries.
rng = random.Random(1)
sequential_actions = {"A": (-1 if rng.random() < 0.5 else 1), "B": (-1 if rng.random() < 0.5 else 1)}
sequential_cells = {
    recipient + source: recipient_outcome(recipient, sequential_actions[source])
    for recipient in "AB"
    for source in "AB"
}
reset_actions = {}
for source in "AB":
    local_rng = random.Random(1)
    reset_actions[source] = -1 if local_rng.random() < 0.5 else 1
reset_cells = {
    recipient + source: recipient_outcome(recipient, reset_actions[source])
    for recipient in "AB"
    for source in "AB"
}
print("blind_sequential_rng", sequential_actions, "I_MS", interaction(sequential_cells))
print("blind_reset_rng", reset_actions, "I_MS", interaction(reset_cells))

# Carrying source-query policy cache into continuation can also create an own-source effect.
carried_cache_cells = {"AA": 1, "AB": 0, "BB": 1, "BA": 0}
fresh_continuation_cells = {"AA": 1, "AB": 1, "BB": 0, "BA": 0}
print("blind_carried_source_cache", carried_cache_cells, "I_MS", interaction(carried_cache_cells))
print("blind_fresh_continuation", fresh_continuation_cells, "I_MS", interaction(fresh_continuation_cells))

attempted, eligible = 4, 3
print("coverage", eligible / attempted, "excluded", attempted - eligible)
