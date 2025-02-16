# RobotFollow
此项目用作帮助用户实现Mercury系列机型(A1/B1/X1)的手臂跟随效果

## 1.跟随效果

### 1.1 鼠标跟踪

<img src="resource\mouse.gif">

### 1.2 外骨骼控制

<img src="resource\exoskeleton.gif">


### 1.3 VR控制

<img src="resource\VR.gif">

## 2.运动模式说明

### 2.1 点位控制模式PTP

PTP模式是机械臂**默认**的控制方法，机械臂以0的起始\终止速度运动到目标位置，适用于绝大部分的应用场景

<img src="resource\PTP.png">

其速度规划曲线如下：

<img src="resource\ptp_speed.png">

当连续调用PTP接口时，可以看到在运动衔接处存在速度的启停：

<img src="resource\ptp_speed2.png">



使用以下接口可切换至PTP模式，其中MovJ表示坐标运动时执行**非直线轨迹**，MovL表示坐标运动时执行**直线轨迹**

    set_movement_type(0) #MovJ非直线运动
    set_movement_type(1) #MovL直线运动（默认）

**在PTP模式下支持多点位的缓存，控制器会依次执行缓存的运动指令**

### 2.2 连续轨迹控制模式CP

CP模式支持连续的轨迹、速度控制

<img src="resource\CP.png">

其速度规划曲线如下，**可以看到在运动衔接处速度未降到零**：

<img src="resource\cp_speed.png">

使用以下接口可切换至CP模式

    set_movement_type(4) #CP

**在CP模式下不支持多点位的缓存，控制器会始终执行最新一条运动指令，指令衔接不会导致机械臂停止，而是在原速度的基础上继续规划**

### 2.3 速度融合模式FUSION

FUSION模式不是一个通用的控制模式，它是为了适配VR遥操作、外骨骼跟随等应用场景的**高速响应**模式，在CP模式中我们可以做到运动指令的速度衔接，但由于无法严格控制指令的运动时间，可能会出现机械臂响应速度较慢的情况

为了解决联动场景中的延迟问题，FUSION模式严格限制了指令的运动周期，用户可规定运动指令的执行时间，**每一段的周期T是可控的，周期的控制优先级高于位置**：

<img src="resource\fusion_time.png">

使用以下接口可切换至FUSION模式

基于**位置环**的融合规划,适用于对位置精度要求高的场景，**适用于VR控制**

    set_movement_type(2) #pos


基于**速度环**的融合规划，适用于对位置精度要求低的的应用场景，**适用于外骨骼联动等应用场景！**

    set_movement_type(3) #speed

**注意，在速度环模式下，机器会跟随采样点位的差分速度而不是实际位置！**

开启融合模式后，使用以下接口开始速度融合控制

    send_angles(angles, time)
    send_coords(coords, time)

其中angles\coords表示目标位置，time表示控制周期（单位为7ms），例如：

    send_angles([0, 0, 0, 0, 0, 0, 0], 3)

**表示在3个周期（3*7=21ms）内抵达[0, 0, 0, 0, 0, 0, 0]位置**


## 3.跟踪案例实现

本文提供的速度融合接口适用于带**位置采样器**的应用场景，采集器以固定采样周期采集位置数据并下发给机械臂，从而实现机械臂跟随

#### 我在mouse_follow文件夹中存放了两个鼠标跟随的案例帮助用户使用速度融合接口

    mouse.py    坐标跟随
    mouse_joint.py  角度跟随

*在上述脚本中，我用鼠标作为采样器模拟了MercuryA1跟随的应用场景，用户移动鼠标采集位置信息，通过调用速度融合接口即可实现机械臂的跟随效果*
<img src="resource\mouse.gif">

---


#### 我在mouse_follow\X1文件夹中存放了MercuryX1的坐标跟随案例
    mouse.py    双臂坐标跟随

<img src="resource\X1.gif">

*用户可基于此框架进行VR坐标控制的功能开发*

---

#### 在ex_mercury_follow文件夹中存放了外骨骼控制MercuryX1、B1的案例代码和说明
    MercuryControl.py 外骨骼跟随主程序
    exoskeleton_api.py 外骨骼控制库

*在上述脚本中，外骨骼作为采样器，用户通过转动外骨骼关节采集关节信息，通过调用速度融合接口即可实现机械臂的跟随效果*
<img src="resource\exoskeleton.gif">


## 4.速度融合接口使用的常见问题

**1.若在指定周期内无法抵达目标位置，则会运动到周期内的最远距离**

**2.若在机械臂执行完指定周期后仍未收到新的运动指令，则会以最大减速度减速至静止**

**3.速度环的采样频率建议小于100Hz**

#### 执行卡顿
* 由于规则2的限制，采样器的采样频率需高于执行频率，否则当机械臂内部点位缓存为空时，会发生急停引发卡顿
**(采样周期可通过脚本中的time.time()得到，执行周期为见第2章速度融合接口说明,一般情况下建议采样周期为10~20ms，执行周期为TIME>=3(3*7=21ms))**

* 在位置环的融合控制下，机械臂对位置高度敏感，若采样器采集到的点位差分速度不平滑，例如存在急停和急启动的情况，会导致执行卡顿
**（大部分情况建议使用速度环控制，除非你对精度要求很高，并且了解规划的加减速知识）**

* 在速度环的融合控制下，机械臂通过采样器的差分速度控制运动趋势，若采样频率过高(>100hz)则可能导致差分速度过小，引发执行卡顿
**(加10ms延迟即可)**

#### 位置误差

* 由于规则1的限制，位置模式下可能出现位置误差
**(多次发送目标位置即可消除该误差)**

* 在速度环的融合控制下，由于接口存在速度的映射关系，机械臂会出现位置的累积误差
**(中断联动控制，待机械臂停止后重新调用融合接口，机械臂会自动校准位置误差)**