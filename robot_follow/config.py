"""Configuration loading for RobotFollow examples."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATH = Path("config.json")


@dataclass
class RobotFollowConfig:
    single_arm_port: str = "/dev/ttyAMA1"
    left_arm_port: str = "/dev/left_arm"
    right_arm_port: str = "/dev/right_arm"
    exoskeleton_port: str = "/dev/ttyACM2"
    send_interval_ms: float = 10.0
    movement_type: int = 4
    kp: int = 16
    enable_read_angles: bool = True
    read_angles_interval_ms: float = 100.0
    vr_mode: bool = True
    enable_gripper: bool = True
    mouse_coord_x_scale: float = -0.15
    mouse_coord_y_scale: float = -0.15
    mouse_joint_0_scale: float = -0.05
    mouse_joint_3_scale: float = -0.05
    mouse_x1_scale: float = 0.3
    a1_initial_angles: tuple[float, ...] = (0, 0, 0, -90, 0, 90, 0)
    x1_initial_angles: tuple[float, ...] = (0, 30, 0, -120, 0, 90, 0)

    def is_cp_mode(self) -> bool:
        return self.movement_type == 4


def load_config(path: str | Path) -> RobotFollowConfig:
    with Path(path).open("r", encoding="utf-8") as config_file:
        data: dict[str, Any] = json.load(config_file)
    for key in ("a1_initial_angles", "x1_initial_angles"):
        if key in data:
            data[key] = tuple(data[key])
    return RobotFollowConfig(**data)


def load_default_config(path: str | Path = DEFAULT_CONFIG_PATH) -> RobotFollowConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file '{config_path}' not found. Copy config.example.json to "
            "config.json and adjust ports before running examples."
        )
    return load_config(config_path)
