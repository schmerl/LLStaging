# Euler Orientation Convertor
The convertor creates a ros node. The node continuously converts odom and imu quaternion orientations to euler pitch, roll and yaw. This is based on the initial work by Thomas D <https://denewiler.us/cv> .

## Setup

- Clone the project using:
```
git clone https://github.com/ekanshgupta90/euler_orientation_convertor.git
```

- Move the files to your catkin workspace src directory.
```
cp -r ./* <catkin_ws>/src/
```

by default
```
cp -r ./* ~/catkin_ws/src/
```

- Make the source file (you need to be in catkin workspace directory):
```
cd ..

catkin_make
```

- Add the build files to environment:
```
source devel/setup.bash
```

- Run rospack to add the packages to roscd:
```
rospack depends1 euler_orientation
```

## Running

- Run ROS Gazebo
```
roslaunch turtlebot_gazebo turtlebot_world.launch
```

- Run AMCL
```
roslaunch turtlebot_gazebo amcl_demo.launch
```

- Run Rviz
```
roslaunch turtlebot_rviz_launchers view_navigation.launch
```

- Run Euler orientation convertor
```
roscd euler_orientation/src
python eiuler_orientation.py
```

- Reading messages
```
rostopic echo euler_orientation
```

