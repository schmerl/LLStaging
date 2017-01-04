#! /usr/bin/env python

import roslib; roslib.load_manifest('messages')
import rospy
import actionlib
import ig_action_msgs.msg
from gazebo_msgs.msg import ModelStates
from tf import TransformListener

import sys
import traceback
import time
import threading

# A logger that is meant to log information specific to the scoring and logging of the 
# the challenge problem
class ChallengeProblemLogger(object):
  _knownObstacles = {}
  _placedObstacle = False
  _lastgzlog = 0.0
  _tf_listener = None
  
  def __init__(self,name):
    self._name = name;

    self._experiment_started = False
    self._tf_listener = TransformListener()

    # Subscribe to robot pose ground truth from gazebo
    rospy.Subscriber("/gazebo/model_states", ModelStates, callback=self.gazebo_model_monitor,
                     queue_size=1)

  # Whenever we get a report from Gazebo, map the gazebo coordinate to map coordinates and
  # log this
  # Only do this every second - this should be accurate enough
  # TODO: model is assumed to be the third in the list. Need to make this based
  #       on the array to account for obstacles (maybe)
  def gazebo_model_monitor(self, data):
    if (len(data.pose))<=2:
      return
    data_time = rospy.get_rostime().to_sec()
    if ((self._lastgzlog == 0.0) | (data_time - self._lastgzlog >= 1)):
      # Only do this every second

      # Get the turtlebot model state information (assumed to be indexed at 2)    
      tb_pose = data.pose[2]
      tb_position = tb_pose.position
      self._lastgzlog = data_time

      # Do this only if the transform exists
      if self._tf_listener.frameExists("/base_link") and self._tf_listener.frameExists("/map"):
        self._tf_listener.waitForTransform("/map", "/base_link", rospy.Time(0), rospy.Duration(1))
        (trans,rot) = self._tf_listener.lookupTransform("/map", "/base_link",rospy.Time(0))
        rospy.loginfo("BRASS | Turtlebot | {},{}".format(trans[0], trans[1]))
      
      # Log any obstacle information, but do it only once. This currently assumes one obstacle
      # TODO: test this
      if len(data.name) > 3:
        addedObstacles = {}
        removedObstacles = self._knownObstacles.copy()
        for obs in range(3, len(data.name)-1):
          if (data.name[obs] not in self._knownObstacles):
            addedObstacles[data.name[obs]] = obs
          else:
             self._knownObstacles[data.name[obs]] = obs
 	     del removedObstacles[data.name[obs]]
        
        for key, value in removedObstacles.iteritems():
           rospy.logInfo("BRASS | Obstacle {} | removed".format(key))
           del self._knownObstacles[key]

        for key, value in addedObstacles.iteritems():
	   obs_pos = data.pose[value].position
           rospy.logInfo ("BRASS | Obstacle {} | {},{}".format(key, obs_pos.x, obs_pos.y))
	   self._knownObstacles[key] = value

#     if len(data.pose) > 3 & ~self._placedObstacle:
#        # we have an obstacle, so log
#        obs_pose = data.pose[3]
#        obs_position = obs_pose.position
#        rospy.logInfo("BRASS | Obstacle | {},{}".format(obs_position.x, obs_position.y))
#        self._placedObstacle = True
#      elif self._placedObstacle:
#        # obstacle was removed, so log
#	self._placedObstacle = False
#        rospy.loginfo("BRASS | Obstacle | removed")  
    
if __name__ == '__main__':
  rospy.init_node('brass_logger',anonymous=True)
  logger = ChallengeProblemLogger('brass_logger')
  rospy.spin()    

