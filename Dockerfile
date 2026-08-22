ARG ROS_DISTRO=humble

FROM ros:${ROS_DISTRO}-ros-base-jammy AS builder

ARG ROS_DISTRO=humble

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      cmake \
      python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ws

# Dal context principale: teleoperation/
COPY src ./src
COPY config ./config

# Dal context aggiuntivo: ../interfaces
COPY --from=interfaces /src/robot_interfaces ./src/robot_interfaces

RUN source /opt/ros/${ROS_DISTRO}/setup.bash \
    && colcon build \
        --merge-install \
        --cmake-args -DCMAKE_BUILD_TYPE=Release


FROM ros:${ROS_DISTRO}-ros-base-jammy

ARG ROS_DISTRO=humble

ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
    ROS_DOMAIN_ID=0 \
    MODULE_SETUP=/opt/robot_module/setup.bash

RUN apt-get update && apt-get install -y --no-install-recommends \
      ros-${ROS_DISTRO}-rmw-cyclonedds-cpp \
      ros-${ROS_DISTRO}-joy \
      ros-${ROS_DISTRO}-teleop-twist-joy \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /ws/install /opt/robot_module

COPY docker-entrypoint.sh /ros_module_entrypoint.sh
RUN chmod +x /ros_module_entrypoint.sh

WORKDIR /teleoperation

ENTRYPOINT ["/ros_module_entrypoint.sh"]

CMD ["sleep", "infinity"]