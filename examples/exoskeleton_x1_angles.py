"""Mercury X1/B1 exoskeleton-to-joint-angles example."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from robot_follow.config import load_default_config
from robot_follow.controllers import periodic_interval, run_periodic, send_angles
from robot_follow.robot import configure_motion, connect_mercury, ensure_power, start_angles_reader
from robot_follow.samplers.exoskeleton import Exoskeleton


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mercury X1/B1 exoskeleton angle following")
    parser.add_argument("--config", default="config.json", help="path to config json")
    return parser.parse_args()


def map_exoskeleton_to_mercury(arm_data: list[float]) -> list[float]:
    return [
        arm_data[0],
        -arm_data[1],
        arm_data[2],
        -arm_data[3],
        arm_data[4],
        135 + arm_data[5],
        arm_data[6],
    ]


def main() -> None:
    args = parse_args()
    cfg = load_default_config(args.config)
    exoskeleton = Exoskeleton(port=cfg.exoskeleton_port)
    left = connect_mercury(cfg.left_arm_port)
    right = connect_mercury(cfg.right_arm_port)
    ensure_power(left)
    ensure_power(right)
    configure_motion(left, cfg.movement_type, vr_mode=cfg.vr_mode)
    configure_motion(right, cfg.movement_type, vr_mode=cfg.vr_mode)
    if cfg.enable_gripper:
        left.set_gripper_mode(0)
        right.set_gripper_mode(0)
    start_angles_reader(
        {"left": left, "right": right},
        cfg.read_angles_interval_ms,
        enabled=cfg.enable_read_angles,
    )

    def step() -> None:
        for arm_id, robot in ((1, left), (2, right)):
            arm_data = exoskeleton.get_arm_data(arm_id)
            if arm_data is None:
                return
            target_angles = map_exoskeleton_to_mercury(arm_data)
            if cfg.enable_gripper and arm_data[9] == 0:
                robot.set_gripper_state(1, 100)
            elif cfg.enable_gripper and arm_data[10] == 0:
                robot.set_gripper_state(0, 100)
            send_angles(robot, target_angles, cfg.kp)

    run_periodic(step, periodic_interval(cfg.send_interval_ms))


if __name__ == "__main__":
    main()
