#!/usr/bin/env python3
"""
@file joy_launch.py
@brief Launch file for joystick teleoperation, they create button service and velocity references.
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    workspace_config_path = './config/params.yaml'

    ld = LaunchDescription()

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
