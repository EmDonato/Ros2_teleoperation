# Teleoperation

This module contains:

- `joy_service_node`, which converts button presses into `robot_interfaces/srv/ControlCommand` requests;
- `joy_teleop_twist_ref`, which bounds and converts velocity commands for a differential-drive base;
- the standard ROS 2 `joy` node, installed in the image.

The default control service is `control/command`. The robot-specific bringup can override button mappings, maximum speed, wheel base, service name, and topics.

```bash
docker compose -f teleoperation/compose.yaml build
docker compose -f teleoperation/compose.yaml up -d
docker compose -f teleoperation/compose.yaml exec teleoperation ros2 run joy joy_node
```
