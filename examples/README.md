# RobotFollow Examples

[中文](#中文) | [English](#english)

## 中文

本目录是 RobotFollow 推荐使用的运行入口。旧目录中的脚本已经合并到这些示例和 `robot_follow/` 公共模块中。

## 使用前准备

先在项目根目录复制配置文件：

```bash
cp config.example.json config.json
```

Windows PowerShell:

```powershell
Copy-Item config.example.json config.json
```

然后根据实际设备修改 `config.json` 中的串口和参数：

```json
{
  "single_arm_port": "/dev/ttyAMA1",
  "left_arm_port": "/dev/left_arm",
  "right_arm_port": "/dev/right_arm",
  "exoskeleton_port": "/dev/ttyACM2",
  "movement_type": 4,
  "kp": 16,
  "send_interval_ms": 10.0
}
```

```text
movement_type = 4
```

`kp` 是 CP 跟随参数，当前 examples 会把它作为控制指令的第二个参数下发，建议默认值为 `16`。`Kp` 越大响应越快；如果出现超调、冲过目标、抖动或跟随过激，通常是 `Kp` 偏大，可以先适当降低。


## 示例说明

| 文件 | 说明 |
| --- | --- |
| `mouse_a1_coords.py` | Mercury A1 鼠标坐标跟随 |
| `mouse_a1_angles.py` | Mercury A1 鼠标关节跟随 |
| `mouse_x1_base.py` | Mercury X1 双臂鼠标 base 坐标跟随 |
| `exoskeleton_a1_angles.py` | Mercury A1 外骨骼关节跟随 |
| `exoskeleton_x1_angles.py` | Mercury X1/B1 双臂外骨骼关节跟随 |
| `power_reset.py` | Mercury X1/B1 双臂上下电顺序辅助 |

## 运行命令

在项目根目录运行：

```bash
python examples/mouse_a1_coords.py
python examples/mouse_a1_angles.py
python examples/mouse_x1_base.py
python examples/exoskeleton_a1_angles.py
python examples/exoskeleton_x1_angles.py
python examples/power_reset.py
```

如需使用其他配置文件：

```bash
python examples/mouse_a1_coords.py --config my_config.json
```

## 读取线程

控制示例默认会启动低频读取线程，周期性调用：

```python
get_angles()
```

输出格式示例：

```text
read_angles,single,[...]
read_angles,left,[...]
read_angles,right,[...]
```

相关配置：

```json
{
  "enable_read_angles": true,
  "read_angles_interval_ms": 100.0
}
```

如果读取影响实机控制或串口输出太多，可以关闭：

```json
{
  "enable_read_angles": false
}
```

## 实机注意事项

- 运行示例前确认 `pymycobot` 和机械臂固件版本匹配。
- CP/FUSION 相关示例需要支持对应运动模式的固件。
- 如果 `set_movement_type(4)` 不生效，请先检查固件版本和烧录情况。
- 鼠标/外骨骼示例会持续下发控制指令，请确保机械臂工作空间安全。
- 采样周期建议 `10~20 ms`，不要让发送频率超过 `100 Hz`。

## English

This directory contains the recommended RobotFollow entry points. Scripts from the old directories have been merged into these examples and the shared `robot_follow/` modules.

## Preparation

First copy the config file from the project root:

```bash
cp config.example.json config.json
```

Windows PowerShell:

```powershell
Copy-Item config.example.json config.json
```

Then adjust serial ports and parameters in `config.json` for your device:

```json
{
  "single_arm_port": "/dev/ttyAMA1",
  "left_arm_port": "/dev/left_arm",
  "right_arm_port": "/dev/right_arm",
  "exoskeleton_port": "/dev/ttyACM2",
  "movement_type": 4,
  "kp": 16,
  "send_interval_ms": 10.0
}
```

```text
movement_type = 4
```

`kp` is the CP follow parameter. The examples send it as the second argument of the control command, and `16` is the recommended default. A larger `Kp` gives faster response. If the robot overshoots, passes beyond the target, shakes, or tracks too aggressively, `Kp` is usually too large and should be reduced first.

## Example List

| File | Description |
| --- | --- |
| `mouse_a1_coords.py` | Mercury A1 mouse-to-coordinate follow |
| `mouse_a1_angles.py` | Mercury A1 mouse-to-joint follow |
| `mouse_x1_base.py` | Mercury X1 dual-arm mouse-to-base-coordinate follow |
| `exoskeleton_a1_angles.py` | Mercury A1 exoskeleton-to-joint follow |
| `exoskeleton_x1_angles.py` | Mercury X1/B1 dual-arm exoskeleton-to-joint follow |
| `power_reset.py` | Mercury X1/B1 dual-arm power reset helper |

## Run Commands

Run from the project root:

```bash
python examples/mouse_a1_coords.py
python examples/mouse_a1_angles.py
python examples/mouse_x1_base.py
python examples/exoskeleton_a1_angles.py
python examples/exoskeleton_x1_angles.py
python examples/power_reset.py
```

To use another config file:

```bash
python examples/mouse_a1_coords.py --config my_config.json
```

## Read Thread

Control examples start a low-frequency read thread by default. It periodically calls:

```python
get_angles()
```

Example output:

```text
read_angles,single,[...]
read_angles,left,[...]
read_angles,right,[...]
```

Related config:

```json
{
  "enable_read_angles": true,
  "read_angles_interval_ms": 100.0
}
```

If reading affects real-machine control or produces too much serial output, disable it:

```json
{
  "enable_read_angles": false
}
```

## Real-Machine Notes

- Before running examples, confirm that `pymycobot` and the robot firmware version match.
- CP/FUSION examples require firmware that supports the corresponding motion mode.
- If `set_movement_type(4)` does not take effect, check the firmware version and burning status first.
- Mouse and exoskeleton examples continuously send control commands. Make sure the robot workspace is safe.
- The recommended sampling period is `10~20 ms`. Do not exceed a `100 Hz` send frequency.
