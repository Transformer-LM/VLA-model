"""Default-deny real-robot adapter.

The frozen v2.1 bundle authorizes offline contract preparation only. It exposes
no network or motion implementation.
"""

from __future__ import annotations


class LiveRobotNotAuthorized(PermissionError):
    pass


class LockedRobotAdapter:
    live_action_authorized = False
    endpoint_allowlist: tuple[str, ...] = ()

    @staticmethod
    def _deny(operation: str) -> None:
        raise LiveRobotNotAuthorized(
            f"{operation} is not authorized by PGR-Audit v2.1; a separate exact robot contract and jury are required"
        )

    def connect(self, *args, **kwargs):
        self._deny("robot connectivity")

    def observe(self, *args, **kwargs):
        self._deny("robot probing")

    def command(self, *args, **kwargs):
        self._deny("robot command")

    def move(self, *args, **kwargs):
        self._deny("robot motion")
