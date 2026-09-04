from __future__ import annotations

import json
import hashlib
import os
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest import mock

import torch
import pgr_audit.launcher as launcher_module

from pgr_audit.adapter import IdentityLowRankAdapter
from pgr_audit.canonical import canonical_json_bytes, directory_sha256, file_sha256
from pgr_audit.determinism import role_seed
from pgr_audit.checkpoint import CheckpointContractError, validate_state_keys
from pgr_audit.constants import RUNTIME_CACHE, RUNTIME_CONFIG, RUNTIME_HOME, RUNTIME_TMP
from pgr_audit.gradient_router import adapters_identical, matched_triplet_step
from pgr_audit.gpu_guard import (
    GPUGuardError,
    GPUSnapshot,
    GPUReservation,
    GPUState,
    assert_owned_gpu_binding,
    assert_recorded_gpu_pids_absent,
    choose_idle_gpu,
    take_snapshot,
)
from pgr_audit.host import move_tensor_inputs_to_device
from pgr_audit.launcher import (
    LaunchLifecycleError,
    _private_environment,
    _validate_exact_regular_files,
    _validate_handshake,
    exact_canary_command,
    validate_canary_metrics,
    validate_private_environment,
)
from pgr_audit.provenance import CanaryProvenance, source_tree_sha256
from pgr_audit.retry import decide_retry
from pgr_audit.robot import LiveRobotNotAuthorized, LockedRobotAdapter
from pgr_audit.sealing import PRE_REVEAL_STDOUT_FIELDS, SealedBatch, filter_pre_reveal_telemetry
from pgr_audit.splits import allocate_task, assert_disjoint_complete


class CanonicalTests(unittest.TestCase):
    def test_canonical_json_has_no_newline_and_sorted_keys(self) -> None:
        payload = canonical_json_bytes({"z": 1, "a": "世界"})
        self.assertEqual(payload, '{"a":"世界","z":1}'.encode("utf-8"))
        self.assertFalse(payload.endswith(b"\n"))

    def test_directory_hash_rejects_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "real").write_bytes(b"x")
            try:
                (root / "link").symlink_to(root / "real")
            except OSError:
                self.skipTest("Symlinks unavailable")
            with self.assertRaises(ValueError):
                directory_sha256(root)

    def test_directory_hash_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "b").write_bytes(b"two")
            (root / "a").write_bytes(b"one")
            first = directory_sha256(root)
            second = directory_sha256(root)
            self.assertEqual(first, second)
            self.assertEqual(len(first), 64)
            self.assertEqual(file_sha256(root / "a"), "7692c3ad3540bb803c020b3aee66cd8887123234ea0c6e7143c0add73ff431ed")


class AdapterTests(unittest.TestCase):
    def test_initial_mapping_is_exact_identity_and_shapes_are_frozen(self) -> None:
        generator = torch.Generator(device="cpu").manual_seed(3)
        adapter = IdentityLowRankAdapter(generator=generator)
        hidden = torch.randn(2, 8, 2560, generator=generator)
        adapter.assert_identity(hidden)
        self.assertEqual(tuple(adapter.V.shape), (32, 2560))
        self.assertEqual(tuple(adapter.U.shape), (2560, 32))

    def test_ln0_uses_population_variance(self) -> None:
        adapter = IdentityLowRankAdapter(dimension=4, rank=2)
        hidden = torch.tensor([[[1.0, 2.0, 3.0, 4.0]]])
        normalized = adapter.ln0(hidden)
        variance = normalized.var(dim=-1, unbiased=False)
        self.assertTrue(torch.allclose(variance, torch.tensor([[1.0]]), atol=1e-4))

    def test_bfloat16_input_is_exact_fp32_identity_at_zero_u(self) -> None:
        adapter = IdentityLowRankAdapter(dimension=4, rank=2)
        hidden = torch.tensor([[[1.0, -2.0, 0.5, 3.0]]], dtype=torch.bfloat16)
        adapter.assert_identity(hidden)
        self.assertEqual(adapter(hidden).dtype, torch.float32)


class SealingAndRetryTests(unittest.TestCase):
    def test_pre_reveal_fields_fail_closed(self) -> None:
        allowed = {field: False for field in PRE_REVEAL_STDOUT_FIELDS}
        self.assertEqual(filter_pre_reveal_telemetry(allowed), allowed)
        with self.assertRaises(ValueError):
            filter_pre_reveal_telemetry({"success": True})

    def test_sealed_batch_is_immutable_and_requires_completeness(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # The production guard is intentionally bypassed in this isolated unit test.
            class TestGuard:
                def require_existing(self, path, regular=None):
                    return Path(path).resolve()

            batch = SealedBatch(root=root, expected_record_ids=("r0", "r1"), guard=TestGuard())
            batch.initialize()
            batch.write_record("r0", {"value": 1})
            with self.assertRaises(FileExistsError):
                batch.write_record("r0", {"value": 2})
            with self.assertRaises(RuntimeError):
                batch.freeze_completion()
            batch.write_record("r1", {"value": 2})
            batch.freeze_completion()
            completion = json.loads((root / "completion_manifest.json").read_text("utf-8"))
            self.assertEqual(completion["status"], "sealed-complete")

    def test_only_one_unchanged_technical_retry(self) -> None:
        first = decide_retry(
            attempt_no=1,
            failure_class="simulation_reset_before_policy_action",
            hashes_unchanged=True,
            same_seed_and_condition=True,
            scientific_input_read=True,
            optimizer_update_or_policy_action=False,
        )
        self.assertTrue(first.allowed)
        second = decide_retry(
            attempt_no=2,
            failure_class="simulation_reset_before_policy_action",
            hashes_unchanged=True,
            same_seed_and_condition=True,
            scientific_input_read=True,
            optimizer_update_or_policy_action=False,
        )
        self.assertFalse(second.allowed)
        self.assertTrue(second.terminal_missing)

    def test_role_seed_is_domain_separated_and_repeatable(self) -> None:
        self.assertEqual(role_seed("adapter", 4), role_seed("adapter", 4))
        self.assertNotEqual(role_seed("adapter", 4), role_seed("projector", 4))


class SplitAndRobotTests(unittest.TestCase):
    EXPECTED = {
        0: ((15, 6, 17), (7, 4, 4), (4, 4, 3, 3, 3)),
        1: ((14, 5, 17), (7, 4, 3), (4, 4, 3, 3, 3)),
        2: ((13, 5, 16), (6, 4, 3), (4, 3, 3, 3, 3)),
        3: ((16, 7, 18), (8, 4, 4), (4, 4, 3, 3, 4)),
        4: ((17, 7, 19), (9, 4, 4), (4, 4, 4, 3, 4)),
        5: ((13, 4, 16), (6, 4, 3), (4, 3, 3, 3, 3)),
        6: ((11, 3, 15), (5, 3, 3), (3, 3, 3, 3, 3)),
        7: ((20, 9, 20), (10, 5, 5), (5, 5, 3, 3, 4)),
        8: ((14, 5, 16), (7, 4, 3), (4, 3, 3, 3, 3)),
        9: ((16, 7, 18), (8, 4, 4), (4, 4, 3, 3, 4)),
    }

    def test_golden_task_counts(self) -> None:
        episode_counts = {0: 38, 1: 36, 2: 34, 3: 41, 4: 43, 5: 33, 6: 29, 7: 49, 8: 35, 9: 41}
        for task, count in episode_counts.items():
            split = allocate_task(task, range(count))
            outer_counts = tuple(len(split.outer[label]) for label in ("head", "adapter", "post"))
            head_counts = tuple(len(split.head[label]) for label in ("train", "val", "strict_test"))
            post_counts = tuple(len(split.post[f"fold{fold}"]) for fold in range(5))
            self.assertEqual((outer_counts, head_counts, post_counts), self.EXPECTED[task])
            assert_disjoint_complete(range(count), split.outer)
            assert_disjoint_complete(split.outer["head"], split.head)
            assert_disjoint_complete(split.outer["post"], split.post)

    def test_task_below_29_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            allocate_task(0, range(28))

    def test_split_is_input_order_invariant(self) -> None:
        forward = allocate_task(7, range(49))
        reverse = allocate_task(7, reversed(range(49)))
        self.assertEqual(forward, reverse)

    def test_robot_adapter_has_no_live_surface(self) -> None:
        adapter = LockedRobotAdapter()
        self.assertFalse(adapter.live_action_authorized)
        self.assertEqual(adapter.endpoint_allowlist, ())
        for operation in (adapter.connect, adapter.observe, adapter.command, adapter.move):
            with self.assertRaises(LiveRobotNotAuthorized):
                operation()


class CheckpointAndGradientTests(unittest.TestCase):
    def test_checkpoint_key_contract(self) -> None:
        keys = [f"qwen_vl_interface.layer.{index}" for index in range(729)] + ["action_model.head"]
        digest = hashlib.sha256()
        for key in sorted(keys):
            digest.update(key.encode("utf-8"))
            digest.update(b"\n")
        with mock.patch("pgr_audit.checkpoint.CHECKPOINT_KEYSET_SHA256", digest.hexdigest()):
            self.assertEqual(len(validate_state_keys(keys)), 730)
        with self.assertRaises(CheckpointContractError):
            validate_state_keys(keys[:-1])
        contaminated = list(keys)
        contaminated[-1] = "action_model.future_head.weight"
        with self.assertRaises(CheckpointContractError):
            validate_state_keys(contaminated)

    def test_matched_step_computes_and_discards_b_future_gradient(self) -> None:
        generator = torch.Generator(device="cpu").manual_seed(11)
        adapters = [IdentityLowRankAdapter(dimension=4, rank=2, generator=generator) for _ in range(3)]
        # Reinitialize from one exact state so the triplet starts identically.
        state = adapters[0].state_dict()
        for adapter in adapters[1:]:
            adapter.load_state_dict(state)
        self.assertTrue(adapters_identical(adapters))

        hidden = torch.tensor([[[1.0, -2.0, 0.5, 3.0]]])
        action_target = torch.tensor([[[0.2, -0.1, 0.4, 0.8]]])
        valid_target = torch.tensor([[[0.7, -0.3, 0.1, 0.2]]])
        donor_target = torch.tensor([[[-0.4, 0.5, 0.2, -0.7]]])

        def loss(target):
            return lambda adapter: (adapter(hidden) - target).square().mean()

        diagnostics = matched_triplet_step(
            adapter_a=adapters[0],
            adapter_b=adapters[1],
            adapter_c=adapters[2],
            action_loss_a=loss(action_target),
            action_loss_b=loss(action_target),
            action_loss_c=loss(action_target),
            valid_future_loss_a=loss(valid_target),
            valid_future_loss_b=loss(valid_target),
            donor_future_loss_c=loss(donor_target),
        )
        self.assertGreaterEqual(diagnostics.future_norm_b_discarded, 0.0)
        self.assertTrue(torch.isfinite(torch.tensor(diagnostics.action_norm_b)))
        # A and B differ unless the joint fallback gate intentionally made both action-only.
        if not diagnostics.fallback:
            self.assertFalse(adapters_identical(adapters[:2]))

    def test_joint_fallback_when_rho_is_zero(self) -> None:
        generator = torch.Generator(device="cpu").manual_seed(12)
        adapters = [IdentityLowRankAdapter(dimension=4, rank=2, generator=generator) for _ in range(3)]
        state = adapters[0].state_dict()
        for adapter in adapters[1:]:
            adapter.load_state_dict(state)
        hidden = torch.ones(1, 1, 4)

        def zero_action(adapter):
            return adapter(hidden).sum() * 0.0

        def future(adapter):
            return adapter(hidden).square().mean()

        diagnostics = matched_triplet_step(
            adapter_a=adapters[0],
            adapter_b=adapters[1],
            adapter_c=adapters[2],
            action_loss_a=zero_action,
            action_loss_b=zero_action,
            action_loss_c=zero_action,
            valid_future_loss_a=future,
            valid_future_loss_b=future,
            donor_future_loss_c=future,
        )
        self.assertTrue(diagnostics.fallback)
        self.assertTrue(any("rho<=1e-12" in reason for reason in diagnostics.fallback_reasons))
        self.assertTrue(adapters_identical(adapters))

    def test_nonfinite_loss_fails_before_update(self) -> None:
        adapters = [IdentityLowRankAdapter(dimension=4, rank=2) for _ in range(3)]
        state = adapters[0].state_dict()
        for adapter in adapters[1:]:
            adapter.load_state_dict(state)
        hidden = torch.ones(1, 1, 4)

        def finite(adapter):
            return adapter(hidden).square().mean()

        def nonfinite(adapter):
            return adapter(hidden).sum() * torch.tensor(float("nan"))

        before = [{key: value.clone() for key, value in adapter.state_dict().items()} for adapter in adapters]
        with self.assertRaises(FloatingPointError):
            matched_triplet_step(
                adapter_a=adapters[0],
                adapter_b=adapters[1],
                adapter_c=adapters[2],
                action_loss_a=nonfinite,
                action_loss_b=finite,
                action_loss_c=finite,
                valid_future_loss_a=finite,
                valid_future_loss_b=finite,
                donor_future_loss_c=finite,
            )
        for adapter, expected in zip(adapters, before, strict=True):
            self.assertTrue(all(torch.equal(adapter.state_dict()[key], value) for key, value in expected.items()))


class GPUGuardTests(unittest.TestCase):
    GPU_ROWS = "\n".join(
        [
            "0, GPU-417b37b2-bb07-cc79-ca59-2e43af96d3ea, 700, 10",
            "1, GPU-708fad71-ac97-0c67-85fc-15e9534b2f59, 0, 0",
            "2, GPU-c034ca59-aa0c-4629-ce5d-a0b5d92e2747, 0, 0",
            "3, GPU-aa863a6c-8482-fd6c-e957-424e559e9df4, 0, 0",
        ]
    )

    def test_preferred_idle_order_and_independent_gpu01_rule(self) -> None:
        def runner(command):
            return self.GPU_ROWS if "--query-gpu=index,uuid,memory.used,utilization.gpu" in command else ""

        snapshot = take_snapshot(runner)
        self.assertEqual(choose_idle_gpu(snapshot).physical_index, 2)

    def test_compute_pid_makes_preferred_gpu_busy(self) -> None:
        def runner(command):
            if "--query-gpu=index,uuid,memory.used,utilization.gpu" in command:
                return self.GPU_ROWS
            return "GPU-c034ca59-aa0c-4629-ce5d-a0b5d92e2747, 991\n"

        snapshot = take_snapshot(runner)
        self.assertEqual(choose_idle_gpu(snapshot).physical_index, 3)

    def test_uuid_mismatch_fails_closed(self) -> None:
        rows = self.GPU_ROWS.replace("GPU-c034ca59-aa0c-4629-ce5d-a0b5d92e2747", "GPU-WRONG")

        def runner(command):
            return rows if "--query-gpu=index,uuid,memory.used,utilization.gpu" in command else ""

        with self.assertRaises(GPUGuardError):
            take_snapshot(runner)

    def test_malformed_compute_row_fails_closed(self) -> None:
        def runner(command):
            return self.GPU_ROWS if "--query-gpu=index,uuid,memory.used,utilization.gpu" in command else "N/A, N/A\n"

        with self.assertRaises(GPUGuardError):
            take_snapshot(runner)

    def test_owned_binding_rejects_foreign_pid(self) -> None:
        states = (
            GPUState(0, "GPU-417b37b2-bb07-cc79-ca59-2e43af96d3ea", 0, 0, ()),
            GPUState(1, "GPU-708fad71-ac97-0c67-85fc-15e9534b2f59", 0, 0, ()),
            GPUState(2, "GPU-c034ca59-aa0c-4629-ce5d-a0b5d92e2747", 100, 1, (41, 99)),
            GPUState(3, "GPU-aa863a6c-8482-fd6c-e957-424e559e9df4", 0, 0, ()),
        )
        snapshot = GPUSnapshot("now", 1.0, states)
        with self.assertRaises(GPUGuardError):
            assert_owned_gpu_binding(snapshot, states[2], owned_pids=frozenset({41}), child_pid=41)

    def test_owned_binding_rejects_cross_gpu_context(self) -> None:
        states = (
            GPUState(0, "GPU-417b37b2-bb07-cc79-ca59-2e43af96d3ea", 0, 0, (41,)),
            GPUState(1, "GPU-708fad71-ac97-0c67-85fc-15e9534b2f59", 0, 0, ()),
            GPUState(2, "GPU-c034ca59-aa0c-4629-ce5d-a0b5d92e2747", 100, 1, (41,)),
            GPUState(3, "GPU-aa863a6c-8482-fd6c-e957-424e559e9df4", 0, 0, ()),
        )
        snapshot = GPUSnapshot("now", 1.0, states)
        with self.assertRaises(GPUGuardError):
            assert_owned_gpu_binding(snapshot, states[2], owned_pids=frozenset({41}), child_pid=41)

    def test_recorded_pid_must_be_absent_before_release(self) -> None:
        states = (
            GPUState(0, "GPU-417b37b2-bb07-cc79-ca59-2e43af96d3ea", 0, 0, ()),
            GPUState(1, "GPU-708fad71-ac97-0c67-85fc-15e9534b2f59", 0, 0, ()),
            GPUState(2, "GPU-c034ca59-aa0c-4629-ce5d-a0b5d92e2747", 10, 0, (41,)),
            GPUState(3, "GPU-aa863a6c-8482-fd6c-e957-424e559e9df4", 0, 0, ()),
        )
        with self.assertRaises(GPUGuardError):
            assert_recorded_gpu_pids_absent(GPUSnapshot("now", 1.0, states), frozenset({41}))

    def test_reservation_release_is_archived_with_release_proof(self) -> None:
        class TestGuard:
            def require_existing(self, path, regular=None):
                return Path(path).resolve()

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = GPUState(2, "GPU-c034ca59-aa0c-4629-ce5d-a0b5d92e2747", 0, 0, ())
            reservation = GPUReservation(
                state=state,
                launch_uuid="launch-test",
                logical_run_id="V2-007",
                root=root,
                guard=TestGuard(),
            )
            reservation.acquire()
            reservation.refresh()
            target, digest, payload = reservation.archive_release(post_exit_snapshot_sha256="a" * 64)
            self.assertTrue(target.is_file())
            self.assertEqual(digest, file_sha256(target))
            self.assertEqual(payload["status"], "verified-released")
            self.assertEqual(payload["post_exit_snapshot_sha256"], "a" * 64)


class LauncherPureTests(unittest.TestCase):
    def test_handshake_requires_exact_physical_binding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "child_bound.json"
            value = {
                "pid": 12,
                "pgid": 12,
                "visible_device_count": 1,
                "cuda_visible_devices": "2",
                "selected_physical_index": 2,
                "selected_gpu_uuid": "GPU-X",
                "observed_gpu_uuid": "GPU-WRONG",
            }
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaises(LaunchLifecycleError):
                _validate_handshake(
                    path,
                    process_pid=12,
                    pgid=12,
                    selected_index=2,
                    selected_uuid="GPU-X",
                    launch_uuid="launch-x",
                )

    def test_output_whitelist_rejects_unexpected_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "launch.json").write_bytes(b"{}")
            (root / "leak.txt").write_bytes(b"x")
            with self.assertRaises(LaunchLifecycleError):
                _validate_exact_regular_files(root, frozenset({"launch.json"}))

    def test_launcher_exposes_only_exact_canary_command(self) -> None:
        command = exact_canary_command(1000)
        self.assertEqual(command[1:], ("-m", "pgr_audit.engineering_canary", "--checkpoint-step", "1000"))
        with self.assertRaises(LaunchLifecycleError):
            exact_canary_command(42)

    def test_private_environment_uses_uuid_and_frozen_roots(self) -> None:
        state = GPUState(2, "GPU-c034ca59-aa0c-4629-ce5d-a0b5d92e2747", 0, 0, ())
        provenance = CanaryProvenance(*(["a" * 64] * 8), upstream_head="b" * 40)
        environment = _private_environment(state, "launch", Path("/tmp/output"), provenance)
        validate_private_environment(environment, state.hardware_uuid)
        self.assertEqual(environment["CUDA_VISIBLE_DEVICES"], state.hardware_uuid)
        self.assertEqual(environment["HOME"], str(RUNTIME_HOME))
        self.assertEqual(environment["TMPDIR"], str(RUNTIME_TMP))
        self.assertEqual(environment["XDG_CACHE_HOME"], str(RUNTIME_CACHE))
        self.assertEqual(environment["XDG_CONFIG_HOME"], str(RUNTIME_CONFIG))
        self.assertNotIn("PYTHONPATH", environment)

    def test_canary_metrics_require_zero_science_and_finite_parity(self) -> None:
        provenance = CanaryProvenance(*(["a" * 64] * 8), upstream_head="b" * 40)
        value = {
            "canary_kind": "engineering-only-no-scientific-target",
            "checkpoint_step": 1000,
            "scientific_examples_read": 0,
            "scientific_outcomes_read": 0,
            "robot_trials": 0,
            "paid_cost_usd": 0.0,
            "synthetic_examples": 1,
            "approval_sha256": provenance.approval_sha256,
            "overlay_source_sha256": provenance.overlay_source_sha256,
            "environment_lock_sha256": provenance.environment_lock_sha256,
            "sanitized_config_sha256": provenance.sanitized_config_sha256,
            "review_response_sha256": provenance.review_response_sha256,
            "host_audit": {
                "hidden_size": 2560,
                "action_horizon": 8,
                "trainable_parameter_count": 0,
                "checkpoint": {
                    "sha256": provenance.checkpoint_sha256,
                    "key_count": 730,
                    "keyset_sha256": "c258f23f041e115f20626b6b4a49acf8cf01a562377ba37a94101e3331d810e0",
                },
            },
            "determinism": {
                "cublas_workspace_config": ":4096:8",
                "cudnn_benchmark": False,
                "cudnn_deterministic": True,
                "deterministic_algorithms": True,
                "matmul_precision": "highest",
                "pythonhashseed": "7",
                "tf32_cudnn": False,
                "tf32_matmul": False,
            },
            "interface_parity": {
                "direct_vs_interface_max_abs": 0.0,
                "interface_repeat_max_abs": 0.0,
                "in_memory_cache_roundtrip_max_abs": 0.0,
                "threshold": 1e-6,
            },
            "max_memory_allocated_bytes": 1,
            "max_memory_reserved_bytes": 1,
            "model_load_seconds": 1.0,
            "parity_seconds": 1.0,
        }
        validate_canary_metrics(value, 1000, provenance)
        value["scientific_outcomes_read"] = 1
        with self.assertRaises(LaunchLifecycleError):
            validate_canary_metrics(value, 1000, provenance)

    def test_mocked_end_to_end_canary_seals_exact_success_set(self) -> None:
        class TestGuard:
            def verify_root(self):
                return root

            def require_existing(self, path, regular=None):
                return Path(path).resolve()

            def create_uuid_directory(self, parent, label):
                output = Path(parent) / f"{label}-fixed"
                output.mkdir(mode=0o700)
                return output

        class FakePopen:
            pid = 4321

            def __init__(self, command, cwd, env, stdout, stderr, start_new_session):
                self.returncode = None
                self.polls = 0
                output = Path(env["PGR_OUTPUT_DIR"])
                handshake = {
                    "cuda_device_name": "mock-a100",
                    "cuda_visible_devices": env["CUDA_VISIBLE_DEVICES"],
                    "launch_uuid": env["PGR_LAUNCH_UUID"],
                    "observed_gpu_uuid": env["PGR_SELECTED_GPU_UUID"],
                    "pgid": 4321,
                    "pid": 4321,
                    "selected_gpu_uuid": env["PGR_SELECTED_GPU_UUID"],
                    "selected_physical_index": int(env["PGR_SELECTED_PHYSICAL_INDEX"]),
                    "visible_device_count": 1,
                }
                (output / "child_bound.json").write_text(json.dumps(handshake), encoding="utf-8")
                metrics = {
                    "canary_kind": "engineering-only-no-scientific-target",
                    "checkpoint_step": 1000,
                    "scientific_examples_read": 0,
                    "scientific_outcomes_read": 0,
                    "robot_trials": 0,
                    "paid_cost_usd": 0.0,
                    "synthetic_examples": 1,
                    "approval_sha256": env["PGR_APPROVAL_SHA256"],
                    "overlay_source_sha256": env["PGR_OVERLAY_SOURCE_SHA256"],
                    "environment_lock_sha256": env["PGR_ENVIRONMENT_LOCK_SHA256"],
                    "sanitized_config_sha256": env["PGR_SANITIZED_CONFIG_SHA256"],
                    "review_response_sha256": env["PGR_REVIEW_RESPONSE_SHA256"],
                    "host_audit": {
                        "hidden_size": 2560,
                        "action_horizon": 8,
                        "trainable_parameter_count": 0,
                        "checkpoint": {
                            "sha256": provenance.checkpoint_sha256,
                            "key_count": 730,
                            "keyset_sha256": "c258f23f041e115f20626b6b4a49acf8cf01a562377ba37a94101e3331d810e0",
                        },
                    },
                    "determinism": {
                        "cublas_workspace_config": ":4096:8",
                        "cudnn_benchmark": False,
                        "cudnn_deterministic": True,
                        "deterministic_algorithms": True,
                        "matmul_precision": "highest",
                        "pythonhashseed": "7",
                        "tf32_cudnn": False,
                        "tf32_matmul": False,
                    },
                    "interface_parity": {
                        "direct_vs_interface_max_abs": 0.0,
                        "interface_repeat_max_abs": 0.0,
                        "in_memory_cache_roundtrip_max_abs": 0.0,
                        "threshold": 1e-6,
                    },
                    "max_memory_allocated_bytes": 100,
                    "max_memory_reserved_bytes": 200,
                    "model_load_seconds": 1.0,
                    "parity_seconds": 1.0,
                }
                (output / "canary_metrics.json").write_text(json.dumps(metrics), encoding="utf-8")

            def poll(self):
                self.polls += 1
                if self.polls >= 2:
                    self.returncode = 0
                return self.returncode

            def wait(self, timeout=None):
                self.returncode = 0
                return 0

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspace"
            artifact = root / "artifacts"
            locks = root / "locks"
            python = root / "python3.11"
            workspace.mkdir()
            artifact.mkdir()
            locks.mkdir()
            python.write_bytes(b"mock-python")
            runtime_paths = [root / name for name in ("home", "tmp", "cache", "config", "hf", "torch", "ext", "cuda", "wandb")]
            for path in runtime_paths:
                path.mkdir()
            provenance = CanaryProvenance(*(["a" * 64] * 8), upstream_head="b" * 40)
            idle_states = (
                GPUState(0, "GPU-417b37b2-bb07-cc79-ca59-2e43af96d3ea", 0, 0, ()),
                GPUState(1, "GPU-708fad71-ac97-0c67-85fc-15e9534b2f59", 0, 0, ()),
                GPUState(2, "GPU-c034ca59-aa0c-4629-ce5d-a0b5d92e2747", 0, 0, ()),
                GPUState(3, "GPU-aa863a6c-8482-fd6c-e957-424e559e9df4", 0, 0, ()),
            )
            bound_states = tuple(
                GPUState(s.physical_index, s.hardware_uuid, 100 if s.physical_index == 2 else 0, 1 if s.physical_index == 2 else 0, (4321,) if s.physical_index == 2 else ())
                for s in idle_states
            )
            snapshots = [
                GPUSnapshot("t0", 1.0, idle_states),
                GPUSnapshot("t1", 2.0, idle_states),
                GPUSnapshot("t2", 3.0, bound_states),
                GPUSnapshot("t3", 4.0, bound_states),
                GPUSnapshot("t4", 5.0, idle_states),
            ]

            def reservation_factory(state, launch_uuid, logical_run_id):
                return GPUReservation(
                    state=state,
                    launch_uuid=launch_uuid,
                    logical_run_id=logical_run_id,
                    root=locks,
                    guard=TestGuard(),
                )

            patches = (
                mock.patch.object(launcher_module, "PersonalRootGuard", return_value=TestGuard()),
                mock.patch.object(launcher_module, "ISOLATED_WORKSPACE", workspace),
                mock.patch.object(launcher_module, "ARTIFACT_ROOT", artifact),
                mock.patch.object(launcher_module, "TRAIN_PYTHON", python),
                mock.patch.object(launcher_module, "RUNTIME_HOME", runtime_paths[0]),
                mock.patch.object(launcher_module, "RUNTIME_TMP", runtime_paths[1]),
                mock.patch.object(launcher_module, "RUNTIME_CACHE", runtime_paths[2]),
                mock.patch.object(launcher_module, "RUNTIME_CONFIG", runtime_paths[3]),
                mock.patch.object(launcher_module, "RUNTIME_HF_HOME", runtime_paths[4]),
                mock.patch.object(launcher_module, "RUNTIME_TORCH_HOME", runtime_paths[5]),
                mock.patch.object(launcher_module, "RUNTIME_TORCH_EXTENSIONS", runtime_paths[6]),
                mock.patch.object(launcher_module, "RUNTIME_CUDA_CACHE", runtime_paths[7]),
                mock.patch.object(launcher_module, "RUNTIME_WANDB", runtime_paths[8]),
                mock.patch.object(launcher_module, "verify_canary_provenance", return_value=provenance),
                mock.patch.object(launcher_module, "take_snapshot", side_effect=snapshots),
                mock.patch.object(launcher_module, "GPUReservation", side_effect=reservation_factory),
                mock.patch.object(launcher_module.subprocess, "Popen", FakePopen),
                mock.patch.object(launcher_module.os, "getpgid", return_value=4321),
                mock.patch.object(launcher_module, "proc_start_ticks", return_value=77),
                mock.patch.object(launcher_module, "pids_in_process_group", return_value=frozenset({4321})),
                mock.patch.object(launcher_module.time, "sleep", return_value=None),
            )
            with ExitStack() as stack:
                for patcher in patches:
                    stack.enter_context(patcher)
                output = launcher_module.run_guarded_canary(1000)
            observed = {path.name for path in output.iterdir()}
            self.assertEqual(observed, set(launcher_module.FINAL_SUCCESS_FILES))
            terminal = json.loads((output / "terminal_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(terminal["status"], "success")
            completion = json.loads((output / "completion.json").read_text(encoding="utf-8"))
            self.assertTrue(completion["reservation_release_verified"])


class ProvenanceAndHostPureTests(unittest.TestCase):
    def test_source_tree_hash_ignores_non_source_cache_but_detects_source_change(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "a.py").write_text("x=1\n", encoding="utf-8")
            first = source_tree_sha256(root)
            (root / "noise.bin").write_bytes(b"ignored")
            self.assertEqual(first, source_tree_sha256(root))
            (root / "a.py").write_text("x=2\n", encoding="utf-8")
            self.assertNotEqual(first, source_tree_sha256(root))

    def test_move_tensor_inputs_to_verified_device(self) -> None:
        inputs = {"input_ids": torch.ones(1, 3, dtype=torch.long)}
        moved = move_tensor_inputs_to_device(inputs, torch.device("meta"))
        self.assertEqual(moved["input_ids"].device.type, "meta")


if __name__ == "__main__":
    unittest.main()
