from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch.conditions import IfCondition
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
    use_gui_arg = DeclareLaunchArgument("use_gui", default_value="true",
                description="Use GUI software! Rviz, ..."
    )
    map_file_arg = DeclareLaunchArgument('map_file',
                default_value='vnpc_edit.yaml',
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
    profile_arg = DeclareLaunchArgument(
        name='profile',
        default_value='640x480x30',
        description='Set resolution and FPS for rgb and depth cameras'
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
            #("camera_name", PythonExpression(["'",LaunchConfiguration("vikings_bot_name"),"_camera'"])), # this renames the node, topics and frame ids
            ("align_depth.enable", "true"),
            ("depth_module.depth_profile", LaunchConfiguration('profile')),
            ("rgb_camera.color_profile", LaunchConfiguration('profile')),
            ("pointcloud.enable","true")
        ],
    )

    # add a TF tree relation between /vikings_bot_x/camera_link and realsense camera frame
    # TODO: find a better way to fix issue. Ideally camera_link (from realsense node) should be renamed to vikings_bot_1/camera_link
    rs_tf_node = Node(
            package = "tf2_ros",
            executable = "static_transform_publisher",
            arguments = ["0", "0", "0", "0", "0", "0",
                        PythonExpression(["'",LaunchConfiguration("vikings_bot_name"), "/camera_link'"]), #parent
                        "camera_link"], #child
                        #PythonExpression(["'",LaunchConfiguration("vikings_bot_name"),"_camera_link'"])], #child
            
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
            ("camera_name", "camera"),
            ("safe_classes", "[5]"), # see "Classes for deeplabv3_mobilenet_v3_large" comment #TODO add CLI argument
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
            ("filter_lidar", LaunchConfiguration("filter_lidar")),
            ("filter_depth_cam", LaunchConfiguration("filter_depth_cam")),
        ],
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
            use_lidar_arg,
            use_depth_cam_arg,
            filter_lidar_arg,
            filter_depth_cam_arg,
            profile_arg,

            state_publisher_node,
            lidar_node,
            depth_cam_node,
            rs_tf_node,
            sensor_filter_node,
            map_server_node,
            localization_server_node,
            path_planner_server_node,
            rviz_node
        ]
    )
