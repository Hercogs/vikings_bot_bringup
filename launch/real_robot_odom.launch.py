import os

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, TextSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    ### INPUT ###
    vikings_bot_name_arg = DeclareLaunchArgument("vikings_bot_name",
                default_value="vikings_bot_1",
                description="Namespace of robot - [vikings_bot_1 or vikings_bot_2]"
    )
    use_sim_arg = DeclareLaunchArgument("use_sim", default_value="false",
                description="Use simulation clock or real time"
    )

    
    # Robot state publisher with control
    state_publisher_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution([
                    FindPackageShare("vikings_bot_description"),
                    "launch",
                    "robot_state_publisher.launch.py"
                ])
            ]
        ),
        launch_arguments=[
            ("vikings_bot_name", LaunchConfiguration("vikings_bot_name")),
            ("use_sim", LaunchConfiguration("use_sim")),
        ],
    )

    #  RVIZ configuration file
    rviz_file = "simple_odom.rviz"
    rviz_config_dir = PathJoinSubstitution([
        FindPackageShare("vikings_bot_bringup"), "rviz", rviz_file])

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        parameters=[{
            "use_sim_time": LaunchConfiguration("use_sim"),
        }],
        arguments=["-d", rviz_config_dir]
    )


    return LaunchDescription(
        [
            vikings_bot_name_arg,
            use_sim_arg,
            state_publisher_node,
            rviz_node
        ]
    )