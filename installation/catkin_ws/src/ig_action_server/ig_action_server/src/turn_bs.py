import rospy
import time
from geometry_msgs.msg import *
from math import *
from tf import TransformListener
from tf import transformations as t
import numpy
import math

# def olfforward(distance, speed):
# 	twist = Twist()
# 	cmd_vel = rospy.Publisher("cmd_vel_mux/input/teleop", Twist, queue_size=10)
# 	listener = TransformListener()
# 	listener.waitForTransform("/base_link", "/odom", rospy.Time(0), rospy.Duration(1))
# 	(start_t, start_r) = listener.lookupTransform("/base_link", "/odom", rospy.Time())
# 	start_transform = t.concatenate_matrices(t.translation_matrix(start_t), t.quaternion_matrix(start_r))
# 	twist.linear.x = abs(speed)
# 	rate = rospy.Rate(10)
# 	done = False
# #	for i in range(int((10*distance)/speed)):
# #		cmd_vel.publish(twist)
# #		rate.sleep()

# 	while not done:
# 		cmd_vel.publish(twist)
# 		rate.sleep()
# 		(curr_t, curr_r) = listener.lookupTransform("/base_link", "/odom", rospy.Time(0))
# 		current_transform = t.concatenate_matrices(t.translation_matrix(curr_t), t.quaternion_matrix(curr_r))
# 		relative = numpy.dot(t.inverse_matrix(start_transform), current_transform)
# 		(x, y, z) = t.translation_from_matrix(relative)
# 		print ("distance=%s, moved=%s,stop=%s"%(str(distance),str(x), str(abs(x)>abs(distance))))

# 		if abs(x) > abs(distance):
# 			done = True
# 			break
# 	return done, "Made it"

# def add_secs_to_time(timeval, secs_to_add):
#     dummy_date = datetime.date(1, 1, 1)
#     full_datetime = datetime.datetime.combine(dummy_date, timeval)
#     added_datetime = full_datetime + datetime.timedelta(seconds=secs_to_add)
#     return added_datetime.time()

def forward(distance, speed):
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
	while rospy.get_time() < end:
		cmd_vel.publish(twist)
		rate.sleep()
	return True, "Made it"

def charge(seconds):
  	pub = rospy.Publisher('/energy_monitor/set_charging', Bool, queue_size=10, latch=True)
  	msg = Bool()
	msg.data = True
	# Send charge message every half second for number of seconds
	rospy.log('Charging for %d secs' %int(seconds))
	rate = rospy.Rate(10)

	now = rospy.get_time()
	end = now + seconds
	while rospy.get_time() < end:
		pub.publish(msg)
	  	rate.sleep()
	# Turn off charging, sending it multiple times for 1 second
	msg.data = False
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
	listener = TransformListener()
	listener.waitForTransform("/base_link", "/odom", rospy.Time(0), rospy.Duration(1))
	(start_t, start_r) = listener.lookupTransform("/base_link", "/odom", rospy.Time(0))
	start_transform = t.concatenate_matrices(t.translation_matrix(start_t), t.quaternion_matrix(start_r))
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
		
	return done, "Done!"

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

if __name__ == "__main__":
	# (rot, clockwise) = calculateTurnAngleDegrees(90, 0)
	# print ("rotate %s, clockwise %s" %(str((rot)), str(clockwise)))
	# (rot, clockwise) = calculateTurnAngleDegrees(270, 180)
	# print ("rotate %s, clockwise %s" %(str((rot)), str(clockwise)))
	# (rot, clockwise) = calculateTurnAngleDegrees(90, 120)
	# print ("rotate %s, clockwise %s" %(str((rot)), str(clockwise)))
	# (rot, clockwise) = calculateTurnAngleDegrees(90, 45)
	# print ("rotate %s, clockwise %s" %(str((rot)), str(clockwise)))


	rospy.init_node('Turner')
	# ret = turnDegrees(90,3.14/4,True)
	ret = move(5,.5)
	if ret:
		print ("Turned")
	else:
		print ("Didn't turn")



