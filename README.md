# Teleoperation

This module contains:

- `joy_service_node`, which converts button presses into `robot_interfaces/srv/ControlCommand` requests;
- `joy_teleop_twist_ref`, which bounds and converts velocity commands for a differential-drive base;
- the standard ROS 2 `joy` node, installed in the image.

The default control service is `control/command`. The robot-specific bringup can override button mappings, maximum speed, wheel base, service name, and topics.

```bash
ROBOT_PLATFORM=linux/amd64 docker compose build
ROBOT_PLATFORM=linux/amd64 docker compose up -d
ROBOT_PLATFORM=linux/amd64 docker compose exec open-pi-joystick ros2 node list
```

Run these commands from this module directory. The Jazzy/Noble image defaults
to ARM64; omit `ROBOT_PLATFORM` when building on the Raspberry Pi. Use the same
platform override for `up` on an AMD64 PC; runtime needs a joystick.

`joy_bringup` installs `config/params.yaml` and resolves it through the package
share directory, independently of the working directory. Override it with
`ros2 launch joy_bringup joy_launch.py config_file:=/path/to/params.yaml`.
The YAML node keys match the launch names `joy_vel_ref` and
`joy_service_handler`. `/cmd_vel/raw` and `/cmd_vel` both use `TwistStamped`;
the loaded configuration enables stamped output in `teleop_twist_joy`.

Test installed configuration and the stamped velocity pipeline without devices:

```bash
docker run --rm --network none -e ROS_DOMAIN_ID=173 \
  -v "$PWD/tests:/tests:ro" open-pi-joystick-img:jazzy \
  python3 /tests/smoke_launch.py
```

This test publishes synthetic joystick input. Keep `--network none` so those
commands cannot reach a robot.
