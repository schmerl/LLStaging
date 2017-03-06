#! /usr/bin/env python

from __future__ import with_statement
import roslib
import rospy
from std_msgs.msg import String, Int64
import os.path
from mars_notifications.msg import UserNotification

USER_NOTIFICATION_FILE=os.path.expanduser('/test/mars_notifications.txt')

def callback(data):
	message = "%s | %s"%(data.new_deadline,data.user_notification)
	with open(USER_NOTIFICATION_FILE, "a") as logfile:
		logfile.write(message + "\n")
		logfile.flush()
	rospy.loginfo("MARS | %s"%message)

def callbackD(data):
	pub = rospy.Publisher ("/notify_user", UserNotification, queue_size=10);
	msg = UserNotification()
	msg.new_deadline = str(data.data)
	msg.user_notification = "Setting deadline to %s" %str(data.data)
	pub.publish(msg)

def notify_user_listener():
	rospy.init_node('notify_user_node')
	rospy.Subscriber("/notify_user", UserNotification, callback)
	rospy.Subscriber("/notify_user/deadline", Int64, callbackD)
	rospy.spin()

if __name__ == '__main__':
	notify_user_listener()