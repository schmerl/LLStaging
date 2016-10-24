#!/usr/bin/python
##############################################
## The python ros node can be used to convert
## Quaternion representation from odom and IMU 
## to eulers using tf transformations.
## Based on example from Thomas D. 
## <https://denewiler.us/cv>
##############################################
import roslib; roslib.load_manifest('messages')
import rospy
import tf


from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from messages.msg import euler

class EulerConvertor():
	_euler_msg = euler()
	_new_msg = False

	def __init__(self):

		rospy.Subscriber("imu", Imu, self.imu_callback)
		rospy.Subscriber("odom", Odometry, self.odom_callback)
		publish = rospy.Publisher("euler_orientation", euler, queue_size=None)
		rospy.loginfo("Euler orientation convertor is running")

		while not rospy.is_shutdown():
			if self._new_msg:
				publish.publish(self._euler_msg)
				self._new_msg = False

	def imu_callback(self ,msg):
		orientation = msg.orientation
		
		self.create_euler(msg.header.stamp, orientation)

	def odom_callback(self, msg):
		orientation = msg.pose.pose.orientation
		self.create_euler(msg.header.stamp, orientation)

	def create_euler(self, stamp, orientation):
		(r, p, y) = tf.transformations.euler_from_quaternion([orientation.x, orientation.y, orientation.z, orientation.w])
		self._euler_msg.header.stamp = stamp
		self._euler_msg.roll = r
		self._euler_msg.pitch = p
		self._euler_msg.yaw = y
		self._new_msg = True

if __name__ == "__main__":
	rospy.init_node("euler_orientation")
	try:
		EulerConvertor()
	except rospy.ROSInterruptException:
		rospy.logerr('Euler orientation failed')
