import rospy
import sys
from mars_notifications.msg import UserNotification

def notify(time, message):
	pub = rospy.Publisher('/notify_user', UserNotification, queue_size=1)
	rospy.init_node('notify', anonymous=True)
	notification = UserNotification()
	notification.new_deadline=time
	notification.user_notification=message
	pub.publish(notification)
	r = rospy.Rate(1)
	r.sleep()
	rospy.signal_shutdown('Message sent presumably')

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print("Usage: notify <time> <message> %s '%s'" %(len(sys.argv), sys.argv))
		sys.exit(1)
	notify (sys.argv[1], sys.argv[2])