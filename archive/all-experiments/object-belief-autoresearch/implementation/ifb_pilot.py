#!/usr/bin/env python3
"""Falsification pilot for interaction-fingerprint object belief.

The simulator creates visually indistinguishable rigid objects.  A spatial
pusher trajectory is the action; it never receives an object id.  Persistent
body ids are used only to create evaluation labels and per-address context.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def yaw_to_quat(yaw: float) -> np.ndarray:
    return np.asarray([math.cos(yaw / 2), 0.0, 0.0, math.sin(yaw / 2)])


def quat_to_yaw(quat: np.ndarray) -> float:
    w, x, y, z = quat
    return math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))


def angle_delta(after: float, before: float) -> float:
    return math.atan2(math.sin(after - before), math.cos(after - before))


def make_xml(num_objects: int) -> str:
    boxes = []
    for i in range(num_objects):
        boxes.append(
            f"""
    <body name="box{i}" pos="0 0 0.035">
      <freejoint name="box{i}_joint"/>
      <geom name="box{i}_geom" type="box" size="0.035 0.035 0.035"
            mass="0.15" friction="0.6 0.01 0.001" rgba="0.8 0.2 0.2 1"/>
    </body>"""
        )
    return f"""
<mujoco model="ifb_pilot">
  <option timestep="0.005" gravity="0 0 -9.81" integrator="implicitfast"/>
  <size nconmax="100" njmax="500"/>
  <worldbody>
    <geom name="floor" type="plane" size="1 1 0.05" friction="0.8 0.02 0.002"/>
    {''.join(boxes)}
    <body name="pusher" mocap="true" pos="0 0 0.04">
      <geom name="pusher_geom" type="sphere" size="0.025" mass="0.1"
            friction="0.7 0.01 0.001" rgba="0.2 0.2 0.8 1"/>
    </body>
  </worldbody>
</mujoco>
"""


class PushWorld:
    def __init__(self, num_objects: int):
        import mujoco

        self.mujoco = mujoco
        self.num_objects = num_objects
        self.model = mujoco.MjModel.from_xml_string(make_xml(num_objects))
        self.data = mujoco.MjData(self.model)
        self.body_ids = [mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, f"box{i}") for i in range(num_objects)]
        self.geom_ids = [mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_GEOM, f"box{i}_geom") for i in range(num_objects)]
        self.pusher_geom_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_GEOM, "pusher_geom")
        self.joint_ids = [mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_JOINT, f"box{i}_joint") for i in range(num_objects)]
        self.reference_mass = self.model.body_mass[self.body_ids].copy()
        self.reference_inertia = self.model.body_inertia[self.body_ids].copy()

    def _sample_layout(self, rng: np.random.Generator) -> np.ndarray:
        for _layout_attempt in range(1000):
            points: list[np.ndarray] = []
            for _ in range(self.num_objects):
                for _point_attempt in range(200):
                    p = rng.uniform([-0.17, -0.12], [0.17, 0.12])
                    if all(np.linalg.norm(p - q) > 0.10 for q in points):
                        points.append(p)
                        break
                else:
                    break
            if len(points) == self.num_objects:
                return np.asarray(points, dtype=np.float64)
        raise RuntimeError("failed to sample a non-overlapping layout")

    def _state(self) -> np.ndarray:
        out = np.zeros((self.num_objects, 6), dtype=np.float32)
        for i, jid in enumerate(self.joint_ids):
            qa = self.model.jnt_qposadr[jid]
            va = self.model.jnt_dofadr[jid]
            q = self.data.qpos[qa : qa + 7]
            v = self.data.qvel[va : va + 6]
            out[i] = [q[0], q[1], quat_to_yaw(q[3:7]), v[0], v[1], v[5]]
        return out

    def run_trial(
        self,
        rng: np.random.Generator,
        masses: np.ndarray,
        frictions: np.ndarray,
        move_steps: int = 90,
        settle_steps: int = 100,
        enable_pusher: bool = True,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
        mujoco = self.mujoco
        mujoco.mj_resetData(self.model, self.data)
        layout = self._sample_layout(rng)
        # mj_setConst resets qpos to model.qpos0.  Update physical constants
        # first, then place objects; reversing this order silently collapses
        # every randomized layout to the XML default.
        for i, (bid, gid) in enumerate(zip(self.body_ids, self.geom_ids)):
            self.model.body_mass[bid] = float(masses[i])
            self.model.body_inertia[bid] = self.reference_inertia[i] * float(masses[i] / self.reference_mass[i])
            self.model.geom_friction[gid, 0] = float(frictions[i])
        mujoco.mj_setConst(self.model, self.data)
        for i, jid in enumerate(self.joint_ids):
            qa = self.model.jnt_qposadr[jid]
            yaw = float(rng.uniform(-math.pi, math.pi))
            self.data.qpos[qa : qa + 3] = [layout[i, 0], layout[i, 1], 0.037]
            self.data.qpos[qa + 3 : qa + 7] = yaw_to_quat(yaw)
        # Keep the pusher out of the scene while objects settle into their
        # sampled initial state.
        self.data.mocap_pos[0] = [2.0, 2.0, 1.0]
        mujoco.mj_forward(self.model, self.data)
        for _ in range(200):
            mujoco.mj_step(self.model, self.data)

        pre = self._state()
        anchor = int(rng.integers(0, self.num_objects))
        theta = float(rng.uniform(-math.pi, math.pi))
        direction = np.asarray([math.cos(theta), math.sin(theta)])
        normal = np.asarray([-direction[1], direction[0]])
        lateral = float(rng.uniform(-0.018, 0.018))
        start = pre[anchor, :2] - direction * float(rng.uniform(0.10, 0.15)) + normal * lateral
        end = pre[anchor, :2] + direction * float(rng.uniform(0.12, 0.22)) + normal * lateral
        action = np.asarray([start[0], start[1], end[0], end[1], move_steps * self.model.opt.timestep], dtype=np.float32)

        self.data.mocap_pos[0] = [start[0], start[1], 0.04] if enable_pusher else [2.0, 2.0, 1.0]
        mujoco.mj_forward(self.model, self.data)
        contact_count = 0
        touched_bodies: set[int] = set()
        for step in range(move_steps):
            alpha = (step + 1) / move_steps
            xy = (1 - alpha) * start + alpha * end
            if enable_pusher:
                self.data.mocap_pos[0] = [xy[0], xy[1], 0.04]
            mujoco.mj_step(self.model, self.data)
            for ci in range(self.data.ncon):
                contact = self.data.contact[ci]
                pair = {int(contact.geom1), int(contact.geom2)}
                if self.pusher_geom_id in pair:
                    other = int(contact.geom2 if int(contact.geom1) == self.pusher_geom_id else contact.geom1)
                    if other in self.geom_ids:
                        contact_count += 1
                        touched_bodies.add(self.geom_ids.index(other))
        self.data.mocap_pos[0] = [2.0, 2.0, 1.0]
        for _ in range(settle_steps):
            mujoco.mj_step(self.model, self.data)
        post = self._state()
        return pre, action, post, {
            "contact_count": contact_count,
            "touched_bodies": sorted(touched_bodies),
            "sampled_layout": layout.astype(np.float32),
            "settle_displacement": np.linalg.norm(pre[:, :2] - layout, axis=1).astype(np.float32),
        }


def query_features(pre: np.ndarray, action: np.ndarray) -> np.ndarray:
    n = pre.shape[0]
    feats = []
    for i in range(n):
        rel_start = action[:2] - pre[i, :2]
        rel_end = action[2:4] - pre[i, :2]
        neighbors = []
        for j in range(n):
            if i != j:
                neighbors.append(pre[j, :2] - pre[i, :2])
        neighbors.sort(key=lambda x: float(np.linalg.norm(x)))
        flat_neighbors = np.concatenate(neighbors, axis=0) if neighbors else np.zeros(0)
        # Yaw is deliberately excluded: the pilot's cubes are visually
        # symmetric, so exact simulator yaw would be privileged information.
        # Trials begin after settling; near-zero simulator velocities are
        # excluded to prevent numerical noise from becoming a normalized
        # outlier feature.
        feats.append(np.concatenate([pre[i, :2], rel_start, rel_end, action[4:5], flat_neighbors]))
    return np.asarray(feats, dtype=np.float32)


def history_features(pre: np.ndarray, action: np.ndarray, post: np.ndarray) -> np.ndarray:
    n = pre.shape[0]
    out = np.zeros((n, 6), dtype=np.float32)
    for i in range(n):
        delta = np.asarray([post[i, 0] - pre[i, 0], post[i, 1] - pre[i, 1]], dtype=np.float32)
        out[i] = np.concatenate([action[:2] - pre[i, :2], action[2:4] - pre[i, :2], delta])
    return out


def sample_properties(rng: np.random.Generator, regime: int, n: int) -> tuple[np.ndarray, np.ndarray]:
    if regime == 0:  # heterogeneous, in-distribution
        masses = rng.uniform(0.07, 0.32, size=n)
        frictions = rng.uniform(0.25, 1.00, size=n)
    elif regime == 1:  # homogeneous negative control
        mass = float(rng.uniform(0.12, 0.22))
        friction = float(rng.uniform(0.45, 0.75))
        masses = np.full(n, mass)
        frictions = np.full(n, friction)
    else:  # heterogeneous OOD extremes
        masses = rng.choice([0.045, 0.42], size=n) * rng.uniform(0.9, 1.1, size=n)
        frictions = rng.choice([0.14, 1.25], size=n) * rng.uniform(0.9, 1.1, size=n)
    # Prevent a unique continuous property tuple from always becoming a trivial
    # instance barcode.  Some objects deliberately share their physics.
    if regime != 1 and n > 1 and rng.random() < 0.35:
        dst = int(rng.integers(1, n))
        src = int(rng.integers(0, dst))
        masses[dst] = masses[src]
        frictions[dst] = frictions[src]
    return masses.astype(np.float32), frictions.astype(np.float32)


def generate_dataset(args: argparse.Namespace) -> None:
    seed_everything(args.seed)
    rng = np.random.default_rng(args.seed)
    world = PushWorld(args.num_objects)
    qdim = 7 + 2 * (args.num_objects - 1)
    arrays: dict[str, np.ndarray] = {
        "query": np.zeros((args.episodes, args.num_objects, qdim), np.float32),
        "history": np.zeros((args.episodes, args.num_objects, args.context_steps, 6), np.float32),
        "pre_pose": np.zeros((args.episodes, args.num_objects, 2), np.float32),
        "post_detection": np.zeros((args.episodes, args.num_objects, 2), np.float32),
        "target_delta": np.zeros((args.episodes, args.num_objects, 2), np.float32),
        "properties": np.zeros((args.episodes, args.num_objects, 2), np.float32),
        "id_to_detection": np.zeros((args.episodes, args.num_objects), np.int64),
        "regime": np.zeros(args.episodes, np.int64),
        "split": np.zeros(args.episodes, np.int64),
        "decision_target": np.zeros(args.episodes, np.int64),
        "address_to_body": np.zeros((args.episodes, args.num_objects), np.int64),
        "body_properties": np.zeros((args.episodes, args.num_objects, 2), np.float32),
        "contact_count": np.zeros(args.episodes, np.int64),
        "hard_id": np.zeros(args.episodes, np.int64),
        "sampled_layout": np.zeros((args.episodes, args.num_objects, 2), np.float32),
        "settle_displacement": np.zeros((args.episodes, args.num_objects), np.float32),
        "context_contact_count": np.zeros((args.episodes, args.context_steps), np.int64),
    }
    split_cut1 = int(args.episodes * 0.70)
    split_cut2 = int(args.episodes * 0.85)
    started = time.time()
    for e in range(args.episodes):
        split = 0 if e < split_cut1 else (1 if e < split_cut2 else 2)
        if split < 2:
            regime = int(rng.choice([0, 1], p=[0.75, 0.25]))
        else:
            regime = int(rng.choice([0, 1, 2], p=[0.50, 0.20, 0.30]))
        masses, frictions = sample_properties(rng, regime, args.num_objects)
        # Addresses are freshly mapped to MuJoCo bodies in every episode.  The
        # network never sees this permutation or a body/slot embedding.
        address_to_body = rng.permutation(args.num_objects)
        body_masses = np.empty_like(masses)
        body_frictions = np.empty_like(frictions)
        body_masses[address_to_body] = masses
        body_frictions[address_to_body] = frictions
        for k in range(args.context_steps):
            pre_body, action_h, post_body, diagnostics_h = world.run_trial(rng, body_masses, body_frictions)
            pre_h, post_h = pre_body[address_to_body], post_body[address_to_body]
            arrays["history"][e, :, k] = history_features(pre_h, action_h, post_h)
            arrays["context_contact_count"][e, k] = diagnostics_h["contact_count"]
        pre_body, action, post_body, diagnostics = world.run_trial(rng, body_masses, body_frictions)
        pre, post = pre_body[address_to_body], post_body[address_to_body]
        arrays["query"][e] = query_features(pre, action)
        arrays["pre_pose"][e] = pre[:, :2]
        delta = post[:, :2] - pre[:, :2]
        arrays["target_delta"][e] = delta
        arrays["properties"][e, :, 0] = masses
        arrays["properties"][e, :, 1] = frictions
        det_to_id = rng.permutation(args.num_objects)
        arrays["post_detection"][e] = post[det_to_id, :2]
        arrays["id_to_detection"][e, det_to_id] = np.arange(args.num_objects)
        arrays["regime"][e] = regime
        arrays["split"][e] = split
        arrays["decision_target"][e] = int(rng.integers(0, args.num_objects))
        arrays["address_to_body"][e] = address_to_body
        arrays["body_properties"][e, :, 0] = body_masses
        arrays["body_properties"][e, :, 1] = body_frictions
        arrays["contact_count"][e] = diagnostics["contact_count"]
        arrays["sampled_layout"][e] = diagnostics["sampled_layout"][address_to_body]
        arrays["settle_displacement"][e] = diagnostics["settle_displacement"][address_to_body]
        distances = np.linalg.norm(pre[:, None, :2] - post[None, :, :2], axis=-1)
        sorted_distances = np.sort(distances, axis=1)
        pose_margin = float(np.mean(sorted_distances[:, 1] - sorted_distances[:, 0]))
        max_move = float(np.linalg.norm(delta, axis=1).max())
        # Fixed before any model training.  The 9.5 cm margin is on the scale
        # of one box diameter and selects the genuinely ambiguous part of the
        # corrected two-dimensional layout distribution.
        arrays["hard_id"][e] = int(pose_margin < 0.095 and max_move > 0.025)
        if (e + 1) % max(1, args.episodes // 20) == 0:
            print(json.dumps({"event": "progress", "episodes": e + 1, "elapsed_sec": round(time.time() - started, 2)}), flush=True)

    out = Path(args.output)
    if out.suffix != ".npz":
        raise ValueError("--output must end in .npz")
    out.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "seed": args.seed,
        "episodes": args.episodes,
        "num_objects": args.num_objects,
        "context_steps": args.context_steps,
        "generator": "MuJoCo spatial mocap pusher; stable body ids excluded from model inputs",
        "regimes": {"0": "heterogeneous-id", "1": "homogeneous-negative-control", "2": "heterogeneous-ood"},
        "split": {"0": "train", "1": "validation", "2": "test"},
        "created_unix": time.time(),
    }
    np.savez_compressed(out, **arrays, metadata=np.asarray(json.dumps(metadata)))
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    (out.with_suffix(out.suffix + ".sha256")).write_text(digest + "\n", encoding="utf-8")
    print(json.dumps({"event": "complete", "output": str(out), "sha256": digest, "elapsed_sec": time.time() - started}))


class Normalizer:
    def __init__(self, values: np.ndarray, eps: float = 1e-6):
        self.mean = values.mean(axis=0)
        self.std = values.std(axis=0) + eps

    def apply(self, x: np.ndarray) -> np.ndarray:
        return (x - self.mean) / self.std


def load_data(path: str) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as f:
        return {k: f[k] for k in f.files if k != "metadata"}


def bootstrap_ci(values: np.ndarray, seed: int = 123, rounds: int = 2000) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(values)
    means = np.empty(rounds, np.float64)
    for i in range(rounds):
        means[i] = values[rng.integers(0, n, n)].mean()
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def assignment_metrics(
    predicted_post: np.ndarray,
    sigma: np.ndarray,
    detections: np.ndarray,
    truth: np.ndarray,
    target_address: np.ndarray,
) -> dict[str, Any]:
    e_count, n, _ = predicted_post.shape
    perms = list(itertools.permutations(range(n)))
    object_correct = np.zeros(e_count, np.float32)
    exact = np.zeros(e_count, np.float32)
    wrong_target = np.zeros(e_count, np.float32)
    confidence = np.zeros(e_count, np.float32)
    nll = np.zeros(e_count, np.float32)
    for e in range(e_count):
        costs = np.zeros((n, n), np.float64)
        for i in range(n):
            residual = detections[e] - predicted_post[e, i]
            local_sigma = sigma if sigma.ndim == 1 else sigma[e, i]
            costs[i] = 0.5 * np.sum((residual / local_sigma) ** 2 + 2.0 * np.log(local_sigma), axis=1)
        perm_costs = np.asarray([sum(costs[i, p[i]] for i in range(n)) for p in perms])
        best_idx = int(np.argmin(perm_costs))
        pred = np.asarray(perms[best_idx])
        object_correct[e] = np.mean(pred == truth[e])
        exact[e] = float(np.all(pred == truth[e]))
        target = int(target_address[e])
        wrong_target[e] = float(pred[target] != truth[e, target])
        shifted = -perm_costs - np.max(-perm_costs)
        probs = np.exp(shifted)
        probs /= probs.sum()
        confidence[e] = float(probs[best_idx])
        true_idx = perms.index(tuple(int(x) for x in truth[e]))
        nll[e] = -math.log(max(float(probs[true_idx]), 1e-12))
    bins = np.linspace(0, 1, 11)
    ece = 0.0
    for low, high in zip(bins[:-1], bins[1:]):
        mask = (confidence >= low) & (confidence < high if high < 1 else confidence <= high)
        if mask.any():
            ece += float(mask.mean() * abs(exact[mask].mean() - confidence[mask].mean()))
    coverage = {}
    for q in [0.50, 0.70, 0.90]:
        threshold = float(np.quantile(confidence, 1 - q))
        accepted = confidence >= threshold
        coverage[str(q)] = {
            "threshold": threshold,
            "actual_coverage": float(accepted.mean()),
            "wrong_target_rate": float(wrong_target[accepted].mean()),
        }
    lo, hi = bootstrap_ci(object_correct)
    return {
        "assignment_accuracy": float(object_correct.mean()),
        "assignment_accuracy_ci95": [lo, hi],
        "exact_episode_accuracy": float(exact.mean()),
        "wrong_target_rate": float(wrong_target.mean()),
        "posterior_nll": float(nll.mean()),
        "ece": ece,
        "risk_coverage": coverage,
        "per_episode_accuracy": object_correct.tolist(),
    }


def build_model(variant: str, query_dim: int, history_dim: int, target_dim: int, hidden: int):
    import torch
    from torch import nn

    class EffectModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.variant = variant
            extra = 0
            if variant == "oracle":
                extra = 2
            if variant in {"fingerprint", "global_history", "shuffled_history"}:
                self.hist_encoder = nn.Sequential(nn.Linear(history_dim, hidden), nn.SiLU(), nn.Linear(hidden, hidden), nn.SiLU())
                extra = hidden
            if variant in {"full_history", "full_history_aux"}:
                self.hist_rnn = nn.GRU(history_dim, hidden, batch_first=True)
                extra = hidden
                if variant == "full_history_aux":
                    self.property_head = nn.Linear(hidden, 4)
            if variant == "system_id":
                self.property_encoder = nn.Sequential(
                    nn.Linear(history_dim, hidden), nn.SiLU(), nn.Linear(hidden, hidden), nn.SiLU()
                )
                self.property_head = nn.Linear(hidden, 4)
                # Posterior mean and uncertainty are both passed to dynamics.
                extra = 4
            self.net = nn.Sequential(
                nn.Linear(query_dim + extra, hidden),
                nn.SiLU(),
                nn.Linear(hidden, hidden),
                nn.SiLU(),
                nn.Linear(hidden, hidden),
                nn.SiLU(),
                nn.Linear(hidden, 2 * target_dim),
            )

        def forward(self, query, history, props):
            parts = [query]
            auxiliary = None
            if self.variant == "oracle":
                parts.append(props)
            elif self.variant in {"fingerprint", "global_history", "shuffled_history"}:
                h = self.hist_encoder(history).mean(dim=-2)
                parts.append(h)
            elif self.variant in {"full_history", "full_history_aux"}:
                _, h = self.hist_rnn(history)
                parts.append(h[-1])
                if self.variant == "full_history_aux":
                    posterior = self.property_head(h[-1])
                    auxiliary = (posterior[:, :2], torch.clamp(posterior[:, 2:], -4.0, 2.0))
            elif self.variant == "system_id":
                h = self.property_encoder(history).mean(dim=-2)
                posterior = self.property_head(h)
                prop_mean = posterior[:, :2]
                prop_logscale = torch.clamp(posterior[:, 2:], -4.0, 2.0)
                # The effect loss is not allowed to turn the property
                # posterior into an unconstrained hidden history channel.
                parts.extend([prop_mean.detach(), prop_logscale.detach()])
                auxiliary = (prop_mean, prop_logscale)
            return self.net(torch.cat(parts, dim=-1)), auxiliary

    return EffectModel()


@dataclass
class TrainConfig:
    variant: str
    seed: int
    epochs: int
    batch_size: int
    hidden: int
    learning_rate: float
    weight_decay: float
    patience: int
    property_weight: float
    fixed_epochs: bool


def train_model(args: argparse.Namespace) -> None:
    import torch
    from torch.utils.data import DataLoader, TensorDataset

    seed_everything(args.seed)
    data = load_data(args.data)
    train_ep = np.where(data["split"] == 0)[0]
    val_ep = np.where(data["split"] == 1)[0]
    test_ep = np.where(data["split"] == 2)[0]
    n = data["query"].shape[1]
    train_mask = np.repeat(train_ep, n)
    train_ids = np.tile(np.arange(n), len(train_ep))
    q_train = data["query"][train_mask, train_ids]
    h_train = data["history"][train_mask, train_ids]
    p_train = data["properties"][train_mask, train_ids]
    y_train = data["target_delta"][train_mask, train_ids]

    q_norm = Normalizer(q_train)
    h_norm = Normalizer(h_train.reshape(-1, h_train.shape[-1]))
    p_norm = Normalizer(p_train)
    y_norm = Normalizer(y_train)

    def prepared(ep_idx: np.ndarray, training: bool = False):
        eps = np.repeat(ep_idx, n)
        ids = np.tile(np.arange(n), len(ep_idx))
        q = q_norm.apply(data["query"][eps, ids])
        h = h_norm.apply(data["history"][eps, ids])
        if args.variant == "global_history":
            global_h = h_norm.apply(data["history"][ep_idx]).mean(axis=1)
            h = np.repeat(global_h, n, axis=0)
        elif args.variant == "shuffled_history":
            shifted = (ids + 1) % n
            h = h_norm.apply(data["history"][eps, shifted])
        p = p_norm.apply(data["properties"][eps, ids])
        y = y_norm.apply(data["target_delta"][eps, ids])
        return [x.astype(np.float32) for x in (q, h, p, y)]

    qtr, htr, ptr, ytr = prepared(train_ep, True)
    qv, hv, pv, yv = prepared(val_ep)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    target_dim = ytr.shape[-1]
    model = build_model(args.variant, qtr.shape[-1], htr.shape[-1], target_dim, args.hidden).to(device)
    config = TrainConfig(
        args.variant,
        args.seed,
        args.epochs,
        args.batch_size,
        args.hidden,
        args.learning_rate,
        args.weight_decay,
        args.patience,
        args.property_weight,
        args.fixed_epochs,
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)
    loader = DataLoader(
        TensorDataset(*(torch.from_numpy(x) for x in (qtr, htr, ptr, ytr))),
        batch_size=args.batch_size,
        shuffle=True,
        generator=torch.Generator().manual_seed(args.seed),
        num_workers=0,
    )
    val_tensors = [torch.from_numpy(x).to(device) for x in (qv, hv, pv, yv)]
    best_state = None
    best_val = float("inf")
    stale = 0
    history_log = []
    optimizer_steps = 0
    started = time.time()
    for epoch in range(args.epochs):
        model.train()
        train_losses = []
        for qb, hb, pb, yb in loader:
            qb, hb, pb, yb = [x.to(device, non_blocking=True) for x in (qb, hb, pb, yb)]
            out, auxiliary = model(qb, hb, pb)
            mean, raw_scale = out[:, :target_dim], out[:, target_dim:]
            log_scale = torch.clamp(raw_scale, -4.0, 3.0)
            loss = (0.5 * ((yb - mean) / torch.exp(log_scale)) ** 2 + log_scale).mean()
            if auxiliary is not None:
                prop_mean, prop_logscale = auxiliary
                property_nll = (0.5 * ((pb - prop_mean) / torch.exp(prop_logscale)) ** 2 + prop_logscale).mean()
                loss = loss + args.property_weight * property_nll
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            optimizer_steps += 1
            train_losses.append(float(loss.detach().cpu()))
        model.eval()
        with torch.no_grad():
            out, auxiliary = model(*val_tensors[:3])
            mean, raw_scale = out[:, :target_dim], out[:, target_dim:]
            log_scale = torch.clamp(raw_scale, -4.0, 3.0)
            val_loss = float((0.5 * ((val_tensors[3] - mean) / torch.exp(log_scale)) ** 2 + log_scale).mean().cpu())
        record = {"epoch": epoch, "train_loss": float(np.mean(train_losses)), "val_loss": val_loss}
        history_log.append(record)
        print(json.dumps({"event": "epoch", **record}), flush=True)
        if val_loss < best_val - 1e-5:
            best_val = val_loss
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            stale = 0
        else:
            stale += 1
            if stale >= args.patience and not args.fixed_epochs:
                break
    if args.fixed_epochs:
        # Main comparisons use the state after exactly the registered number
        # of optimizer steps; per-variant checkpoint cherry-picking is banned.
        best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        best_val = history_log[-1]["val_loss"]
    assert best_state is not None
    model.load_state_dict(best_state)

    def predict(ep_idx: np.ndarray):
        q, h, p, _ = prepared(ep_idx)
        model.eval()
        means, scales, property_means, property_scales = [], [], [], []
        with torch.no_grad():
            for start in range(0, len(q), 4096):
                tensors = [torch.from_numpy(x[start : start + 4096]).to(device) for x in (q, h, p)]
                out, auxiliary = model(*tensors)
                out = out.cpu().numpy()
                means.append(out[:, :target_dim])
                scales.append(np.exp(np.clip(out[:, target_dim:], -4.0, 3.0)))
                if auxiliary is not None:
                    property_means.append(auxiliary[0].cpu().numpy())
                    property_scales.append(np.exp(auxiliary[1].cpu().numpy()))
        mean = np.concatenate(means) * y_norm.std + y_norm.mean
        scale = np.concatenate(scales) * y_norm.std
        prop_mean = np.concatenate(property_means).reshape(len(ep_idx), n, 2) if property_means else None
        prop_scale = np.concatenate(property_scales).reshape(len(ep_idx), n, 2) if property_scales else None
        return mean.reshape(len(ep_idx), n, target_dim), scale.reshape(len(ep_idx), n, target_dim), prop_mean, prop_scale

    val_mean, val_scale, _, _ = predict(val_ep)
    val_residual = data["target_delta"][val_ep] - val_mean
    floor = np.full(target_dim, 0.005, dtype=np.float32)
    val_scale = np.maximum(val_scale, floor)
    calibration_factor = np.sqrt(np.mean((val_residual / val_scale) ** 2, axis=(0, 1)))
    calibration_factor = np.clip(calibration_factor, 0.25, 4.0)
    test_mean, test_scale, test_property_mean, test_property_scale = predict(test_ep)
    calibrated_sigma = np.maximum(test_scale * calibration_factor, floor)
    predicted_post = data["pre_pose"][test_ep] + test_mean
    result: dict[str, Any] = {
        "config": asdict(config),
        "device": str(device),
        "gpu_name": torch.cuda.get_device_name() if torch.cuda.is_available() else None,
        "best_val_nll": best_val,
        "epochs_completed": len(history_log),
        "wall_sec": time.time() - started,
        "parameter_count": sum(p.numel() for p in model.parameters()),
        "optimizer_steps": optimizer_steps,
        "dataset_sha256": hashlib.sha256(Path(args.data).read_bytes()).hexdigest(),
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "calibration_factor": calibration_factor.tolist(),
        "splits": {},
    }
    if test_property_mean is not None and test_property_scale is not None:
        property_truth = p_norm.apply(data["properties"][test_ep])
        property_z = (property_truth - test_property_mean) / np.maximum(test_property_scale, 1e-5)
        result["property_posterior"] = {
            "normalized_rmse": np.sqrt(np.mean((property_truth - test_property_mean) ** 2, axis=(0, 1))).tolist(),
            "normalized_nll": float(np.mean(0.5 * property_z**2 + np.log(np.maximum(test_property_scale, 1e-5)))),
            "coverage_1sigma": np.mean(np.abs(property_z) <= 1.0, axis=(0, 1)).tolist(),
            "coverage_2sigma": np.mean(np.abs(property_z) <= 2.0, axis=(0, 1)).tolist(),
        }
    for name, mask in {
        "all": np.ones(len(test_ep), dtype=bool),
        "heterogeneous_id": data["regime"][test_ep] == 0,
        "homogeneous_control": data["regime"][test_ep] == 1,
        "heterogeneous_ood": data["regime"][test_ep] == 2,
        "hard_id": (data["regime"][test_ep] == 0) & (data["hard_id"][test_ep] == 1),
    }.items():
        if not mask.any():
            continue
        ids = test_ep[mask]
        result["splits"][name] = assignment_metrics(
            predicted_post[mask],
            calibrated_sigma[mask],
            data["post_detection"][ids],
            data["id_to_detection"][ids],
            data["decision_target"][ids],
        )
        true_delta = data["target_delta"][ids]
        pred_delta = test_mean[mask]
        result["splits"][name]["effect_rmse"] = np.sqrt(np.mean((true_delta - pred_delta) ** 2, axis=(0, 1))).tolist()

    zero_delta = np.zeros_like(data["target_delta"][test_ep])
    pose_sigma = np.maximum(data["target_delta"][val_ep].reshape(-1, target_dim).std(axis=0), floor)
    result["pose_only_baseline"] = assignment_metrics(
        data["pre_pose"][test_ep] + zero_delta,
        pose_sigma,
        data["post_detection"][test_ep],
        data["id_to_detection"][test_ep],
        data["decision_target"][test_ep],
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    ckpt = out.with_suffix(".pt")
    torch.save(
        {
            "model": best_state,
            "config": asdict(config),
            "normalizers": {
                "query": [q_norm.mean, q_norm.std],
                "history": [h_norm.mean, h_norm.std],
                "properties": [p_norm.mean, p_norm.std],
                "target": [y_norm.mean, y_norm.std],
            },
            "calibration_factor": calibration_factor,
        },
        ckpt,
    )
    print(json.dumps({"event": "complete", "output": str(out), "checkpoint": str(ckpt), "best_val": best_val}))


def summarize(args: argparse.Namespace) -> None:
    # Only registered main-run ids are aggregated.  Smoke/audit JSON files in
    # the same directory must never contaminate the three-seed gate.
    paths = sorted(Path(args.results_dir).glob("R*.json"))
    rows = []
    seen: set[tuple[str, int]] = set()
    for p in paths:
        try:
            result = json.loads(p.read_text(encoding="utf-8"))
            cfg = result["config"]
            split = result["splits"].get(args.split)
            if split:
                key = (cfg["variant"], int(cfg["seed"]))
                if key in seen:
                    raise RuntimeError(f"duplicate variant/seed result: {key}")
                seen.add(key)
                rows.append(
                    {
                        "file": p.name,
                        "variant": cfg["variant"],
                        "seed": cfg["seed"],
                        "dataset_sha256": result["dataset_sha256"],
                        "code_sha256": result["code_sha256"],
                        "optimizer_steps": result["optimizer_steps"],
                        "fixed_epochs": cfg["fixed_epochs"],
                        "parameter_count": result["parameter_count"],
                        "config_signature": {
                            k: cfg[k]
                            for k in ("epochs", "batch_size", "hidden", "learning_rate", "weight_decay", "property_weight", "fixed_epochs")
                        },
                        "assignment_accuracy": split["assignment_accuracy"],
                        "wrong_target_rate": split["wrong_target_rate"],
                        "posterior_nll": split["posterior_nll"],
                    }
                )
        except (KeyError, json.JSONDecodeError):
            continue
    variants: dict[str, dict[str, Any]] = {}
    for variant in sorted({r["variant"] for r in rows}):
        vr = [r for r in rows if r["variant"] == variant]
        variants[variant] = {
            "n_seeds": len(vr),
            "assignment_accuracy_mean": float(np.mean([r["assignment_accuracy"] for r in vr])),
            "assignment_accuracy_std": float(np.std([r["assignment_accuracy"] for r in vr])),
            "wrong_target_rate_mean": float(np.mean([r["wrong_target_rate"] for r in vr])),
            "posterior_nll_mean": float(np.mean([r["posterior_nll"] for r in vr])),
        }
    gate = {"status": "inconclusive", "reason": f"{args.stage} registered results incomplete"}

    def validate_comparability(names: list[str]) -> None:
        selected = [r for r in rows if r["variant"] in names]
        hashes = {r["dataset_sha256"] for r in selected}
        if len(hashes) != 1:
            raise RuntimeError(f"dataset hash mismatch: {hashes}")
        code_hashes = {r["code_sha256"] for r in selected}
        if len(code_hashes) != 1:
            raise RuntimeError(f"code hash mismatch: {code_hashes}")
        config_signatures = {json.dumps(r["config_signature"], sort_keys=True) for r in selected}
        if len(config_signatures) != 1:
            raise RuntimeError(f"training config mismatch: {config_signatures}")
        if not all(r["fixed_epochs"] for r in selected):
            raise RuntimeError("main gate requires fixed epochs")
        by_variant = {name: {r["seed"]: r for r in selected if r["variant"] == name} for name in names}
        common = set.intersection(*(set(x) for x in by_variant.values()))
        if len(common) < args.required_seeds:
            raise RuntimeError(f"fewer than {args.required_seeds} common unique seeds")
        for seed in common:
            steps = {by_variant[name][seed]["optimizer_steps"] for name in names}
            if len(steps) != 1:
                raise RuntimeError(f"optimizer step mismatch at seed {seed}: {steps}")

    full_candidates = [name for name in ("full_history", "full_history_aux") if variants.get(name, {}).get("n_seeds", 0) >= args.required_seeds]
    if args.stage == "method" and variants.get("system_id", {}).get("n_seeds", 0) >= args.required_seeds and full_candidates:
        baseline_name = max(full_candidates, key=lambda name: variants[name]["assignment_accuracy_mean"])
        validate_comparability(["system_id", baseline_name])
        method_rows = {r["seed"]: r for r in rows if r["variant"] == "system_id"}
        base_rows = {r["seed"]: r for r in rows if r["variant"] == baseline_name}
        common_seeds = sorted(set(method_rows) & set(base_rows))
        paired_gains = [method_rows[s]["assignment_accuracy"] - base_rows[s]["assignment_accuracy"] for s in common_seeds]
        if variants[baseline_name]["n_seeds"] >= args.required_seeds:
            baseline_params = min(r["parameter_count"] for r in rows if r["variant"] == baseline_name)
            system_params = max(r["parameter_count"] for r in rows if r["variant"] == "system_id")
            if baseline_params < system_params:
                raise RuntimeError(f"full-history baseline has fewer parameters: {baseline_params} < {system_params}")
        gain = variants["system_id"]["assignment_accuracy_mean"] - variants[baseline_name]["assignment_accuracy_mean"]
        base_wrong = variants[baseline_name]["wrong_target_rate_mean"]
        method_wrong = variants["system_id"]["wrong_target_rate_mean"]
        wrong_reduction = base_wrong - method_wrong
        relative_wrong_reduction = wrong_reduction / max(base_wrong, 1e-8)
        gate = {
            "status": "pass" if gain >= args.method_min_gain and relative_wrong_reduction >= args.min_relative_wrong_reduction and all(x > 0 for x in paired_gains) else "kill",
            "stage": "method",
            "strongest_full_history_baseline": baseline_name,
            "assignment_gain": gain,
            "wrong_target_absolute_reduction": wrong_reduction,
            "wrong_target_relative_reduction": relative_wrong_reduction,
            "paired_seed_assignment_gains": dict(zip(common_seeds, paired_gains)),
            "criterion": f"gain>={args.method_min_gain} and relative wrong-target reduction>={args.min_relative_wrong_reduction}",
        }
    elif args.stage == "headroom" and variants.get("shared", {}).get("n_seeds", 0) >= args.required_seeds and variants.get("oracle", {}).get("n_seeds", 0) >= args.required_seeds:
        validate_comparability(["shared", "oracle"])
        shared_rows = {r["seed"]: r for r in rows if r["variant"] == "shared"}
        oracle_rows = {r["seed"]: r for r in rows if r["variant"] == "oracle"}
        common_seeds = sorted(set(shared_rows) & set(oracle_rows))
        paired_gains = [oracle_rows[s]["assignment_accuracy"] - shared_rows[s]["assignment_accuracy"] for s in common_seeds]
        gain = variants["oracle"]["assignment_accuracy_mean"] - variants["shared"]["assignment_accuracy_mean"]
        wrong_reduction = variants["shared"]["wrong_target_rate_mean"] - variants["oracle"]["wrong_target_rate_mean"]
        gate = {
            "status": "pass" if gain >= args.min_gain and wrong_reduction > 0 and all(x > 0 for x in paired_gains) else "kill",
            "stage": "privileged-headroom",
            "assignment_gain": gain,
            "wrong_target_absolute_reduction": wrong_reduction,
            "paired_seed_assignment_gains": dict(zip(common_seeds, paired_gains)),
            "criterion": f"privileged gain>={args.min_gain}; passing does not support IFB",
        }
    summary = {"split": args.split, "rows": rows, "variants": variants, "gate": gate}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def smoke(args: argparse.Namespace) -> None:
    seed_everything(args.seed)
    world = PushWorld(args.num_objects)
    rng = np.random.default_rng(args.seed)
    masses, frictions = sample_properties(rng, 0, args.num_objects)
    pre, action, post, diagnostics = world.run_trial(rng, masses, frictions, move_steps=40, settle_steps=40)
    assert pre.shape == (args.num_objects, 6)
    assert post.shape == (args.num_objects, 6)
    assert np.isfinite(pre).all() and np.isfinite(post).all()
    assert action.shape == (5,)
    max_move = float(np.linalg.norm(post[:, :2] - pre[:, :2], axis=1).max())
    assert diagnostics["contact_count"] > 0, "pusher made no object contact"
    assert max_move > 0.002, "contact produced no measurable object motion"
    masses2, frictions2 = sample_properties(rng, 0, args.num_objects)
    pre2, _, post2, control = world.run_trial(rng, masses2, frictions2, move_steps=40, settle_steps=40, enable_pusher=False)
    control_move = float(np.linalg.norm(post2[:, :2] - pre2[:, :2], axis=1).max())
    assert control["contact_count"] == 0
    assert control_move < 0.01, f"no-pusher control moved unexpectedly: {control_move}"
    print(json.dumps({"event": "WITNESS", "pre_shape": list(pre.shape), "contact_count": diagnostics["contact_count"], "max_move": max_move, "no_pusher_max_move": control_move}))


def audit_dataset(args: argparse.Namespace) -> None:
    data = load_data(args.data)
    n = data["query"].shape[1]
    assert np.all(np.sort(data["id_to_detection"], axis=1) == np.arange(n)), "invalid detection permutation"
    group_reports = {}
    max_perm_bias = 0.0
    max_abs_correlation = 0.0
    group_failures = []
    for split in sorted(np.unique(data["split"])):
        for regime in sorted(np.unique(data["regime"])):
            mask = (data["split"] == split) & (data["regime"] == regime)
            if mask.sum() < max(20, n * 5):
                continue
            freq = np.zeros((n, n), np.float64)
            for i in range(n):
                freq[i] = np.bincount(data["id_to_detection"][mask, i], minlength=n) / mask.sum()
            group_bias = float(np.max(np.abs(freq - 1.0 / n)))
            correlations = []
            for pidx in range(2):
                for xy in range(2):
                    correlations.append(float(np.corrcoef(data["properties"][mask, :, pidx].ravel(), data["sampled_layout"][mask, :, xy].ravel())[0, 1]))
            group_corr = float(np.nanmax(np.abs(correlations)))
            perm_tolerance = max(args.max_permutation_bias, 4.0 * math.sqrt((1.0 / n) * (1.0 - 1.0 / n) / mask.sum()))
            correlation_tolerance = max(args.max_correlation, 4.0 / math.sqrt(mask.sum() * n))
            group_reports[f"split{split}_regime{regime}"] = {
                "episodes": int(mask.sum()),
                "permutation_bias": group_bias,
                "permutation_tolerance": perm_tolerance,
                "max_abs_property_position_correlation": group_corr,
                "correlation_tolerance": correlation_tolerance,
                "correlation_is_identity_gate": bool(regime != 1),
            }
            # In homogeneous regime 1 every address in an episode has exactly
            # the same properties.  Episode-level property/settling-position
            # correlation cannot encode within-episode identity; retain it as
            # a reported nuisance diagnostic, but do not treat it as an
            # identity-leak gate. Detection permutation always remains gated.
            if group_bias >= perm_tolerance or (regime != 1 and group_corr >= correlation_tolerance):
                group_failures.append(f"split{split}_regime{regime}")
            max_perm_bias = max(max_perm_bias, group_bias)
            max_abs_correlation = max(max_abs_correlation, group_corr)
    props = data["properties"]
    heterogeneous = props[data["regime"] == 0]
    duplicate_fraction = float(
        np.mean(
            [
                len({tuple(np.round(x, 6)) for x in episode}) < n
                for episode in heterogeneous
            ]
        )
    )
    assert np.allclose(data["body_properties"][np.arange(len(props))[:, None], data["address_to_body"]], props), "address/body property mapping is misaligned"
    # A simultaneous relabeling cannot change pose-only assignment accuracy.
    sample = min(args.samples, len(data["pre_pose"]))
    idx = np.arange(sample)
    sigma = np.asarray([0.05, 0.05])
    base = assignment_metrics(data["pre_pose"][idx], sigma, data["post_detection"][idx], data["id_to_detection"][idx], data["decision_target"][idx])
    rng = np.random.default_rng(args.seed)
    permuted_pre = np.empty_like(data["pre_pose"][idx])
    permuted_truth = np.empty_like(data["id_to_detection"][idx])
    permuted_target = np.empty_like(data["decision_target"][idx])
    for e in range(sample):
        p = rng.permutation(n)
        permuted_pre[e] = data["pre_pose"][idx[e], p]
        permuted_truth[e] = data["id_to_detection"][idx[e], p]
        permuted_target[e] = int(np.where(p == data["decision_target"][idx[e]])[0][0])
    permuted = assignment_metrics(permuted_pre, sigma, data["post_detection"][idx], permuted_truth, permuted_target)
    equivariance_error = float(np.max(np.abs(np.asarray(base["per_episode_accuracy"]) - np.asarray(permuted["per_episode_accuracy"]))))
    contact_rate = float(np.mean(data["contact_count"] > 0))
    context_contact_rate = float(np.mean(data["context_contact_count"] > 0))
    hard_count = int(np.sum((data["split"] == 2) & (data["hard_id"] == 1) & (data["regime"] == 0)))
    settle_q99 = float(np.quantile(data["settle_displacement"], 0.99))
    settle_max = float(np.max(data["settle_displacement"]))
    pairwise_minima = []
    for layout in data["sampled_layout"]:
        pairwise_minima.append(min(float(np.linalg.norm(layout[i] - layout[j])) for i in range(n) for j in range(i + 1, n)))
    sampled_layout_min_distance = float(np.min(pairwise_minima))
    report = {
        "episodes": int(len(data["query"])),
        "num_objects": int(n),
        "max_detection_permutation_bias": max_perm_bias,
        "max_abs_property_position_correlation": max_abs_correlation,
        "duplicate_property_episode_fraction": duplicate_fraction,
        "permutation_equivariance_error": float(equivariance_error),
        "pusher_contact_rate": contact_rate,
        "context_pusher_contact_rate": context_contact_rate,
        "hard_id_test_count": hard_count,
        "settle_displacement_q99": settle_q99,
        "settle_displacement_max": settle_max,
        "sampled_layout_min_pairwise_distance": sampled_layout_min_distance,
        "groups": group_reports,
        "group_failures": group_failures,
        "pass": bool(not group_failures and duplicate_fraction > 0.1 and equivariance_error < 1e-7 and contact_rate > 0.95 and context_contact_rate > 0.95 and hard_count >= args.min_hard and settle_q99 < args.max_settle_q99 and sampled_layout_min_distance >= 0.0999),
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise SystemExit(2)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)
    ps = sub.add_parser("smoke")
    ps.add_argument("--seed", type=int, default=7)
    ps.add_argument("--num-objects", type=int, default=3)
    ps.set_defaults(func=smoke)

    pg = sub.add_parser("generate")
    pg.add_argument("--output", required=True)
    pg.add_argument("--episodes", type=int, default=12000)
    pg.add_argument("--num-objects", type=int, default=3)
    pg.add_argument("--context-steps", type=int, default=3)
    pg.add_argument("--seed", type=int, default=20260829)
    pg.set_defaults(func=generate_dataset)

    pt = sub.add_parser("train")
    pt.add_argument("--data", required=True)
    pt.add_argument("--output", required=True)
    pt.add_argument("--variant", choices=["shared", "oracle", "system_id", "full_history", "full_history_aux", "fingerprint", "global_history", "shuffled_history"], required=True)
    pt.add_argument("--seed", type=int, required=True)
    pt.add_argument("--epochs", type=int, default=100)
    pt.add_argument("--batch-size", type=int, default=1024)
    pt.add_argument("--hidden", type=int, default=256)
    pt.add_argument("--learning-rate", type=float, default=3e-4)
    pt.add_argument("--weight-decay", type=float, default=1e-5)
    pt.add_argument("--patience", type=int, default=15)
    pt.add_argument("--property-weight", type=float, default=0.25)
    pt.add_argument("--fixed-epochs", action="store_true")
    pt.set_defaults(func=train_model)

    pm = sub.add_parser("summarize")
    pm.add_argument("--results-dir", required=True)
    pm.add_argument("--output", required=True)
    pm.add_argument("--split", default="heterogeneous_id")
    pm.add_argument("--stage", choices=["headroom", "method"], required=True)
    pm.add_argument("--required-seeds", type=int, default=3)
    pm.add_argument("--min-gain", type=float, default=0.05)
    pm.add_argument("--method-min-gain", type=float, default=0.03)
    pm.add_argument("--min-relative-wrong-reduction", type=float, default=0.15)
    pm.set_defaults(func=summarize)

    pa = sub.add_parser("audit")
    pa.add_argument("--data", required=True)
    pa.add_argument("--output", required=True)
    pa.add_argument("--samples", type=int, default=500)
    pa.add_argument("--seed", type=int, default=1701)
    pa.add_argument("--max-permutation-bias", type=float, default=0.04)
    pa.add_argument("--max-correlation", type=float, default=0.05)
    pa.add_argument("--min-hard", type=int, default=50)
    pa.add_argument("--max-settle-q99", type=float, default=0.02)
    pa.set_defaults(func=audit_dataset)
    return p


if __name__ == "__main__":
    cli = parser()
    ns = cli.parse_args()
    ns.func(ns)
