# Vikings Bot bringup package
<hr>
Description: _contains files to bringup files related with Vikings Bot project_
<hr>

### Dependencies: ...

<hr>

### Important
__To make Nav2 working, chnage `path_planner_server` config file `*bt_navigator` line `default_nav_to_pose_bt_xml: "/home/hercogs/ros2_ws/src/vikings_bot/path_planner_server/config/behavior.xml"` to your actual file path!__

<hr>

To launch gazebo world, execute:
`ros2 launch vikings_bot_bringup start_simulation.launch.xml`

To spawn one robot, execute: 
`ros2 launch vikings_bot_bringup bringup_first_bot.launch.xml`

To spawn two robots, execute: 
`ros2 launch vikings_bot_bringup bringup_two_bots.launch.xml` In Rviz enable second robot visualization.

To move robots with keypad, execute:
```
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=vikings_bot_1/cmd_vel
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=vikings_bot_2/cmd_vel
```

To test Nav2, in Rviz us `2D Goal Pose` button to send goal to robot. 


In case something is not working, let me know!




