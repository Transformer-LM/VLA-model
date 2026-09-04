"""One-retry infrastructure ledger with terminal scientific semantics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FailureClass(str, Enum):
    LAUNCHER_TRANSPORT_BEFORE_EXEC_ACK = "launcher_transport_before_exec_ack"
    CUDA_CONTEXT_BEFORE_SCIENTIFIC_READ = "cuda_context_before_scientific_read"
    PERSONAL_STORAGE_TRANSIENT_BEFORE_UPDATE = "personal_storage_transient_before_update"
    SIMULATION_RESET_BEFORE_POLICY_ACTION = "simulation_reset_before_policy_action"
    REAL_TRANSPORT_BEFORE_TASK_ACTION = "real_transport_before_task_action"


@dataclass(frozen=True)
class RetryDecision:
    allowed: bool
    next_attempt_no: int | None
    terminal_missing: bool
    reason: str


def decide_retry(
    *,
    attempt_no: int,
    failure_class: str,
    hashes_unchanged: bool,
    same_seed_and_condition: bool,
    scientific_input_read: bool,
    optimizer_update_or_policy_action: bool,
) -> RetryDecision:
    try:
        classified = FailureClass(failure_class)
    except ValueError:
        return RetryDecision(False, None, True, "unlisted failure class")

    if not hashes_unchanged or not same_seed_and_condition:
        return RetryDecision(False, None, True, "changed code/config/input/seed/condition requires a new logical run")
    if optimizer_update_or_policy_action:
        return RetryDecision(False, None, True, "failure occurred after optimizer update or policy action")
    if attempt_no == 1:
        if classified is FailureClass.CUDA_CONTEXT_BEFORE_SCIENTIFIC_READ and scientific_input_read:
            return RetryDecision(False, None, True, "CUDA retry class requires failure before scientific read")
        return RetryDecision(True, 2, False, "single unchanged technical retry")
    return RetryDecision(False, None, True, "one technical retry already consumed; claim gate permanently fails")
