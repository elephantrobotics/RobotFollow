"""Mercury A1 mouse-to-joint-angles example."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from robot_follow.config import load_default_config
from robot_follow.controllers import periodic_interval, run_periodic, send_angles
from robot_follow.robot import configure_motion, connect_mercury, ensure_power, move_to_initial_angles, start_angles_reader
from robot_follow.samplers.mouse import MouseOffsetSampler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mercury A1 mouse joint-angle following")
    parser.add_argument("--config", default="config.json", help="path to config json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_default_config(args.config)
    arm = connect_mercury(cfg.single_arm_port)
    ensure_power(arm)

    initial_angles = list(cfg.a1_initial_angles)
    if not cfg.is_cp_mode():
        move_to_initial_angles(arm, initial_angles, 10)
    configure_motion(arm, cfg.movement_type, vr_mode=cfg.vr_mode)
    start_angles_reader(
        {"single": arm},
        cfg.read_angles_interval_ms,
        enabled=cfg.enable_read_angles,
    )
    sampler = MouseOffsetSampler()

    def step() -> None:
        dx, dy = sampler.offset()
        target = initial_angles.copy()
        target[0] = initial_angles[0] + dx * cfg.mouse_joint_0_scale
        target[3] = initial_angles[3] + dy * cfg.mouse_joint_3_scale
        send_angles(arm, target, cfg.kp)

    run_periodic(step, periodic_interval(cfg.send_interval_ms))


if __name__ == "__main__":
    main()
