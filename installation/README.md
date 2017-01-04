# CMU MARS Example Deployment and Base Case

This repostitory contains teh CMU MARS demonstraction of the a base TurtleBot in a simulated environment. This repository contains the files to set up and deploy this initial demonstration.

Currently, the demonstration just starts the robot and gives it instructions to move 8m to the right.

## Deploying the Example

Build the VM which will contain the example.

```
vagrant up
```

This command will provision a virtual machine called `cmu-mars` and install the required software. The software installed is:

```
Ansible -- for installing ros
Java -- for future components
XServer Dummy -- for running headless graphics operations
```

Ansible is run by Vagrant to install ROS and TurtleBot components:

```
ROS Indigo Desktop Full
ROS Install
ROS Indigo TurtleBot
ROS Indigo TurtleBot Simulator
TurtleBot Kobuki Base definitions
ROS in Concert
Python Ply
```

After running, Vagrant will have set up ROS, X-Server, TurtleBot definitions, Gazebo Simulator, Instruction Graph Interpreter, and the sample world. Paths for running the demo will be defined in ~/.bashrc, and scripts for running the demo will be in ~/.

## Running the demo

To run the demo, ssh into the machine using `vagrant ssh` and run the command:

```
./run-cp1.sh
```

This will start the dummy X Server, and the TurtleBot simulation, and give it instructions. All in all, it takes some minutes to run. The simulation will be finished when the following is output on the console:

```
Finished!
End output:  [<parserIG.Action object at 0xxxxxxxxxxxxx>, <parserIG.Action object at 0xxxxxxxxxxxxx>]
```

At this point, press Ctrl-C to exit out.
