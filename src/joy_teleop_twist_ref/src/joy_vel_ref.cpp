#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist_stamped.hpp"

#include <algorithm>
#include <cmath>

class JoyVelRef : public rclcpp::Node
{
public:
    JoyVelRef()
        : Node("joy_vel_ref_node"),
          last_stamp_(0, 0, RCL_ROS_TIME)
    {
        // ===============================
        // Parameters
        // ===============================
        this->declare_parameter("max_vel", 0.30);      // [m/s]
        this->declare_parameter("scales", 1.0);        // [0..1]
        this->declare_parameter("wheel_base", 0.2);    // [m]

        max_vel_    = this->get_parameter("max_vel").as_double();
        scales_     = this->get_parameter("scales").as_double();
        wheel_base_ = this->get_parameter("wheel_base").as_double();

        // ===============================
        // ROS interfaces
        // ===============================
        pub_ = this->create_publisher<geometry_msgs::msg::TwistStamped>(
            "cmd_vel",
            rclcpp::QoS(10)
        );

        sub_ = this->create_subscription<geometry_msgs::msg::TwistStamped>(
            "cmd_vel/raw",
            rclcpp::SensorDataQoS(),
            std::bind(
                &JoyVelRef::send_vel_twist_,
                this,
                std::placeholders::_1
            )
        );

        RCLCPP_INFO(
            get_logger(),
            "JOY ref vel started (symmetric normalized mixing)"
        );
    }

private:
    double max_vel_;
    double scales_;
    double wheel_base_;

    rclcpp::Time last_stamp_;

    rclcpp::Publisher<
        geometry_msgs::msg::TwistStamped
    >::SharedPtr pub_;

    rclcpp::Subscription<
        geometry_msgs::msg::TwistStamped
    >::SharedPtr sub_;

    void send_vel_twist_(
        const geometry_msgs::msg::TwistStamped::SharedPtr msg)
    {
        const rclcpp::Time stamp(msg->header.stamp);
        const rclcpp::Time now = this->now();

        // ===============================
        // 0) Temporal validation
        // ===============================

        const double age = (now - stamp).seconds();

        // Too old
        if (age > 0.2) {
            RCLCPP_WARN(
                get_logger(),
                "Discarding old command: %.3f s old",
                age
            );
            return;
        }

        // Out of order / duplicate
        if (last_stamp_.nanoseconds() != 0 &&
            stamp <= last_stamp_)
        {
            RCLCPP_WARN(
                get_logger(),
                "Discarding out-of-order command"
            );
            return;
        }

        last_stamp_ = stamp;

        // ===============================
        // 1) Joystick -> reference signals
        // ===============================
        const float limit =
            static_cast<float>(max_vel_ * scales_);

        const float v_ref =
            limit * static_cast<float>(msg->twist.linear.x);

        const float wheel_diff =
            limit * static_cast<float>(msg->twist.angular.z);

        // ===============================
        // 2) Symmetric wheel mixing
        //
        // v_l = v - L/2*w
        // v_r = v + L/2*w
        //
        // wheel_diff represents L/2*w
        // ===============================

        float v_l = v_ref - wheel_diff;
        float v_r = v_ref + wheel_diff;

        // ===============================
        // 3) Normalize while preserving
        //    v/w ratio
        // ===============================

        const float max_abs =
            std::max(std::abs(v_l), std::abs(v_r));

        if (max_abs > limit) {
            const float scale = limit / max_abs;

            v_l *= scale;
            v_r *= scale;
        }

        // ===============================
        // 4) Reconstruct physical Twist
        // ===============================

        geometry_msgs::msg::TwistStamped out;

        // IMPORTANT:
        // preserve original generation timestamp
        out.header = msg->header;

        out.twist.linear.x =
            (v_r + v_l) * 0.5f;

        out.twist.angular.z =
            (v_r - v_l) /
            static_cast<float>(wheel_base_);

        pub_->publish(out);
    }
};


int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);

    rclcpp::spin(
        std::make_shared<JoyVelRef>()
    );

    rclcpp::shutdown();

    return 0;
}