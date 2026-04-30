"""Mercury X1 dual-arm mouse-to-base-coordinates example."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from robot_follow.config import load_default_config
from robot_follow.controllers import periodic_interval, run_periodic, send_base_coords
from robot_follow.robot import configure_motion, connect_mercury, ensure_power, move_to_initial_angles, start_angles_reader
from robot_follow.samplers.mouse import MouseOffsetSampler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mercury X1 mouse base-coordinate following")
    parser.add_argument("--config", default="config.json", help="path to config json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_default_config(args.config)
    left = connect_mercury(cfg.left_arm_port)
    right = connect_mercury(cfg.right_arm_port)
    ensure_power(left)
    ensure_power(right)

    initial_angles = list(cfg.x1_initial_angles)
    move_to_initial_angles(left, initial_angles, 10)
    move_to_initial_angles(right, initial_angles, 10)
    time.sleep(2)

    base_left = left.get_base_coords()
    base_right = right.get_base_coords()
    configure_motion(left, cfg.movement_type, vr_mode=cfg.vr_mode)
    configure_motion(right, cfg.movement_type, vr_mode=cfg.vr_mode)
    start_angles_reader(
        {"left": left, "right": right},
        cfg.read_angles_interval_ms,
        enabled=cfg.enable_read_angles,
    )
    sampler = MouseOffsetSampler()

    def step() -> None:
        dx, dy = sampler.offset()
        target_left = base_left.copy()
        target_right = base_right.copy()
        target_left[1] = base_left[1] + dx * cfg.mouse_x1_scale
        target_left[2] = base_left[2] - dy * cfg.mouse_x1_scale
        target_right[1] = base_right[1] + dx * cfg.mouse_x1_scale
        target_right[2] = base_right[2] - dy * cfg.mouse_x1_scale
        send_base_coords(left, target_left, cfg.kp)
        send_base_coords(right, target_right, cfg.kp)

    run_periodic(step, periodic_interval(cfg.send_interval_ms))


if __name__ == "__main__":
    main()
