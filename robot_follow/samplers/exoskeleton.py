"""Exoskeleton serial and socket protocol helpers."""

from __future__ import annotations

import socket
import threading


_lock = threading.Lock()


def _parse_arm_data(data: str) -> list[float]:
    parsed_data = []
    for i in range(7):
        data_h = data[0 + i * 4: 2 + i * 4]
        data_l = data[2 + i * 4: 4 + i * 4]
        encode = int(data_h + data_l, 16)
        if encode == 2048:
            angle = 0
        elif encode > 2048:
            angle = 180 * (encode - 2048) / 2048
        else:
            angle = -180 * (2048 - encode) / 2048
        parsed_data.append(round(angle, 2))

    button = bin(int(data[28:30], 16))[2:].rjust(4, "0")
    parsed_data.extend([
        int(button[-4]),
        int(button[-1]),
        int(button[-3]),
        int(button[-2]),
        int(data[30:32], 16),
        int(data[32:34], 16),
    ])
    return parsed_data


class Exoskeleton:
    def __init__(self, port: str, baudrate: int = 1000000):
        import serial

        self.ser = serial.Serial(port=port, baudrate=baudrate)

    def _common(self, command_array: list[int]) -> str | None:
        with _lock:
            command_id = command_array[3]
            self.ser.write(bytearray(command_array))
            start1 = self.ser.read().hex()
            if start1 != "fe" or self.ser.read().hex() != "fe":
                return None
            data_len = int(self.ser.read().hex(), 16)
            count = self.ser.in_waiting
            if data_len == count:
                data = self.ser.read(count).hex()
                if data[-2:] == "fa" and int(data[0:2], 16) == command_id:
                    return data[2:-2]
        return None

    def get_all_data(self) -> list[list[float]] | None:
        data = self._common([0xFE, 0xFE, 0x02, 0x01, 0xFA])
        if data is None:
            return None
        return [_parse_arm_data(data), _parse_arm_data(data[34:])]

    def get_arm_data(self, arm: int) -> list[float] | None:
        if arm not in [1, 2]:
            raise ValueError("arm must be 1 or 2")
        data = self._common([0xFE, 0xFE, 0x03, 0x02, arm, 0xFA])
        if data is None:
            return None
        return _parse_arm_data(data)

    def get_joint_data(self, arm: int, joint_id: int) -> float | None:
        if arm not in [1, 2] or joint_id < 1 or joint_id > 7:
            raise ValueError("arm must be 1 or 2 and joint_id must be 1..7")
        data = self._common([0xFE, 0xFE, 0x04, 0x03, arm, joint_id, 0xFA])
        if data is None:
            return None
        encode = int(data[0:2] + data[2:4], 16)
        if encode == 2048:
            angle = 0
        elif encode > 2048:
            angle = 180 * (encode - 2048) / 2048
        else:
            angle = -180 * (2048 - encode) / 2048
        return round(angle, 2)

    def set_zero(self, arm: int, joint_id: int) -> None:
        if arm not in [1, 2] or joint_id < 1 or joint_id > 7:
            raise ValueError("arm must be 1 or 2 and joint_id must be 1..7")
        with _lock:
            self.ser.write(bytearray([0xFE, 0xFE, 0x04, 0x04, arm, joint_id, 0xFA]))

    def set_color(self, arm: int, red: int, green: int, blue: int) -> None:
        if arm not in [1, 2]:
            raise ValueError("arm must be 1 or 2")
        with _lock:
            self.ser.write(bytearray([0xFE, 0xFE, 0x06, 0x05, arm, red, green, blue, 0xFA]))


class ExoskeletonSocket:
    def __init__(self, ip: str = "192.168.4.1", port: int = 80):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((ip, port))

    def _common(self, command_array: list[int]) -> str | None:
        with _lock:
            command_id = command_array[3]
            self.client.sendall(bytearray(command_array))
            if self.client.recv(1).hex() != "fe" or self.client.recv(1).hex() != "fe":
                return None
            data_len = int(self.client.recv(1).hex(), 16) * 2
            data = self.client.recv(1024).hex()
            if len(data) == data_len and data[-2:] == "fa" and int(data[0:2], 16) == command_id:
                return data[2:-2]
        return None

    def get_all_data(self) -> list[list[float]] | None:
        data = self._common([0xFE, 0xFE, 0x02, 0x01, 0xFA])
        if data is None:
            return None
        return [_parse_arm_data(data), _parse_arm_data(data[34:])]

    def get_arm_data(self, arm: int) -> list[float] | None:
        if arm not in [1, 2]:
            raise ValueError("arm must be 1 or 2")
        data = self._common([0xFE, 0xFE, 0x03, 0x02, arm, 0xFA])
        if data is None:
            return None
        return _parse_arm_data(data)

    def get_joint_data(self, arm: int, joint_id: int) -> float | None:
        if arm not in [1, 2] or joint_id < 1 or joint_id > 7:
            raise ValueError("arm must be 1 or 2 and joint_id must be 1..7")
        data = self._common([0xFE, 0xFE, 0x04, 0x03, arm, joint_id, 0xFA])
        if data is None:
            return None
        encode = int(data[0:2] + data[2:4], 16)
        if encode == 2048:
            angle = 0
        elif encode > 2048:
            angle = 180 * (encode - 2048) / 2048
        else:
            angle = -180 * (2048 - encode) / 2048
        return round(angle, 2)

    def set_zero(self, arm: int, joint_id: int) -> None:
        if arm not in [1, 2] or joint_id < 1 or joint_id > 7:
            raise ValueError("arm must be 1 or 2 and joint_id must be 1..7")
        with _lock:
            self.client.sendall(bytearray([0xFE, 0xFE, 0x04, 0x04, arm, joint_id, 0xFA]))

    def set_color(self, arm: int, red: int, green: int, blue: int) -> None:
        if arm not in [1, 2]:
            raise ValueError("arm must be 1 or 2")
        with _lock:
            self.client.sendall(bytearray([0xFE, 0xFE, 0x06, 0x05, arm, red, green, blue, 0xFA]))


__all__ = ["Exoskeleton", "ExoskeletonSocket"]
