#!/usr/bin/env bash

set -e

# Load the ROS 2 installation.
source "/opt/ros/${ROS_DISTRO}/setup.bash"

# Load the workspace built inside the image.
source /ws/install/setup.bash

# Execute the command specified by Docker Compose.
exec "$@"