"""Check installed teleoperation launch in a container without network or devices.

Run with the Jazzy overlay sourced. Publishes synthetic joystick input; use
Docker --network none, never run this against a physical robot's ROS graph.
"""

import math
import signal
import subprocess
import time

import rclpy
from geometry_msgs.msg import TwistStamped
from rcl_interfaces.srv import GetParameters
from sensor_msgs.msg import Joy


def main():
    process = subprocess.Popen(['ros2', 'launch', 'joy_bringup', 'joy_launch.py'])
    rclpy.init()
    node = rclpy.create_node('teleop_launch_smoke')
    commands = []
    subscription = node.create_subscription(TwistStamped, '/cmd_vel', commands.append, 10)
    publisher = node.create_publisher(Joy, '/joy', 10)
    try:
        for service, name, expected in [
            ('/joy_vel_ref/get_parameters', 'max_vel', 0.20),
            ('/teleop_twist_joy/get_parameters', 'publish_stamped_twist', True),
            ('/joy_service_handler/get_parameters', 'arm_button', 0),
        ]:
            client = node.create_client(GetParameters, service)
            assert client.wait_for_service(timeout_sec=15), service
            request = GetParameters.Request(names=[name])
            future = client.call_async(request)
            rclpy.spin_until_future_complete(node, future, timeout_sec=10)
            assert future.done(), name
            value = future.result().values[0]
            actual = {1: value.bool_value, 2: value.integer_value, 3: value.double_value}[value.type]
            assert actual == expected, (name, actual, expected)
            node.destroy_client(client)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and not commands:
            assert process.poll() is None, 'launch exited'
            joy = Joy()
            joy.header.stamp = node.get_clock().now().to_msg()
            joy.axes = [0.0, 0.5, 0.0, 0.0, 0.0, 0.0]
            joy.buttons = [0] * 12
            joy.buttons[10] = 1  # Enable velocity only; no arm/reset buttons.
            publisher.publish(joy)
            rclpy.spin_once(node, timeout_sec=0.1)
        assert commands, 'no stamped velocity received through the full joystick pipeline'
        assert 0.0 < commands[-1].twist.linear.x <= 0.20
        assert math.isclose(commands[-1].twist.angular.z, 0.0, abs_tol=1e-9)
        assert commands[-1].header.stamp.sec > 0
        print('PASS: installed parameters, TwistStamped pipeline, configured velocity bound')
    finally:
        process.send_signal(signal.SIGINT)
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise
        node.destroy_subscription(subscription)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
