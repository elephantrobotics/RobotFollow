# RobotFollow
此项目用作帮助用户实现Mercury系列机型(A1/B1/X1)的手臂跟随效果

## 1.跟随效果

### 1.1 鼠标跟踪

<img src="resource\mouse.gif">

### 1.2 外骨骼控制

<img src="resource\exoskeleton.gif">


### 1.3 VR控制

<img src="resource\VR.gif">

## 2.速度规划

### 2.1 点位控制模式PTP

PTP模式是机械臂最基础的控制方法，机械臂以0的起始、终止速度运动到目标位置，适用于简单的应用场景

<img src="resource\PTP.png">

其速度规划曲线如下：

<img src="resource\ptp_speed.png">

当连续调用PTP接口时，速度曲线如下：

<img src="resource\ptp_speed2.png">

可以看到在运动衔接处存在速度的启停

### 2.2 连续轨迹控制模式CP

CP模式支持连续的轨迹、速度控制

<img src="resource\CP.png">

其速度规划曲线如下：

<img src="resource\cp_speed.png">

**可以看到在运动衔接处速度未降到零**

### 2.3 固定周期的速度融合

本文使用的规划方式为周期可控的速度融合，适用于对跟随延迟有要求的开发场景，其速度规划曲线如下：

<img src="resource\fusion_time.png">

**其中每一段的周期T是可控的，周期的控制优先级高于位置**

## 3.速度融合接口说明

本文提供的速度融合接口适用于带**位置采样器**的应用场景，采集器以固定采样周期采集位置数据并下发给机械臂，从而实现机械臂跟随

#### 本文中提供的速度融合模式分为两种：

    基于位置环的融合规划,适用于对位置精度有要求的应用场景
    set_movement_type(2)

    基于速度环的融合规划，适用于对速度平滑有要求的应用场景
    set_movement_type(3)

开启融合模式后，使用以下接口开始速度融合控制

    send_angles(angles, time)
    send_coords(coords, time)

其中angles\coords表示目标位置，time表示控制周期（单位为7ms），例如：

    send_angles([0, 0, 0, 0, 0, 0, 0], 3)

#### 表示在3个周期（3*7=21ms）内抵达[0, 0, 0, 0, 0, 0, 0]位置




## 4.跟踪案例实现

#### 我在mouse_follow文件夹中存放了两个鼠标跟随的案例帮助用户使用速度融合接口

    mouse.py    坐标跟随
    mouse_joint.py  角度跟随

*在上述脚本中，我用鼠标作为采样器模拟了MercuryA1跟随的应用场景，用户移动鼠标采集位置信息，通过调用速度融合接口即可实现机械臂的跟随效果*
![alt text](resource\mouse.gif)

#### 在ex_mercury_follow文件夹中存放了外骨骼控制MercuryX1、B1的案例代码和说明
    MercuryControl.py 外骨骼跟随主程序
    exoskeleton_api.py 外骨骼控制库

*在上述脚本中，外骨骼作为采样器，用户通过转动外骨骼关节采集关节信息，通过调用速度融合接口即可实现机械臂的跟随效果*
![alt text](resource\exoskeleton.gif)


## 5.接口使用的常见问题

**1.若在指定周期内无法抵达目标位置，则会运动到周期内的最远距离**

**2.若在机械臂执行完指定周期后仍未收到新的运动指令，则会以最大减速度减速至静止**

**3.速度环的采样频率建议小于100Hz**

#### 执行卡顿
* 由于规则2的限制，采样器的采样频率需高于执行频率，否则当机械臂内部点位缓存为空时，会发生急停引发卡顿
**(采样周期可通过脚本中的time.time()得到，执行周期为见第3章速度融合接口说明,一般情况下建议采样周期为10~20ms，执行周期为TIME>=3(3*7=21ms))**

* 在位置环的融合控制下，机械臂对位置高度敏感，若采样器采集到的点位速度不平滑，例如存在急停和急启动的情况，会导致执行卡顿
**（大部分情况建议使用速度环控制，除非你对精度要求很高，并且了解规划的加减速知识）**

* 在速度环的融合控制下，机械臂通过采样器的差分速度控制运动趋势，若采样频率过高(>100hz)则可能导致差分速度过小，引发执行卡顿
**(加10ms延迟即可)**

#### 位置误差

* 由于规则1的限制，位置模式下可能出现位置误差
**(多次发送目标位置即可消除该误差)**

* 在速度环的融合控制下，由于接口存在速度的映射关系，机械臂会出现位置的累积误差
**(中断联动控制，待机械臂停止后重新调用融合接口，机械臂会自动校准位置误差)**