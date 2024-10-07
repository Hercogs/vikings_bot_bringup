from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from launch.substitutions import (
    LaunchConfiguration, PathJoinSubstitution,
    EnvironmentVariable, PythonExpression
)

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
    use_gui_arg = DeclareLaunchArgument("use_gui", default_value="false",
                description="Use GUI software! Rviz, ..."
    )
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


    #  RVIZ configuration file
    rviz_file = "camera.rviz"
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
            filter_lidar_arg,
            filter_depth_cam_arg,
            safe_classes_arg,
            profile_arg,

            depth_cam_node,
            rs_tf_node,
            sensor_filter_node,
            rviz_node
        ]
    )
