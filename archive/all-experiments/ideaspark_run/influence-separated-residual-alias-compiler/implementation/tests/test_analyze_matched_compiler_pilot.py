from analyze_matched_compiler_pilot import analyze, boundary_key, rollout_calls


def record(boundary, pairs, selector=None, seed=None, witnesses=None, total_blocks=1):
    if witnesses is None:
        witnesses = int(pairs > 0)
    blocks = [
        {"certified_pairs": int(index < witnesses), "failure_reason_counts": {}}
        for index in range(total_blocks)
    ]
    item = {
        "rollout": f"/tmp/task_{boundary}.json",
        "candidate_chunk_index": boundary,
        "compiled_pair_count": pairs,
        "selected_block_count": total_blocks,
        "selection_contact_rollouts": 2,
        "physics_rollouts_per_selected_block": 8,
        "blocks": blocks,
        "best_pairs": [],
    }
    if selector is not None:
        item["block_selector"] = selector
        item["selector_seed"] = seed
    return item


def test_boundary_key_and_legacy_call_budget():
    item = record(3, 2)
    assert boundary_key(item).endswith("::c03")
    assert rollout_calls(item) == 10


def test_missing_seed_is_not_counted_as_zero_and_blocks_gate():
    israc = [record(1, 2), record(2, 2)]
    baseline = [record(1, 1, "random-scene", 0)]
    result = analyze(israc, baseline, bootstrap_samples=100, bootstrap_seed=0)
    seed = result["baselines"]["random-scene"]["seeds"]["0"]
    assert not seed["complete"]
    assert len(seed["missing_boundaries"]) == 1
    assert not result["baselines"]["random-scene"][
        "paired_bootstrap_unique_witness_yield_ratio_israc_over_baseline"
    ]["complete"]


def test_paired_bootstrap_reports_two_x_for_exact_matched_calls():
    israc = [record(1, 2, witnesses=2, total_blocks=2), record(2, 2, witnesses=2, total_blocks=2)]
    baseline = []
    for seed in range(3):
        baseline.extend(
            [
                record(1, 1, "candidate-contact", seed, witnesses=1, total_blocks=2),
                record(2, 1, "candidate-contact", seed, witnesses=1, total_blocks=2),
            ]
        )
    result = analyze(israc, baseline, bootstrap_samples=200, bootstrap_seed=0)
    ratio = result["baselines"]["candidate-contact"][
        "paired_bootstrap_unique_witness_yield_ratio_israc_over_baseline"
    ]
    assert ratio["complete"]
    assert ratio["median"] == 2.0
    assert ratio["ci95"] == [2.0, 2.0]
    assert ratio["probability_ratio_ge_2"] == 1.0
