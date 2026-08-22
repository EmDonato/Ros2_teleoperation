FROM ros:humble-ros-base-jammy

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    python3-colcon-common-extensions \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-joy \
    ros-humble-teleop-twist-joy \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ws

COPY src/ src/
COPY --from=interfaces /src/robot_interfaces src/robot_interfaces/

RUN source /opt/ros/humble/setup.bash && \
    colcon build --merge-install \
        --cmake-args -DCMAKE_BUILD_TYPE=Release

COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ENTRYPOINT ["/entrypoint.sh"]

CMD ["sleep", "infinity"]