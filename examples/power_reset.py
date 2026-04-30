"""Power-cycle Mercury X1/B1 arms in the required order."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from robot_follow.config import load_default_config
from robot_follow.robot import connect_mercury


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mercury dual-arm power reset")
    parser.add_argument("--config", default="config.json", help="path to config json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_default_config(args.config)
    left = connect_mercury(cfg.left_arm_port)
    right = connect_mercury(cfg.right_arm_port)
    right.power_off()
    left.power_off()
    left.power_on()
    right.power_on()


if __name__ == "__main__":
    main()
