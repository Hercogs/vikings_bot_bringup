# Vikings Bot bringup package

This package conatains files to bringup nodes related to Vikings Bot project.

## Setup

### Setup Udev rules for joystick:
```
sudo bash udev/create_udev_rules.sh
```
Rules can be deleted by executing ```delete_udev_rules.sh``` script the same way.

### Install dependencies:
```
rosdep install -y --from-paths src --ignore-src
```

## Launch files

__This package contains multiple launch files. Main ones are:__

__Real robot:__

* ```real_robot_navigation_+_cam.launch.py``` - Launch all components on real robot.

* Other launch files for real robot launch parts of system, e.g. camera, localizaiton, navigation etc.

__Simulation:__

* ```start_simulation.launch.xml``` - Start Gazebo for simulation.
* ```bringup_first_bot.launch.xml``` - Simulate 1 robot.
* ```bringup_two_bots.launch.xml``` - Simulate 2 robots.



## Simulation

### Configuration
To enable lidar / depth cam filtering, set parameters in `bringup_first_bot.launch.xml` (only for 1 robot):
```
<let name='filter_lidar_param' value='true'/>
<let name='filter_depth_cam_param' value='true'/>
<let name='use_lidar_param' value='true'/>
<let name='use_depth_cam_param' value='true'/>
```
### Start simulation
__Launch gazebo world:__

```
ros2 launch vikings_bot_bringup start_simulation.launch.xml
```

__A) To spawn one robot, execute:__
```
ros2 launch vikings_bot_bringup bringup_first_bot.launch.xml
```

__B) To spawn two robots, execute:__
```
ros2 launch vikings_bot_bringup bringup_two_bots.launch.xml
```
In Rviz enable second robot visualization.

__To move robots with keypad, execute:__

Vikings Bot 1:
```
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=vikings_bot_1/cmd_vel
```

Vikings Bot 2:
```
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=vikings_bot_2/cmd_vel
```

__To test Nav2, in Rviz us `2D Goal Pose` button to send goal to robot.__


In case something is not working, let me know!




