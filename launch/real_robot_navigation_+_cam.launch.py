import os
import re

import launch
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    LogInfo,
    ExecuteProcess,
    RegisterEventHandler
)
from launch.substitutions import (
    LaunchConfiguration, PathJoinSubstitution, TextSubstitution,
    EnvironmentVariable, PythonExpression
)
from launch.event_handlers import OnProcessIO
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch.conditions import IfCondition
from launch_ros.substitutions import FindPackageShare


# Clean string
def escape_ansi(line):
    return re.sub(r'\033\[(\d|;)+?m', '', line)

# Create event handler that waits for an output message and then returns actions
def on_matching_output(matcher: str, result: launch.SomeActionsType):
    def on_output(event: OnProcessIO):
        for line in event.text.decode("ascii").splitlines():
            if matcher in escape_ansi(line):
                return result

    return on_output


def generate_launch_description():

    diff_drive_loaded_message = "Configured and activated diffbot_base_controller"

    ### INPUT ###
    vikings_bot_name_arg = DeclareLaunchArgument("vikings_bot_name",
                default_value=EnvironmentVariable("ROBOT_NAME"),
                description="Namespace of robot - [vikings_bot_1 or vikings_bot_2]"
    )
    use_sim_arg = DeclareLaunchArgument("use_sim", default_value="false",
                description="Use simulation clock or real time"
    )
    use_gui_arg = DeclareLaunchArgument("use_gui", default_value="false",
                description="Use GUI software! Rviz, ..."
    )
    map_file_arg = DeclareLaunchArgument('map_file',
                default_value='vnpc_full.yaml',
                description='Specify map name'
    )
    use_lidar_arg = DeclareLaunchArgument(
                name='use_lidar',
                default_value='true',
                description='Use lidar for navigation')
    use_depth_cam_arg = DeclareLaunchArgument(
                name='use_depth_cam',
                default_value='false',
                description='Use depth camera for navigation')
    filter_lidar_arg = DeclareLaunchArgument(
                name='filter_lidar',
                default_value='false',
                description='Filter lidar data based on segmentation model')
    filter_depth_cam_arg = DeclareLaunchArgument(
                name='filter_depth_cam',
                default_value='false',
                description='Filter depth camera data based on segmentation model')
    safe_classes_arg = DeclareLaunchArgument(
        name='safe_classes',
        default_value='[-1]',
        description='A list of classes that are considered a safe obstacle.'
    )
    profile_arg = DeclareLaunchArgument(
        name='profile',
        default_value='640x480x30',
        description='Set resolution and FPS for rgb and depth cameras'
    )
    camera_name = PythonExpression(["'",LaunchConfiguration("vikings_bot_name"),"_camera'"])

    # Robot state publisher with control
    state_publisher_node = ExecuteProcess(
        name="state_publisher_node",
        cmd=[
            "ros2",
            "launch",
            PathJoinSubstitution([
                    FindPackageShare("vikings_bot_description"),
                    "launch",
                    "robot_state_publisher.launch.py"
            ]),
            PythonExpression(["'vikings_bot_name:=", LaunchConfiguration("vikings_bot_name"), "'"]),
            PythonExpression(["'use_sim:=", LaunchConfiguration("use_sim"), "'"]),

        ],
        output="screen",
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

    # Realsense depth cam node
    depth_cam_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution([
                    FindPackageShare("realsense2_camera"),
                    "launch",
                    "rs_launch.py"
                ])
            ]
        ),
        launch_arguments=[
            ("camera_namespace", LaunchConfiguration("vikings_bot_name")),
            ("camera_name", camera_name), # this renames the node, topics and frame ids
            ("align_depth.enable", "true"),
            ("depth_module.depth_profile", LaunchConfiguration('profile')),
            ("rgb_camera.color_profile", LaunchConfiguration('profile')),
            ("pointcloud.enable","false"),
        ],
    )

    # add a TF tree relation between /vikings_bot_x/camera_link and realsense camera frame
    rs_tf_node = Node(
            package = "tf2_ros",
            executable = "static_transform_publisher",
            arguments = ["0", "0", "0", "0", "0", "0",
                        PythonExpression(["'",LaunchConfiguration("vikings_bot_name"), "/camera_link'"]), #parent
                        PythonExpression(["'",camera_name,"_link'"])], #child
    )

    # Point cloud processor node
    sensor_filter_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution([
                    FindPackageShare("vikings_bot_point_cloud_processor"),
                    "launch",
                    "pc_processor.launch.py"
                ])
            ]
        ),
        launch_arguments=[
            ("use_sim_time", LaunchConfiguration("use_sim")),
            ("robot_name", LaunchConfiguration("vikings_bot_name")),
            ("camera_name", camera_name),
            ("safe_classes", LaunchConfiguration("safe_classes")), # see "Classes for deeplabv3_mobilenet_v3_large" comment
            ("vis_sem_seg", "false"),
            ("seg_bb_type", "0"),
            ("seg_bb_pad", "0"),
            ("filter_buffer_len", "60"),
            ("filter_prob_threshold", "0.5"),
            # main arguments:
            ("filter_lidar", LaunchConfiguration("filter_lidar")),
            ("filter_depth_cam", LaunchConfiguration("filter_depth_cam")),
            ("perf_seg_sem", "true"),
        ]
    )
    """
    Classes for deeplabv3_mobilenet_v3_large:
    __background__: 0,
    aeroplane: 1,
    bicycle: 2,
    bird: 3,
    boat: 4,
    bottle: 5,
    bus: 6,
    car: 7,
    cat: 8,
    chair: 9,
    cow: 10,
    diningtable: 11,
    dog: 12,
    horse: 13,
    motorbike: 14,
    person: 15,
    pottedplant: 16,
    sheep: 17,
    sofa: 18,
    train: 19,
    tvmonitor: 20,
    """

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
            #arguments to set topics
            ("use_lidar", LaunchConfiguration("use_lidar")),
            ("use_depth_cam", LaunchConfiguration("use_depth_cam")),
        ],
    )
    delay_navigation_nodes = RegisterEventHandler(
        event_handler=OnProcessIO(
            target_action=state_publisher_node,
            on_stdout=on_matching_output(
                diff_drive_loaded_message,
                [
                    # rs_tf_node,
                    # sensor_filter_node,
                    map_server_node,
                    localization_server_node,
                    path_planner_server_node,
                ]
            )
        )
    )

    # Display manager node
    display_manager_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution([
                    FindPackageShare("vikings_bot_display_manager"),
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
    rviz_file = "rviz_config_sem.rviz"
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
            use_lidar_arg,
            use_depth_cam_arg,
            filter_lidar_arg,
            filter_depth_cam_arg,
            safe_classes_arg,
            profile_arg,

            state_publisher_node,
            lidar_node,
            depth_cam_node,
            rs_tf_node,
            sensor_filter_node,
            delay_navigation_nodes,
            display_manager_node,
            rviz_node
        ]
    )
