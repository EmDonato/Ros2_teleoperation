#!/usr/bin/env python3
"""
@file joy_launch.py
@brief Launch file for joystick teleoperation.
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    workspace_config_path = '../../config/params.yaml'

    ld = LaunchDescription()

    # -----------------------------------------------------------------------
    # Joystick driver
    ld.add_action(
        Node(
            package='joy',
            executable='joy_node',
            name='joy',
            parameters=[
                workspace_config_path,
                {
                    'qos_overrides./joy.publisher.reliability': 'best_effort',
                    'qos_overrides./joy.publisher.history': 'keep_last',
                    'qos_overrides./joy.publisher.depth': 1,
                }
            ],
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
            parameters=[
                workspace_config_path,
                {
                    'qos_overrides./joy.subscription.reliability': 'best_effort',
                    'qos_overrides./joy.subscription.history': 'keep_last',
                    'qos_overrides./joy.subscription.depth': 1,

                    'qos_overrides./cmd_vel.publisher.reliability': 'best_effort',
                    'qos_overrides./cmd_vel.publisher.history': 'keep_last',
                    'qos_overrides./cmd_vel.publisher.depth': 1,
                }
            ],
            remappings=[
                ('/cmd_vel', '/cmd_vel/raw')
            ],
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