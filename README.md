# Teleoperation

ROS 2 joystick control for Open PiRobot. The module starts its own Docker container
and launches the joystick driver, normalized command conversion and wheel mixing.

```bash
bash joystick.sh build
bash joystick.sh create
bash joystick.sh stop
```

`create` requires a joystick in `/dev/input/js*`. Use `status` and `logs` to inspect
the container. The default configuration is `config/params.yaml`; hold L1 (button 9)
while moving the sticks to publish velocity commands. Topics and controller settings
are defined in that YAML. The `joy_bringup` package provides
`teleoperation.launch.py` with `config_file` and optional `use_sim_time` arguments.

Compose mounts the configuration as `/ws/config/params.yaml`.
`PIROBOT_TELEOP_CONFIG` selects another parameter file, including the temporary
config prepared by the simulation workspace. The workspace calls `joystick.sh`;
ROS nodes run inside this module's container.

Set `use_sim_time` in the module YAML for standalone operation: `false` uses the
system clock and `true` subscribes to `/clock`. The simulation workspace's
`runtime.use_sim_time` overrides the temporary config; `null` preserves module defaults.
