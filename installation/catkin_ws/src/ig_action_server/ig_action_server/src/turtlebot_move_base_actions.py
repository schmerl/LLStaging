import rospy
import time
from geometry_msgs.msg import Point, Pose, PoseWithCovarianceStamped, Quaternion, Twist
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from actionlib_msgs.msg import *
import publisher
from math import radians, pi
import dynamic_reconfigure.client
from std_msgs.msg import String,Bool
import tf
from tf import transformations as t

SETUP_DONE = False

def setup():
  pass
  #publisher.initialize()
  #SETUP_DONE = True
  #rospy.init_node("IG", anonymous=False)

def say(speech):
  if not SETUP_DONE: setup()
  rospy.loginfo(speech)

def locate(x,y, w):
  if not SETUP_DONE: setup()
  pub = rospy.Publisher('initialpose', PoseWithCovarianceStamped, queue_size=10, latch=True)

  initial_pose = PoseWithCovarianceStamped()

  initial_pose.header.stamp = rospy.Time.now()
  initial_pose.header.frame_id = 'map'

  initial_pose.pose.pose.position.x = x
  initial_pose.pose.pose.position.y = y
  initial_pose.pose.pose.position.z = 0
  q = t.quaternion_from_euler(0,0,w)
  initial_pose.pose.pose.orientation.x = q[0]
  initial_pose.pose.pose.orientation.y = q[1]
  initial_pose.pose.pose.orientation.z = q[2]
  initial_pose.pose.pose.orientation.w = q[3]
  initial_pose.pose.covariance = [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.06853891945200942]

  pub.publish(initial_pose)

  time.sleep(1)



def moveTo(x, y):
  move_base_client = publisher.move_base_action_client (); #actionlib.SimpleActionClient("move_base", MoveBaseAction)
  rospy.loginfo ("Go to (%s, %s) pose", x, y)

  goal = MoveBaseGoal()
  goal.target_pose.header.frame_id = 'map'
  goal.target_pose.header.stamp = rospy.Time.now()
  goal.target_pose.pose = Pose(Point(x,y, 0.000),
                               Quaternion(quaternion['r1'], quaternion['r2'], quaternion['r3'], quaternion['r4']))

  move_base_client.send_goal(goal)

  result = move_base_client.wait_for_result()

  state = move_base_client.get_state()
  success = False
  msg = ""

  if result and state == GoalStatus.SUCCEEDED:
    success = True

  if success:
    rospy.loginfo("Reached the destination")
    msg = "Reached the destination"
  else:
    rospy.loginfo("Unable to reach destination")
    msg = "Unable to reach destination"

  # Sleep to give the last log messages time to be sent
  rospy.sleep(1)

  publisher.close_move_base_action_client()
  return success,msg;
 



def move(distance, angular, speed, delta_y, rotation):
  return moveAllAtOnce(distance, angular, speed, delta_y, rotation)
  
  if not SETUP_DONE: setup()
  cmd_vel = rospy.Publisher("cmd_vel_mux/input/navi", Twist, queue_size=10)
  rospy.sleep(1)
  
  # create a Twist message, fill it in to drive forward
  twist = Twist()
  if speed != 0:
    move_base = publisher.move_base_action_client (); #actionlib.SimpleActionClient("move_base", MoveBaseAction)
    #move_base.wait_for_server(rospy.Duration(10))
    for i in range(int(distance*2)):
      rospy.loginfo("Doing iteration " + str(i) + " of " + str (distance*2))
      goal = MoveBaseGoal()
      goal.target_pose.header.frame_id = 'base_link'
      goal.target_pose.header.stamp = rospy.Time.now()
      goal.target_pose.pose.position.x = 0.5 #3 meters
      goal.target_pose.pose.orientation.w = 1.0 #go forward
      
      move_base.send_goal(goal)

      success = move_base.wait_for_result(rospy.Duration(30))

      if not success:
        move_base.cancel_goal()
        rospy.loginfo("The base failed to move forward .5 meters for some reason")
        break
      else:
        # We made it!
        state = move_base.get_state()
        if state == GoalStatus.SUCCEEDED:
          continue
    publisher.close_move_base_action_client()
  # create a twist message, fill it in to turn
  else:
    twist.angular.z = radians(45)*rotation #0.785398*2*rotation    # 90 deg/s
    for i in range(0,int(10*angular)):
      cmd_vel.publish(twist)
      rospy.sleep(0.2)

def moveAllAtOnce(distance, angular, speed, delta_y, rotation):
  if not SETUP_DONE: setup()

  rospy.sleep(1)
  
  # create a Twist message, fill it in to drive forward
  twist = Twist()
  if speed != 0:
    move_base = publisher.move_base_action_client()
    # go the full distance
    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = 'base_link'
    goal.target_pose.header.stamp = rospy.Time.now()
    goal.target_pose.pose.position.x = distance
    goal.target_pose.pose.orientation.w = 1



    move_base.send_goal(goal)
    success = move_base.wait_for_result()
#    for i in range(int(distance*2)):
#      goal = MoveBaseGoal()
#      goal.target_pose.header.frame_id = 'base_link'
#      goal.target_pose.header.stamp = rospy.Time.now()
#      goal.target_pose.pose.position.x = 0.5 #3 meters
#      goal.target_pose.pose.orientation.w = 1.0 #go forward
      
#      move_base.send_goal(goal)

#      success = move_base.wait_for_result(rospy.Duration(10))

#      if not success:
#        move_base.cancel_goal()
        #rospy.loginfo("The base failed to move forward 3 meters for some reason")
#        break
#      else:
        # We made it!
#        state = move_base.get_state()
#        if state == GoalStatus.SUCCEEDED:
#          continue
    publisher.close_move_base_action_client()
    return success, ""
  # create a twist message, fill it in to turn
  else:
    twist.angular.z = radians(45)*rotation #0.785398*2*rotation    # 90 deg/s
    for i in range(0,int(10*angular)):
      cmd_vel.publish(twist)
      rospy.sleep(0.2)
    return True, ""



def recalibrate(mode):
  return False, "Recalibrate is not yet implemented"

kinect_on = True

def configure_localization(mode):
  global kinect_on
  if mode == 2:
    kinect = True
    kinect_array = 550
    update_min_a = 0.0
    update_min_d = 0.2
  elif mode == 1:
    kinect = True
    kinect_array = 640
    update_min_a = pi / 6
    update_min_d = 0.6
  elif mode == 0:
    kinect = False
  else: 
    return False, "Unsupported mode " %mode

  if not kinect:
    pub = rospy.Publisher("/sensor/kinect/onoff", String, queue_size = 10, latch=True)
    msg = String()
    msg.data = "off"
    for i in range(0, 4):
      pub.publish(msg)
      rospy.sleep(0.25)
    kinect_on = False
    return True, ""
  else:
    # client = dynamic_reconfigure.client.Client('amcl')
    # params = {'kinect_array' : kinect_array, 'update_min_a' : update_min_a, 'update_min_d' : update_min_d}
    # config = client.update_configuration(params)
    
    if not kinect_on:
      pub = rospy.Publisher("/sensor/kinect/onoff", String, queue_size = 10, latch=True)
      msg = String()
      msg.data = "on"
      for i in range(0, 4):
        pub.publish(msg)
        rospy.sleep(0.25)
      kinect_on = True
    return True,""

