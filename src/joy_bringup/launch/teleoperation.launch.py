"""Launch the joystick module using its own configuration and topic boundaries."""
from pathlib import Path
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def start(context):
    config = LaunchConfiguration('config_file').perform(context)
    settings = yaml.safe_load(Path(config).read_text())['teleoperation_bringup']['ros__parameters']
    clock = LaunchConfiguration('use_sim_time').perform(context)
    overrides = {} if clock == 'config' else {'use_sim_time': clock == 'true'}
    parameters = [config, overrides]
    actions = [
        Node(package='teleop_twist_joy', executable='teleop_node', name='teleop_twist_joy',
             parameters=parameters, output='screen',
             remappings=[('joy', settings['joy_topic']), ('cmd_vel', settings['raw_topic'])]),
        Node(package='joy_teleop_twist_ref', executable='joy_vel_ref', name='joy_vel_ref',
             parameters=parameters, output='screen',
             remappings=[('cmd_vel/raw', settings['raw_topic']), ('cmd_vel', settings['command_topic'])]),
    ]
    if settings['start_driver']:
        actions.append(Node(package='joy', executable=settings['driver_executable'], name='joy',
                            parameters=parameters, remappings=[('joy', settings['joy_topic'])], output='screen'))
    if settings['start_buttons']:
        actions.append(Node(package='joy_service_pkg', executable='joy_service_node', name='joy_service_handler',
                            parameters=[*parameters, {'control_service': settings['control_service']}], output='screen'))
    return actions


def generate_launch_description():
    default = str(Path(get_package_share_directory('joy_bringup')) / 'config/params.yaml')
    return LaunchDescription([
        DeclareLaunchArgument('config_file', default_value=default),
        DeclareLaunchArgument('use_sim_time', default_value='config', choices=['config', 'true', 'false']),
        OpaqueFunction(function=start),
    ])
