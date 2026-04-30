"""Mercury A1 mouse-to-coordinates example."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from robot_follow.config import load_default_config
from robot_follow.controllers import periodic_interval, run_periodic, send_coords
from robot_follow.robot import configure_motion, connect_mercury, ensure_power, move_to_initial_angles, start_angles_reader
from robot_follow.samplers.mouse import MouseOffsetSampler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mercury A1 mouse coordinate following")
    parser.add_argument("--config", default="config.json", help="path to config json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_default_config(args.config)
    arm = connect_mercury(cfg.single_arm_port)
    ensure_power(arm)
    move_to_initial_angles(arm, list(cfg.a1_initial_angles), 10)

    base_coords = arm.get_coords()
    configure_motion(arm, cfg.movement_type, vr_mode=cfg.vr_mode)
    start_angles_reader(
        {"single": arm},
        cfg.read_angles_interval_ms,
        enabled=cfg.enable_read_angles,
    )
    sampler = MouseOffsetSampler()

    def step() -> None:
        dx, dy = sampler.offset()
        target = base_coords.copy()
        target[0] = base_coords[0] + dy * cfg.mouse_coord_x_scale
        target[1] = base_coords[1] + dx * cfg.mouse_coord_y_scale
        send_coords(arm, target, cfg.kp)

    run_periodic(step, periodic_interval(cfg.send_interval_ms))


if __name__ == "__main__":
    main()
