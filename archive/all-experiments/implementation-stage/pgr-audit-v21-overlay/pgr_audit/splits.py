"""Exact task-local episode allocation frozen by PGR-Audit v2.1."""

from __future__ import annotations

import hashlib
import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass


SEED = 1701


@dataclass(frozen=True)
class TaskSplit:
    task: int
    outer: dict[str, tuple[int, ...]]
    head: dict[str, tuple[int, ...]]
    post: dict[str, tuple[int, ...]]
    head_nuisance_cv: dict[str, tuple[int, ...]]


def _hash_key(task: int, episode: int, stream: str) -> tuple[str, int]:
    material = f"PGR-Audit-v2|task={task}|episode={episode}|stream={stream}|seed={SEED}".encode("utf-8")
    return hashlib.sha256(material).hexdigest(), episode


def _counts(
    n: int,
    labels: Sequence[str],
    minima: Sequence[int],
    proportions: Sequence[float],
) -> dict[str, int]:
    if not (len(labels) == len(minima) == len(proportions)):
        raise ValueError("labels, minima, and proportions must have equal length")
    required = sum(minima)
    if n < required:
        raise ValueError(f"Need at least {required} items, got {n}")
    remainder = n - required
    exact = [remainder * proportion for proportion in proportions]
    extras = [math.floor(value) for value in exact]
    undistributed = remainder - sum(extras)
    order = sorted(range(len(labels)), key=lambda index: (-(exact[index] - extras[index]), index))
    for index in order[:undistributed]:
        extras[index] += 1
    result = {label: minimum + extra for label, minimum, extra in zip(labels, minima, extras, strict=True)}
    if sum(result.values()) != n:
        raise AssertionError("Allocator lost items")
    return result


def _assign(
    task: int,
    episodes: Iterable[int],
    *,
    stream: str,
    labels: Sequence[str],
    minima: Sequence[int],
    proportions: Sequence[float],
) -> dict[str, tuple[int, ...]]:
    values = tuple(episodes)
    if len(values) != len(set(values)):
        raise ValueError("Episode IDs must be unique within a task")
    ordered = sorted(values, key=lambda episode: _hash_key(task, episode, stream))
    counts = _counts(len(ordered), labels, minima, proportions)
    result: dict[str, tuple[int, ...]] = {}
    offset = 0
    for label in labels:
        end = offset + counts[label]
        result[label] = tuple(ordered[offset:end])
        offset = end
    return result


def allocate_task(task: int, episodes: Iterable[int]) -> TaskSplit:
    episode_tuple = tuple(episodes)
    if len(episode_tuple) < 29:
        raise ValueError(f"Task {task} has fewer than 29 episodes")
    outer = _assign(
        task,
        episode_tuple,
        stream="outer",
        labels=("head", "adapter", "post"),
        minima=(11, 3, 15),
        proportions=(0.45, 0.30, 0.25),
    )
    head = _assign(
        task,
        outer["head"],
        stream="head",
        labels=("train", "val", "strict_test"),
        minima=(5, 3, 3),
        proportions=(0.60, 0.20, 0.20),
    )
    post = _assign(
        task,
        outer["post"],
        stream="post",
        labels=("fold0", "fold1", "fold2", "fold3", "fold4"),
        minima=(3, 3, 3, 3, 3),
        proportions=(0.30, 0.30, 0.10, 0.10, 0.20),
    )
    head_nuisance_cv = _assign(
        task,
        head["train"],
        stream="head_nuisance_cv",
        labels=("fold0", "fold1", "fold2", "fold3", "fold4"),
        minima=(1, 1, 1, 1, 1),
        proportions=(0.20, 0.20, 0.20, 0.20, 0.20),
    )
    return TaskSplit(task=task, outer=outer, head=head, post=post, head_nuisance_cv=head_nuisance_cv)


def assert_disjoint_complete(source: Iterable[int], groups: dict[str, tuple[int, ...]]) -> None:
    source_set = set(source)
    flat = [episode for group in groups.values() for episode in group]
    if len(flat) != len(set(flat)):
        raise AssertionError("Split groups overlap")
    if set(flat) != source_set:
        raise AssertionError("Split groups are not complete")
