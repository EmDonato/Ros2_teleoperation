FROM ros:jazzy-ros-base-noble

SHELL ["/bin/bash", "-c"]

ARG USERNAME=joy
ARG UID=1000
ARG GID=1000


# Noble reserves UID/GID 1000 for its default ubuntu account.
RUN if id ubuntu >/dev/null 2>&1; then userdel -r ubuntu; fi && \
    groupadd -g ${GID} ${USERNAME} && \
    useradd -m -u ${UID} -g ${GID} -s /bin/bash ${USERNAME}

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    python3-colcon-common-extensions \
    ros-jazzy-rmw-cyclonedds-cpp \
    ros-jazzy-joy \
    ros-jazzy-teleop-twist-joy \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ws

COPY src/ src/
COPY config/ config/
COPY --from=interfaces /src/robot_interfaces src/robot_interfaces/

RUN source /opt/ros/${ROS_DISTRO}/setup.bash && \
    colcon build \
        --merge-install \
        --cmake-args -DCMAKE_BUILD_TYPE=Release

COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["sleep", "infinity"]