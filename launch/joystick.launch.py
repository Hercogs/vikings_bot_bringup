# ===========================================================
# |         THIS LAUNCH FILE DOES NOT LAUNCH ODOMETRY ETC   |
# |         IT LAUNCHES ONLY TELEOP TO CONTROL ROBOT WITH   |
# |         JOYSTICK!                                       |
# ===========================================================

from launch import LaunchDescription
from launch_ros.actions import Node, PushRosNamespace
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch.substitutions import (
    LaunchConfiguration, PathJoinSubstitution,
    EnvironmentVariable, PythonExpression
)

from launch_ros.substitutions import FindPackageShare



def generate_launch_description():

    ### INPUT ###
    vikings_bot_name_arg = DeclareLaunchArgument("vikings_bot_name",
                default_value=EnvironmentVariable("ROBOT_NAME"),
                description="Namespace of robot - [vikings_bot_1 or vikings_bot_2]")

    # joystick node
    joystick_config_file = PathJoinSubstitution(
        [FindPackageShare("vikings_bot_bringup"),
         'config', 'joystick.yaml'])
    joystick_cmd_vel_topic = PythonExpression(["'",LaunchConfiguration("vikings_bot_name"), "/cmd_vel'"])
    

    joy_cmd_vel_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare("teleop_twist_joy"),
                    "launch",
                    "teleop-launch.py"
                ])]
        ),
        launch_arguments=[
            ('config_filepath', joystick_config_file),
            ('joy_vel', joystick_cmd_vel_topic)
        ],
    )
    joy_cmd_vel_node_with_namespace = GroupAction(
     actions=[
         PushRosNamespace(LaunchConfiguration("vikings_bot_name")),
         joy_cmd_vel_node,
      ]
   )


    return LaunchDescription(
        [
            vikings_bot_name_arg,

            joy_cmd_vel_node_with_namespace,
        ]
    )
