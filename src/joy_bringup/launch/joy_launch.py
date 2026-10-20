#!/usr/bin/env python3
"""Launch joystick input, button services, and velocity references."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    workspace_config_path = LaunchConfiguration('config_file')

    ld = LaunchDescription()
    ld.add_action(DeclareLaunchArgument(
        'config_file',
        default_value=os.path.join(
            get_package_share_directory('joy_bringup'), 'config', 'params.yaml'),
        description='Joystick and velocity-control parameters'))

    # -----------------------------------------------------------------------
    # Joystick driver
    ld.add_action(
        Node(
            package='joy',
            executable='joy_node',
            name='joy',
            parameters=[workspace_config_path],
            output='screen',
            respawn=True,
            respawn_delay=2.0
        )
    )

    # -----------------------------------------------------------------------
    # Teleop Twist from joystick
    ld.add_action(
        Node(
            package='teleop_twist_joy',
            executable='teleop_node',
            name='teleop_twist_joy',
            parameters=[workspace_config_path],
            remappings=[('/cmd_vel', '/cmd_vel/raw')],
            output='screen'
        )
    )

    # -----------------------------------------------------------------------
    # Joy service handler
    ld.add_action(
        Node(
            package='joy_service_pkg',
            executable='joy_service_node',
            name='joy_service_handler',
            parameters=[workspace_config_path],
            output='screen'
        )
    )

    # -----------------------------------------------------------------------
    # Velocity reference from joystick
    ld.add_action(
        Node(
            package='joy_teleop_twist_ref',
            executable='joy_vel_ref',
            name='joy_vel_ref',
            parameters=[workspace_config_path],
            output='screen'
        )
    )

    return ld
