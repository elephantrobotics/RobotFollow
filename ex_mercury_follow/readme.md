# 外骨骼&MercuryX1\B1联动说明

## 控制效果
<img src="../resource\exoskeleton.gif">

## 使用前的准备

#### 更新pymycobot固件(version=b66及之后的版本)

	pip install pymycobot==3.5.0b66


#### 更新Mercury固件(get_modified_version=12及之后的版本)

	Mercury_firmware\MercuryX1_left_v1.0.13_20250212.bin
	Mercury_firmware\MercuryX1_right_v1.0.13_20250212.bin

#### 固件烧录方法如下：

<video controls src="../resource/MercuryX1固件烧录方法.mp4" title=""></video>

#### 后续我们会将该固件更新至官网的mystudio中，目前需要手动更新

## 文件说明

exoskeleton_api.py 外骨骼控制库

MercuryControl.py 手臂跟随主程序

power_reset.py 双臂使能

**完成使用前准备后，运行MercuryControl.py脚本即可**

## 异常处理

**由于双臂有严格的上下电顺序，当出现机械臂无法使能时，可尝试执行power_reset.py控制机械臂使能**


## MercuryControl.py脚本说明

**首先需要修改为外骨骼对应串口，一般为ttyACM0~4**

	obj = Exoskeleton(port="/dev/ttyACM2")

修改对应串口权限
	sudo chmod 777 /dev/ttyACM2

切换为速度融合模式

	ml.set_movement_type(3)
	mr.set_movement_type(3)

	print(ml.get_movement_type())
	print(mr.get_movement_type())

#### 注意！如果此处显示出错，或未成功切换至mode=3，需要确认 *使用前准备* 是否正常完成！

设置VR模式

	ml.set_vr_mode(1)
	mr.set_vr_mode(1)

循环将采样点发送给Mercury

	while 1:
		mc.send_angles(mercury_list, TI, _async=True)
			time.sleep(0.01)

参数说明：	

	mercury_list：目标位置（1*7关节角度）

	TI：速度等级，TI越小速度越快，建议>=3

	_async=True：开环接口，指令不等待
	
	time.sleep(0.01)：发送频率不要超过100hz（10ms）

	