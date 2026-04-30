"""Simulate the online PID step planner used by PID_CONTROL::CPInterpolation.

Run from the project root:

    python scripts/sim_pid_step.py

The script assumes ideal feedback: each returned position is fed back as the
next cycle's current_pos. Tune the constants below to match the joint or
Cartesian CP path you want to inspect.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi
from random import Random

import matplotlib.pyplot as plt


CONTROL_TIME_MS = 7.0
FREQUENCY = 1000.0 / CONTROL_TIME_MS

KP = 12.0      # 或先降到 15.0
KI = 0.0
KD = 0.05      # 先加一点阻尼

MAX_SPEED_DEG_S = 300.0
MAX_ACCEL_DEG_S2 = 1000.0

INITIAL_POS = 0.0
TARGET_COUNT = 100
TARGET_MIN = 0.5
TARGET_MAX = 1.5
INTERVAL_MIN_MS = 40.0
INTERVAL_MAX_MS = 300.0
TELEOP_TARGET_START = 1.0
TELEOP_MAX_TARGET_SPEED = 1.2
TELEOP_NOISE_RAD = 0.015
RANDOM_SEED = 7
SETTLE_TIME_S = 1.0

# targetPos is rad. Keep velocity and acceleration in rad-based units.
CONTROL_MAX = MAX_SPEED_DEG_S * pi / 180.0
CONTROL_RATE_MAX = MAX_ACCEL_DEG_S2 * pi / 180.0
DEAD_BAND = 1.0e-6


def clamp(value: float, limit: float) -> float:
    if limit <= 0:
        return value
    return max(-limit, min(limit, value))


def clamp_range(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


@dataclass
class PidStepPlanner:
    kp: float = KP
    ki: float = KI
    kd: float = KD
    frequency: float = FREQUENCY
    control_max: float = CONTROL_MAX
    control_rate_max: float = CONTROL_RATE_MAX
    dead_band: float = DEAD_BAND
    integral: float = 0.0
    previous_error: float = 0.0
    previous_target: float = 0.0
    control_prev: float = 0.0
    target_state: bool = False

    def step(self, target_pos: float, current_pos: float) -> tuple[float, float, float]:
        fre = self.frequency
        if fre <= 0:
            fre = 1.0
            self.frequency = fre

        dt = 1.0 / fre
        error = target_pos - current_pos

        if (not self.target_state) or target_pos != self.previous_target:
            self.target_state = True
            self.previous_target = target_pos
            self.integral = 0.0
            self.previous_error = error

        self.integral = self.integral + error * dt
        derivative = (error - self.previous_error) / dt
        velocity = self.kp * error + self.ki * self.integral + self.kd * derivative

        velocity = clamp(velocity, self.control_max)

        max_delta = self.control_rate_max * dt
        if max_delta > 0:
            if (velocity - self.control_prev) > max_delta:
                velocity = self.control_prev + max_delta
            elif (velocity - self.control_prev) < -max_delta:
                velocity = self.control_prev - max_delta

        velocity = clamp(velocity, self.control_max)

        if abs(error) < self.dead_band and abs(velocity) <= max_delta:
            velocity = 0.0

        self.control_prev = velocity
        self.previous_error = error

        next_pos = current_pos + velocity * dt
        return next_pos, velocity, error


def build_target_schedule() -> list[tuple[float, float]]:
    random = Random(RANDOM_SEED)
    schedule = []
    time_s = 0.0
    target_pos = TELEOP_TARGET_START

    for _ in range(TARGET_COUNT):
        schedule.append((time_s, target_pos))
        interval_s = random.uniform(INTERVAL_MIN_MS, INTERVAL_MAX_MS) * 0.001
        direction = random.uniform(-1.0, 1.0)
        noise = random.uniform(-TELEOP_NOISE_RAD, TELEOP_NOISE_RAD)
        delta = direction * TELEOP_MAX_TARGET_SPEED * interval_s + noise
        target_pos = clamp_range(target_pos + delta, TARGET_MIN, TARGET_MAX)
        time_s += interval_s

    return schedule


def target_at_time(time_s: float, schedule: list[tuple[float, float]]) -> float:
    target_pos = schedule[0][1]
    for switch_time_s, scheduled_target in schedule:
        if time_s < switch_time_s:
            break
        target_pos = scheduled_target
    return target_pos


def run_step_response() -> dict[str, list[float]]:
    planner = PidStepPlanner()
    schedule = build_target_schedule()
    dt = 1.0 / planner.frequency
    sim_time_s = schedule[-1][0] + SETTLE_TIME_S
    total_steps = int(sim_time_s * planner.frequency)
    current_pos = INITIAL_POS

    data = {
        "time": [],
        "target": [],
        "pos": [],
        "velocity": [],
        "error": [],
    }

    for index in range(total_steps + 1):
        time_s = index * dt
        target_pos = target_at_time(time_s, schedule)
        next_pos, velocity, error = planner.step(target_pos, current_pos)

        data["time"].append(time_s)
        data["target"].append(target_pos)
        data["pos"].append(next_pos)
        data["velocity"].append(velocity)
        data["error"].append(error)

        current_pos = next_pos

    data["switch_time"] = [switch_time_s for switch_time_s, _ in schedule]
    data["scheduled_target"] = [target_pos for _, target_pos in schedule]
    return data


def print_summary(data: dict[str, list[float]]) -> None:
    dt = 1.0 / FREQUENCY
    velocities = data["velocity"]
    velocity_deltas = [
        abs(velocities[index] - velocities[index - 1])
        for index in range(1, len(velocities))
    ]

    print("PID step response simulation")
    print(f"frequency: {FREQUENCY:.6f} Hz, dt: {dt:.6f} s")
    print(f"kp: {KP}, ki: {KI}, kd: {KD}")
    print(f"control_max: {CONTROL_MAX:.6f} rad/s ({MAX_SPEED_DEG_S} deg/s)")
    print(f"control_rate_max: {CONTROL_RATE_MAX:.6f} rad/s^2 ({MAX_ACCEL_DEG_S2} deg/s^2)")
    print(
        "teleop target model: "
        f"{TARGET_COUNT} samples, {INTERVAL_MIN_MS:.0f}-{INTERVAL_MAX_MS:.0f} ms interval, "
        f"max target speed {TELEOP_MAX_TARGET_SPEED} rad/s"
    )
    print("target schedule:")
    for index, (switch_time_s, target_pos) in enumerate(
        zip(data["switch_time"], data["scheduled_target"]),
        start=1,
    ):
        print(f"  {index:02d}: t={switch_time_s:.3f}s, target={target_pos:.6f} rad")
    print(f"max |velocity|: {max(abs(value) for value in velocities):.6f}")
    print(f"max |delta_velocity|: {max(velocity_deltas, default=0.0):.6f}")
    print(f"delta_velocity limit per cycle: {CONTROL_RATE_MAX * dt:.6f}")
    print(f"final pos: {data['pos'][-1]:.6f}, final error: {data['error'][-1]:.6f}")


def plot_response(data: dict[str, list[float]]) -> None:
    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(10, 8))

    axes[0].plot(data["time"], data["target"], label="target", linestyle="--")
    axes[0].plot(data["time"], data["pos"], label="pos")
    axes[0].scatter(data["switch_time"], data["scheduled_target"], label="target switch", s=24)
    axes[0].set_ylabel("position")
    axes[0].grid(True)
    axes[0].legend()

    axes[1].plot(data["time"], data["velocity"], label="velocity")
    axes[1].axhline(CONTROL_MAX, color="gray", linestyle="--", linewidth=0.8)
    axes[1].axhline(-CONTROL_MAX, color="gray", linestyle="--", linewidth=0.8)
    axes[1].set_ylabel("velocity")
    axes[1].grid(True)
    axes[1].legend()

    axes[2].plot(data["time"], data["error"], label="error")
    axes[2].set_xlabel("time (s)")
    axes[2].set_ylabel("error")
    axes[2].grid(True)
    axes[2].legend()

    fig.suptitle("PID CPInterpolation Step Response")
    fig.tight_layout()
    plt.show()


def main() -> None:
    data = run_step_response()
    print_summary(data)
    plot_response(data)


if __name__ == "__main__":
    main()
