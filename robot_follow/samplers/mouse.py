"""Mouse sampling helpers."""

from __future__ import annotations


class MouseOffsetSampler:
    """Return mouse movement relative to the first sampled position."""

    def __init__(self) -> None:
        from pynput.mouse import Controller

        self._mouse = Controller()
        self._initial_position: tuple[int, int] | None = None

    def offset(self) -> tuple[int, int]:
        current_position = self._mouse.position
        if self._initial_position is None:
            self._initial_position = current_position

        return (
            current_position[0] - self._initial_position[0],
            current_position[1] - self._initial_position[1],
        )


def apply_xy_offset(
    base: list[float],
    offset: tuple[int, int],
    *,
    x_index: int,
    y_index: int,
    x_scale: float,
    y_scale: float,
) -> list[float]:
    target = base.copy()
    target[x_index] = base[x_index] + offset[0] * x_scale
    target[y_index] = base[y_index] + offset[1] * y_scale
    return target


def apply_two_axis_offset(
    base: list[float],
    offset: tuple[int, int],
    *,
    first_index: int,
    second_index: int,
    first_scale: float,
    second_scale: float,
) -> list[float]:
    target = base.copy()
    target[first_index] = base[first_index] + offset[0] * first_scale
    target[second_index] = base[second_index] + offset[1] * second_scale
    return target
