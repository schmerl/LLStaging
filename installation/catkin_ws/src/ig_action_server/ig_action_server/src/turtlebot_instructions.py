import rospy
import time
from geometry_msgs.msg import *
from math import *
from tf import TransformListener
from tf import transformations as t
import numpy
import math
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from actionlib_msgs.msg import *
import publisher
from math import radians, pi
import dynamic_reconfigure.client
from std_msgs.msg import String,Bool


def forward(distance, speed, cancel):
	twist = Twist()
	t_taken = distance/speed;
	cmd_vel = rospy.Publisher("cmd_vel_mux/input/teleop", Twist, queue_size=10)
	# listener = TransformListener()
	# listener.waitForTransform("/base_link", "/odom", rospy.Time(0), rospy.Duration(1))
	# (start_t, start_r) = listener.lookupTransform("/base_link", "/odom", rospy.Time())
	# start_transform = t.concatenate_matrices(t.translation_matrix(start_t), t.quaternion_matrix(start_r))
	twist.linear.x = abs(speed)

	rate = rospy.Rate(10)
	now = rospy.get_time()
	end = now + t_taken
	while rospy.get_time() < end and not cancel.is_canceled():
		cmd_vel.publish(twist)
		rate.sleep()
	return True, "Made it"

def charge(seconds, cancel):
  	pub = rospy.Publisher('/energy_monitor/set_charging', Bool, queue_size=10, latch=True)
  	msg = Bool()
	msg.data = True
	# Send charge message every half second for number of seconds
	rospy.loginfo('Charging for %d secs' %int(seconds))
	rate = rospy.Rate(10)

	now = rospy.get_time()
	end = now + seconds
	while rospy.get_time() < end and not cancel.is_canceled():
		pub.publish(msg)
	  	rate.sleep()
	# Turn off charging, sending it multiple times for 1 second
	msg.data = False
	if not cancel.is_canceled():
		for i in range(0, 4):
		  	pub.publish(msg)
		  	rate.sleep()
	return True, ""

def turnDegrees(angle_degrees, angular_vel, clockwise):
	return turnRadians(radians(angle_degrees), angular_vel, clockwise)

def turnRadians(angle_radians, angular_vel, clockwise):
	twist = Twist()
	t_taken = angle_radians/angular_vel;
	cmd_vel = rospy.Publisher("cmd_vel_mux/input/teleop", Twist, queue_size=10)
	# listener = TransformListener()
	# listener.waitForTransform("/base_link", "/odom", rospy.Time(0), rospy.Duration(1))
	# (start_t, start_r) = listener.lookupTransform("/base_link", "/odom", rospy.Time(0))
	# start_transform = t.concatenate_matrices(t.translation_matrix(start_t), t.quaternion_matrix(start_r))
	if clockwise:
		twist.angular.z = -abs(angular_vel)
	else:
		twist.angular.z = abs(angular_vel)	
	rate = rospy.Rate(10)
	now = rospy.get_time()
	end = now + t_taken
	while rospy.get_time() < now:
		cmd_vel.publish(twist)
		rate.sleep()
		# (curr_t,curr_r) = listener.lookupTransform("/base_link", "/odom", rospy.Time(0))
		# current_transform = t.concatenate_matrices(t.translation_matrix(curr_t),t.quaternion_matrix(curr_r))
		# relative = numpy.dot(t.inverse_matrix(start_transform), current_transform)
		# rot_moved, dire, point = t.rotation_from_matrix(relative)
		# print ("angle=%s, moved=%s,stop=%s"%(str(angle_radians),str(rot_moved), str(rot_moved/2>angle_radians)))
		# if abs(rot_moved) > abs(angle_radians):
		# 	done = True
		# 	break
		
	return True, "Done!"

def turnAbs(direction, angular_vel):
	EAST = 0
	NORTH = radians(90)
	WEST = radians(180)
	SOUTH = radians(270)
	target_angle = EAST
	if direction == 'NORTH':
		target_angle = NORTH
	elif direction == 'SOUTH':
		target_angle = SOUTH
	elif direction == 'EAST':
		target_angle = EAST
	elif direction == 'WEST':
		target_angle = WEST
	else:
		rospy.logerr("Direction is not correct")
		return False
	# Get current location of robot
	listener = TransformListener()
	try:
		listener.waitForTransform("/base_link", "/map", rospy.Time(0), rospy.Duration(5))
	except Exception:
		rospy.logerr("Need map transform for TurnAbs to work")
		return False
	(start_t, start_r) = listener.lookupTransform("/base_link", "/map", rospy.Time(0))
	q = (start_r[0], start_r[1], start_r[2], start_r[3])
	yaw = t.euler_from_quaternion(q)[2]

	(rot, clockwise) = calculateTurnAngleRadians(target_angle, yaw)
	return turnRadians(rot, angular_vel, clockwise)

TAU = 2 * math.pi
def calculateTurnAngleRadians(target, yaw):
	a = (yaw-target) % TAU
	b = (target-yaw) % TAU
	if a < b:
		return a, True
	else:
		return b,  False

def calculateTurnAngleDegrees(target, yaw):
	
	(rad, clockwise) = calculateTurnAngleRadians(radians(target), radians(yaw))
	return (degrees(rad), clockwise)

recalibrate_pub = rospy.Publisher("/calibration/commands", String, queue_size=1)


def recalibrate(mode):
  global recalibrate_pub
  msg = String()
  msg.data = 'recalibrate'
  recalibrate_pub.publish(msg) 
  return "OK", True

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

def say(speech):
  if not SETUP_DONE: setup()
  rospy.loginfo(speech)

SETUP_DONE = False

def setup():
  pass
  #publisher.initialize()
  #SETUP_DONE = True
  #rospy.init_node("IG", anonymous=False)

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

  rospy.sleep(1)

def moveTo(x, y):
  move_base_client = publisher.move_base_action_client (); #actionlib.SimpleActionClient("move_base", MoveBaseAction)
  rospy.loginfo ("Go to (%s, %s) pose", x, y)

  goal = MoveBaseGoal()
  goal.target_pose.header.frame_id = 'map'
  goal.target_pose.header.stamp = rospy.Time.now()
  quaternion = t.quaternion_from_euler(0,0,0)
  goal.target_pose.pose = Pose(Point(x,y, 0.000),
                               Quaternion(quaternion[0], quaternion[1], quaternion[2], quaternion[3]))

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

def setVelocity(velocity, type):
	client = dynamic_reconfigure.client.Client('move_base/DWAPlannerROS')
	if type == 'LINEAR':
		params = {'max_vel_x' : velocity, 'max_trans_vel': velocity}
	else:
		params = {'max_rot_vel': velocity, 'min_rot_vel':velocity}
	config = client.update_configuration(params)
	rospy.sleep(0.2)
	rospy.loginfo("Velocity set to " + str(velocity))

def cancel_instruction():
	move_base = publisher.move_base_action_client()
	move_base.cancel_all_goals()

def move(x,y,v,action, w=0):
	print "MOVING TO x:" + str(x) + " y:" + str(y)
	status=True
	msg = "Successfully executed the vertex"
	setVelocity(v, 'LINEAR');
	if action == "Absolute":
		frameType = "map"
	else:
		frameType = 'base_link'

	move_base = publisher.move_base_action_client ()
    
	print "moving ->" + str(frameType)
	goal = MoveBaseGoal()
	goal.target_pose.header.frame_id = frameType
	goal.target_pose.header.stamp = rospy.Time.now()
	goal.target_pose.pose.position.x = x 
	if frameType == 'map':
		goal.target_pose.pose.position.y = y #3 meters
	
	q = t.quaternion_from_euler(0,0,w)
	goal.target_pose.pose.orientation.x = q[0]
	goal.target_pose.pose.orientation.y = q[1]
	goal.target_pose.pose.orientation.z = q[2]
	goal.target_pose.pose.orientation.w = q[3]

	move_base.send_goal(goal)
	success = move_base.wait_for_result()
        
	if not success:
		move_base.cancel_goal()
		rospy.logerr("The base failed to move forward")
		msg = "The base failed to move forward"
		status = False
	else:
		succeeded = move_base.get_state () == GoalStatus.SUCCEEDED
		if not succeeded:
			rospy.logerr ("The base failed to move, status=%s" %succeeded)
			msg = "Move %s failed" %action
			status = False
		else:
			rospy.loginfo("Successfully executed the vertex")
	
	publisher.close_move_base_action_client()
	return status, msg

def moveAbs(x,y,v):
	return move (x,y,v,"Absolute");

def moveRel(x,y,v):
	return move (x,y,v,"Relative");
