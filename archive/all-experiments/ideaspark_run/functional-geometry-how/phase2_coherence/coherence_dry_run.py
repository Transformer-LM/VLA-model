"""Stdlib-only executable trace for IdeaSpark Phase 2.3."""

from collections import defaultdict
import json
import random


COMMON_TRANSITIONS = ("grasped", "aligned")


def executor_step(prompt, state):
    """A tiny frozen executor: prompt chooses an action; physics gates its effect."""
    state = dict(state)
    if prompt == "grasp":
        state["held"] = True
        action = "close_gripper"
    elif prompt == "align":
        action = "move_to_target"
        if state["held"]:
            state["aligned"] = True
    elif prompt == "verify":
        action = "hold"
    else:
        action = "unknown_prompt"
    return state, action


def run_common_transition_schedule(schedule, horizon=4):
    """Reading A: every schedule is indexed by one common predicate automaton."""
    state = {"held": False, "aligned": False}
    phase_index = 0
    trace = []
    for tick in range(horizon):
        if phase_index >= len(schedule):
            return {"status": "UNDEFINED_NO_PHASE_TEXT", "trace": trace, "state": state}
        prompt = schedule[phase_index]
        state, action = executor_step(prompt, state)
        trace.append((tick, phase_index, prompt, action, dict(state)))
        if phase_index < len(COMMON_TRANSITIONS):
            if state[COMMON_TRANSITIONS[phase_index].replace("grasped", "held")]:
                phase_index += 1
        if state["held"] and state["aligned"]:
            return {"status": "SUCCESS", "trace": trace, "state": state}
    return {"status": "TIMEOUT", "trace": trace, "state": state}


def run_schedule_specific_transitions(schedule, horizon=4):
    """Reading B: each phase advances after one action chunk (a different scheduler)."""
    state = {"held": False, "aligned": False}
    trace = []
    for tick, prompt in enumerate(schedule[:horizon]):
        state, action = executor_step(prompt, state)
        trace.append((tick, prompt, action, dict(state)))
        if state["held"] and state["aligned"]:
            return {"status": "SUCCESS", "trace": trace, "state": state}
    return {"status": "FAIL", "trace": trace, "state": state}


def rate(xs):
    return sum(xs) / len(xs)


def select_and_score(cal, ev, scaffold_order):
    pairs = sorted(cal)
    star = {}
    for pair in pairs:
        star[pair] = min(scaffold_order, key=lambda s: (rate(cal[pair][s]), scaffold_order.index(s)))
    fixed = min(
        scaffold_order,
        key=lambda s: (sum(rate(cal[p][s]) for p in pairs) / len(pairs), scaffold_order.index(s)),
    )
    terms = {
        p: rate(ev[p][fixed]) - rate(ev[p][star[p]])
        for p in pairs
    }
    return {"s_star": star, "s_fix": fixed, "per_pair_G": terms, "G_E": sum(terms.values()) / len(terms)}


def null_monte_carlo(repetitions=10000, n_pairs=6, n_cal=20, n_eval=20):
    """Contingent sanity check only: p(fail)=.5 for both schedules and all pairs."""
    rng = random.Random(2305)
    gs = []
    for _ in range(repetitions):
        cal, ev = {}, {}
        for p in range(n_pairs):
            cal[p], ev[p] = {}, {}
            for s in ("s0", "s1"):
                cal[p][s] = [int(rng.random() < 0.5) for _ in range(n_cal)]
                ev[p][s] = [int(rng.random() < 0.5) for _ in range(n_eval)]
        gs.append(select_and_score(cal, ev, ["s0", "s1"])["G_E"])
    mean = sum(gs) / repetitions
    return {"repetitions": repetitions, "mean_G_E": round(mean, 6)}


def permutation_within_strata(stars, transforms):
    groups = defaultdict(list)
    for pair, transform in transforms.items():
        groups[transform].append(pair)
    out = dict(stars)
    for members in groups.values():
        values = [stars[p] for p in members]
        values = values[1:] + values[:1]
        for p, value in zip(members, values):
            out[p] = value
    return out, {k: len(v) for k, v in groups.items()}


def main():
    schedules = {
        "reference": ("grasp", "align"),
        "reversed": ("align", "grasp"),
        "short": ("grasp",),
        "extra": ("grasp", "align", "verify"),
    }
    schedule_trace = {
        name: {
            "common_transition_reading": run_common_transition_schedule(s),
            "schedule_specific_reading": run_schedule_specific_transitions(s),
        }
        for name, s in schedules.items()
    }

    cal = {
        "A": {"s0": [0] * 20, "s1": [1] * 20},
        "B": {"s0": [1] * 20, "s1": [0] * 20},
    }
    ev = {
        "A": {"s0": [0] * 20, "s1": [1] * 20},
        "B": {"s0": [1] * 20, "s1": [0] * 20},
    }
    reversal = select_and_score(cal, ev, ["s0", "s1"])
    null = {
        p: {s: [0, 1] * 10 for s in ("s0", "s1")}
        for p in ("A", "B")
    }
    null_result = select_and_score(null, null, ["s0", "s1"])
    singleton_result = select_and_score(
        {"A": {"s0": [0, 1] * 10}, "B": {"s0": [1, 0] * 10}},
        {"A": {"s0": [0, 1] * 10}, "B": {"s0": [1, 0] * 10}},
        ["s0"],
    )

    heldout_error = None
    try:
        _ = cal["C"]
    except KeyError as exc:
        heldout_error = f"s_star(C) undefined without C-specific calibration outcomes: KeyError({exc})"

    unique_perm, unique_sizes = permutation_within_strata(
        reversal["s_star"], {"A": "T_A", "B": "T_B"}
    )
    shared_perm, shared_sizes = permutation_within_strata(
        reversal["s_star"], {"A": "T_shared", "B": "T_shared"}
    )

    physical_counterexample = {
        "observed_reset_hashes": ["pose=0.000|fixture=0.000"] * 2,
        "unobserved_controller_history": [0, 1],
        "same_scaffold_outcomes": [1, 0],
        "implication": "equal observed fiducials do not imply equal full physical reset state",
    }

    report = {
        "schedule_execution": schedule_trace,
        "reversal_tensor": reversal,
        "flat_null_tensor": null_result,
        "singleton": singleton_result,
        "heldout_composition": heldout_error,
        "terminal_transform_permutation": {
            "unique_strata": {"sizes": unique_sizes, "before": reversal["s_star"], "after": unique_perm},
            "shared_stratum": {"sizes": shared_sizes, "before": reversal["s_star"], "after": shared_perm},
        },
        "physical_reset_counterexample": physical_counterexample,
        "null_selection_sanity_check_instance_contingent": null_monte_carlo(),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
