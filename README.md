Note: The latest changes have been updated to the develop branch!

# RobotFollow
This project helps users achieve arm tracking for Mercury series robots (A1/B1/X1).

## 1. Following Effect

### 1.1 Mouse Tracking

<img src="resource\mouse.gif">

### 1.2 Exoskeleton Control

<img src="resource\exoskeleton.gif">

### 1.3 VR Control

<img src="resource\VR.gif">

## 2. Motion Mode Description

### 2.1 Point-to-Point Control Mode (PTP)

PTP mode is the default control method for robotic arms. The arm moves to the target position with a starting and ending velocity of 0. It is suitable for most application scenarios.

<img src="resource\PTP.png">

The velocity planning curve is as follows:

<img src="resource\ptp_speed.png">

When the PTP interface is called continuously, you can see that there is a start and stop of speed at the joint of movement:

<img src="resource\ptp_speed2.png">

Use the following interface to switch to PTP mode, where MovJ indicates that **non-linear trajectory** is executed during coordinate movement, and MovL indicates that **linear trajectory** is executed during coordinate movement

set_movement_type(0) #MovJ non-linear movement
set_movement_type(1) #MovL linear movement (default)

**In PTP mode, multi-point cache is supported, and the controller will execute the cached motion instructions in sequence**

### 2.2 Continuous trajectory control mode CP

CP mode supports continuous trajectory and speed control

<img src="resource\CP.png">

The speed planning curve is as follows, **you can see that the speed does not drop to zero at the joint of movement**:

<img src="resource\cp_speed.png">

Use the following interface to switch to CP mode

set_movement_type(4) #CP

**In CP mode, multi-point caching is not supported. The controller will always execute the latest motion command. Command connection will not cause the robot arm to stop, but will continue planning based on the original speed**

### 2.3 Speed ​​Fusion Mode

FUSION mode is not a general control mode. It is a **high-speed response** mode to adapt to application scenarios such as VR teleoperation and exoskeleton following. In CP mode, we can achieve speed connection of motion commands, but since the movement time of the command cannot be strictly controlled, the robot arm may respond slowly

In order to solve the delay problem in the linkage scene, FUSION mode strictly limits the movement cycle of the command. The user can specify the execution time of the motion command. **The cycle T of each segment is controllable, and the control priority of the cycle is higher than the position**:

<img src="resource\fusion_time.png">

Use the following interface to switch to FUSION mode

Based on **position loop** fusion planning, it is suitable for scenarios with high position accuracy requirements and **suitable for VR control**

set_movement_type(2) #pos

Based on the **velocity loop** fusion planning, it is suitable for application scenarios with low position accuracy requirements, and **suitable for application scenarios such as exoskeleton linkage!**

set_movement_type(3) #speed

**Note that in velocity loop mode, the machine will follow the differential velocity of the sampling point instead of the actual position!** **

After enabling fusion mode, use the following API to start velocity fusion control.

send_angles(angles, time)
send_coords(coords, time)

Where angles\coords represents the target position, and time represents the control period (in 7ms). For example:

send_angles([0, 0, 0, 0, 0, 0, 0], 3)

** indicates reaching the position [0, 0, 0, 0, 0, 0, 0] within 3 periods (3*7=21ms)**

## 3. Tracking Example Implementation

The velocity fusion API provided in this article is suitable for applications with a **position sampler**. The sampler collects position data at a fixed sampling period and sends it to the robot arm, enabling robot tracking.

#### I have included two mouse tracking examples in the mouse_follow folder to help users use the velocity fusion API.

mouse.py Coordinate tracking
mouse_joint.py Angle Following

*In the above script, I used the mouse as a sampler to simulate the MercuryA1 following application scenario. The user moves the mouse to collect position information, and the robotic arm can achieve following effects by calling the velocity fusion interface.*
<img src="resource\mouse.gif">

---

#### I have stored MercuryX1 coordinate following examples in the mouse_follow\X1 folder.

mouse.py Dual-Arm Coordinate Following

<img src="resource\X1.gif">

*Users can develop VR coordinate control functions based on this framework.*

---

#### The ex_mercury_follow folder contains example code and instructions for controlling the MercuryX1 and B1 exoskeleton.

MercuryControl.py Exoskeleton Following Main Program

exoskeleton_api.py Exoskeleton Control Library

*In the above script, the exoskeleton acts as a sampler. The user rotates the exoskeleton joints to collect joint information. By calling the velocity fusion interface, the robotic arm can achieve a following effect.*
<img src="resource\exoskeleton.gif">

## 4. Common Problems Using the Velocity Fusion Interface

**1. If the target position cannot be reached within the specified cycle, it will move to the maximum distance within the cycle.**

**2. If the robotic arm does not receive a new movement command after completing the specified cycle, it will decelerate to a standstill at the maximum deceleration rate.**

**3. The velocity loop sampling frequency is recommended to be less than 100Hz.**

#### Execution Stalls
* Due to the limitations of Rule 2, the sampler's sampling frequency must be higher than the execution frequency. Otherwise, when the robot's internal point buffer is empty, an emergency stop will occur, causing lag.
**(The sampling period can be obtained using time.time() in the script. The execution period is described in Chapter 2, Velocity Fusion Interface. Generally, a sampling period of 10-20ms is recommended, and an execution period of TIME>=3 (3*7=21ms).)**

* Under position loop fusion control, the robot is highly sensitive to position. If the differential velocity of the points collected by the sampler is not smooth, such as during emergency stops and starts, it will cause execution lag.
**(In most cases, velocity loop control is recommended unless you have high accuracy requirements and understand planned acceleration and deceleration.)**

* Under velocity loop fusion control, the robot uses the sampler's differential velocity to control its movement. If the sampling frequency is too high (>100Hz), the differential velocity may be too low, causing execution lag.
**(Adding a 10ms delay is sufficient.)**

#### Position Error

* Due to the limitations of Rule 1, positional errors may occur in position mode.

**(This error can be eliminated by sending the target position multiple times.)**

* Under the fusion control of the speed loop, due to the speed mapping relationship at the interface, the robotic arm will experience cumulative positional errors.

**(Interrupt the linkage control; after the robotic arm stops and the fusion interface is called again, the robotic arm will automatically calibrate the positional error.)**