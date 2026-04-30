"""Periodic send loops used by teleoperation examples."""

from __future__ import annotations

from collections.abc import Callable
import time


def run_periodic(step: Callable[[], None], interval_s: float) -> None:
    """Run a best-effort periodic loop until interrupted."""
    try:
        while True:
            start = time.time()
            step()
            elapsed = time.time() - start
            time.sleep(max(0.0, interval_s - elapsed))
    except KeyboardInterrupt:
        print("RobotFollow stopped")


def send_angles(arm, target: list[float], kp: int, *, async_send: bool = True) -> None:
    arm.send_angles(target, kp, _async=async_send)


def send_coords(arm, target: list[float], kp: int, *, async_send: bool = True) -> None:
    arm.send_coords(target, kp, _async=async_send)


def send_base_coords(arm, target: list[float], kp: int, *, async_send: bool = True) -> None:
    arm.send_base_coords(target, kp, _async=async_send)


def periodic_interval(send_interval_ms: float) -> float:
    return max(0.0, send_interval_ms * 0.001)
