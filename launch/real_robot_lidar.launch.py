import os

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import (LaunchConfiguration,
            PathJoinSubstitution, TextSubstitution,
            EnvironmentVariable)
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    ### INPUT ###
    vikings_bot_name_arg = DeclareLaunchArgument("vikings_bot_name",
                default_value=EnvironmentVariable("ROBOT_NAME"),
                description="Namespace of robot - [vikings_bot_1 or vikings_bot_2]"
    )
    use_sim_arg = DeclareLaunchArgument("use_sim", default_value="false",
                description="Use simulation clock or real time"
    )

    
    # Lidar node
    state_publisher_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution([
                    FindPackageShare("sllidar_ros2"),
                    "launch",
                    "sllidar_s2e_launch.py"
                ])
            ]
        ),
        launch_arguments=[
            ("vikings_bot_name", LaunchConfiguration("vikings_bot_name")),
        ],
    )


    return LaunchDescription(
        [
            vikings_bot_name_arg,
            use_sim_arg,
            state_publisher_node,
        ]
    )