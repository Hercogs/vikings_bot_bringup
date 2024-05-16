# Vikings Bot bringup package
<hr>

### Description: contains files to bringup files related with Vikings Bot project
<hr>

### Dependencies: ...

<hr>

To enable lidar / depth cam filtering, set parameters in `bringup_first_bot.launch.xml`:
```
<let name='filter_lidar_param' value='true'/>
<let name='filter_depth_cam_param' value='true'/>
<let name='use_lidar_param' value='true'/>
<let name='use_depth_cam_param' value='true'/>
```

To launch gazebo world, execute:
`ros2 launch vikings_bot_bringup start_simulation.launch.xml`

To spawn one robot, execute: 
`ros2 launch vikings_bot_bringup bringup_first_bot.launch.xml`

Probably not working: To spawn two robots, execute: 
`ros2 launch vikings_bot_bringup bringup_two_bots.launch.xml` In Rviz enable second robot visualization.

To move robots with keypad, execute:
```
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=vikings_bot_1/cmd_vel
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=vikings_bot_2/cmd_vel
```

To test Nav2, in Rviz us `2D Goal Pose` button to send goal to robot. 


In case something is not working, let me know!




