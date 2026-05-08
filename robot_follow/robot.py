"""Mercury robot setup helpers used by the examples."""

from __future__ import annotations

import threading
import time


def connect_mercury(port: str):
    """Create a Mercury object lazily so docs can import without hardware libs."""
    from pymycobot import Mercury

    return Mercury(port)


def ensure_power(arm) -> None:
    if arm.is_power_on() is not True:
        arm.power_on()


def configure_motion(arm, movement_type: int, *, vr_mode: bool = True) -> None:
    arm.set_movement_type(movement_type)
    if vr_mode:
        arm.set_vr_mode(1)


def move_to_initial_angles(arm, angles: list[float], speed: int = 10, *, async_move: bool = False) -> None:
    arm.set_movement_type(0)
    try:
        arm.send_angles(angles, speed, _async=async_move)
    except TypeError:
        arm.send_angles(angles, speed)


def start_angles_reader(arms: dict[str, object], interval_ms: float, *, enabled: bool = True) -> None:
    """Print get_angles() at a low rate without buffering samples."""
    if not enabled:
        return

    interval_s = max(0.001, interval_ms * 0.001)

    def read_loop() -> None:
        while True:
            for name, arm in arms.items():
                try:
                    print(f"read_angles_coords,{name},{arm.get_base_coords(),arm.get_angles()}")
                except Exception as exc:
                    print(f"read_angles_error,{name},{exc}")
            time.sleep(interval_s)

    thread = threading.Thread(target=read_loop, daemon=True)
    thread.start()
