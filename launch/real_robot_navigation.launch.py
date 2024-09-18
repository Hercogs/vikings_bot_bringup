import os

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import (LaunchConfiguration,
            PathJoinSubstitution, TextSubstitution, EnvironmentVariable)
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch.conditions import IfCondition
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
    use_gui_arg = DeclareLaunchArgument("use_gui", default_value="true",
                description="Use GUI software! Rviz, ..."
    )
    map_file_arg = DeclareLaunchArgument('map_file',
                default_value='vnpc_edit.yaml',
                description='Specify map name'
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

    # Lidar node
    lidar_node = IncludeLaunchDescription(
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

    # Map server
    map_server_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution([
                    FindPackageShare("vikings_bot_map_server"),
                    "launch",
                    "map_server.launch.py"
                ])
            ]
        ),
        launch_arguments=[
            ("vikings_bot_name", LaunchConfiguration("vikings_bot_name")),
            ("use_sim", LaunchConfiguration("use_sim")),
            ("map_file", LaunchConfiguration("map_file")),
        ],
    )

    # Localization server
    localization_server_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution([
                    FindPackageShare("vikings_bot_localization_server"),
                    "launch",
                    "spawn_localization.launch.py"
                ])
            ]
        ),
        launch_arguments=[
            ("vikings_bot_name", LaunchConfiguration("vikings_bot_name")),
            ("use_sim", LaunchConfiguration("use_sim")),
        ],
    )

    # Path planner server
    path_planner_server_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution([
                    FindPackageShare("vikings_bot_path_planner_server"),
                    "launch",
                    "spawn_path_planner.launch.py"
                ])
            ]
        ),
        launch_arguments=[
            ("vikings_bot_name", LaunchConfiguration("vikings_bot_name")),
            ("use_sim", LaunchConfiguration("use_sim")),
        ],
    )

     # Display manager node
    display_manager_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution([
                    FindPackageShare("vikings_bot_firmware_py"),
                    "launch",
                    "display_manager.launch.py"
                ])
            ]
        ),
        launch_arguments=[
            ("vikings_bot_name", LaunchConfiguration("vikings_bot_name"))
        ]
    )

    #  RVIZ configuration file
    rviz_file = "simple_navigation.rviz"
    rviz_config_dir = PathJoinSubstitution([
        FindPackageShare("vikings_bot_bringup"), "rviz", rviz_file])

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        parameters=[{
            "use_sim_time": LaunchConfiguration("use_sim"),
        }],
        arguments=["-d", rviz_config_dir],
        condition = IfCondition(
            LaunchConfiguration("use_gui")
        ),
    )


    return LaunchDescription(
        [
            vikings_bot_name_arg,
            use_sim_arg,
            use_gui_arg,
            map_file_arg,

            state_publisher_node,
            lidar_node,
            map_server_node,
            localization_server_node,
            path_planner_server_node,
            display_manager_node,
            rviz_node
        ]
    )
