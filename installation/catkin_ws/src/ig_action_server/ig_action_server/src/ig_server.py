#! /usr/bin/env python

import roslib; roslib.load_manifest('ig_action_msgs')
import roslib; roslib.load_manifest('messages')
import rospy

import actionlib
import ig_action_msgs.msg

import ply.lex as lex
import lexerIG
import ply.yacc as yacc
import parserIG
import statics

import sys

from constants import *
from statics import findn
import turtlebot_move_base_actions as turtlebot
import turtlebot_actions_2 as turtlebot2

import traceback

from orientation import Orientation
import time

from messages.msg import euler

lexer = lex.lex(module=lexerIG)
parser = yacc.yacc(module=parserIG)

class IGServer(object):
	_feedback = ig_action_msgs.msg.InstructionGraphFeedback()
	_result = ig_action_msgs.msg.InstructionGraphResult()
	_init_time = None
	_init_yaw = None
	_yaw_with_drift = None
	_yaw_with_drift_time = None

	def __init__(self, name):
		self._name = name
		self._as = actionlib.SimpleActionServer(self._name, ig_action_msgs.msg.InstructionGraphAction, execute_cb=self.execute_cb, auto_start = False)
		self._as.start()
		rospy.loginfo('IG action server is running!')
		rospy.Subscriber("euler_orientation", euler, self.euler_callback)
		rospy.sleep(10)
		self._init_yaw = self._yaw_with_drift
		self._init_time = self._yaw_with_drift_time
		print str(self._init_yaw)


	def execute_cb(self, goal):
		# Setting the rate of execution.
		r =rospy.Rate(1)
		self._success = True		

		# Appending the feedback for goal recieved.
		self.publish_feedback('Recieved new goal!')
		rospy.loginfo('Recieved a new goal: %s' % (goal.order))

		# start core code
		self.publish_feedback('Parsing goal')
		rospy.loginfo('Parsing goal')
		try:
			ast = parser.parse(goal.order)
		except Exception, e:
			self._success = False
			print e
			rospy.loginfo('Failed parsing')

			traceback.print_exc()
		else:
			self.publish_feedback('Validating instructions')
			assert(statics.valid(ast))

			self.publish_feedback('Executing graph')
			rospy.loginfo('Executing the graph')
			self.eval(ast)
		
		# end core code
		r.sleep()

		# On success setting results topic
		if self._success:
			self.publish_result('Execution for goal completed successfully')
			rospy.loginfo('Goal completed successfully')
		else:
			self.publish_result('Execution for goal failed')
			rospy.loginfo('Goal failed')

	def publish_feedback(self, feedback):
		# Appending the feedback for goal recieved.
		self._feedback.sequence = feedback
		self._as.publish_feedback(self._feedback)

	
	def publish_result(self, result):
		# Appending the results for goal completed.
		self._result.sequence = result
		self._as.set_succeeded(self._result)

	def doaction(self, action):
		# we currently only support moving and saying in this simulation
		if action.operator == MOVE:
			(distance, angular, speed, delta_y, rotation) = action.params
			print "Moving for distance %s at rotation %s with a speed of %s %s %s" \
			%(distance, angular, speed, delta_y, rotation)
			self.publish_feedback("Moving for distance %s at rotation %s with a speed of %s %s %s" \
			%(distance, angular, speed, delta_y, rotation))
			turtlebot.move(distance, angular, speed, delta_y, rotation)
		elif action.operator == SAY:
			(s,) = action.params
			turtlebot.say(s)
		elif action.operator == LOCATE:
			(x,y) = action.params
			self.publish_feedback("Locating inital pose of robot to (%s, %s)" %(x,y))
			turtlebot.locate(x,y)
		elif action.operator == MOVETO:
			(x,y) = action.params
			self.publish_feedback("Moving to pose of (%s, %s)" %(x,y))
			turtlebot.moveTo (x,y)
		elif action.operator == MOVEABS:
			print str(self._yaw_with_drift)
			(x,y,v) = action.params # x,y coordinates on the map and velocity for movement.
			turtlebot2.moveAbs(x,y,v)
		elif action.operator == MOVEREL:
			(x,y,v) = action.params # x,y distance forward on the map and velocity for movement.
			turtlebot2.moveRel(x,y,v)
		elif action.operator == TURNABS:
			(d,r) = action.params # direction and rotational velocity. d = N, S, E, W (North, South, East, West)
			turtlebot2.turnAbs(d, r, self._init_time, self._init_yaw, self._yaw_with_drift_time, self._yaw_with_drift)
		elif action.operator == TURNREL:
			(a,r) = action.params # Angle and rotational velocity.
			turtlebot2.turnRel(a,r)
		else:
			self.publish_feedback("Runtime Error: Unsupported action!");
			self._success = False

	def checkcond(self, cond):
		# we currently only support checking for visible objects and if an object is
		# nearby
		if cond.operator == VISIBLE:
			print "Checking if %s is visible..." %cond.params[0]
			print "Is %s visible?" %cond.params[0]
			ans = raw_input()
			return ans in ("yes", "y", "", "\n")
		elif cond.operator == STOP:
			print "Checking if %s is within %s distance..." %(cond.params[1], cond.params[0])
			print "Is %s within %s distance?" %(cond.params[1], cond.params[0])
			ans = raw_input()
			return ans in ("yes", "y", "", "\n")

	def trystep(self, config):
		(n, vs, I, O) = config
		v = findn(vs, n)
		(n, c) = v.params
		if c.operator == END:
			return (TERMINATED, None)
		elif I == [] and (c.operator in (DOUNTIL, IFELSE)):
			return (WAITING, None)
		elif c.operator == DOONCE:
			(a, n2) = c.params
			self.doaction(a)
			return (STEP, (n2, vs, I, [a] + O))
		elif c.operator == DOUNTIL:
			(a, cnd, n2) = c.params
			b = checkcond(cnd)
			self.doaction(a)
			if b:
		  		return (STEP, (n2, vs, I, [a] + O))
			else:
		  		return (STEP, (n, vs, I, [a] + O))
		elif c.operator == IFELSE:
			(cnd, n2, n3) = c.params
			b = checkcond(cnd)
			if b:
		  		return (STEP, (n2, vs, I, O))
			else:
		  		return (STEP, (n3, vs, I, O))
		elif c.operator == GOTO:
			(n2,) = c.params
			return (STEP, (n2, vs, I, O))
		else:
			self.publish_feedback("Runtime Error: Unsupported action!");
			self._success = False

	def eval(self, ast):
		(v, vs) = ast.params
		(n, c) = v.params
		config = (n, [v]+vs, [True], [])
		while True:
			(status, config2) = self.trystep(config)
			if status == WAITING:
			  print "Robot is waiting for input! But this shouldn't happen in this simulation! What's going on?"
			  break
			elif status == TERMINATED:
			  print "Finished!"
			  self.publish_feedback("Finished!");
			  break
			else:
			  config = config2
		(_, _, _, O) = config

	def euler_callback(self, msg):
		self._yaw_with_drift = msg.yaw
		self._yaw_with_drift_time = time.time()



if __name__ == "__main__":
	rospy.init_node('ig_action_server')
	igserver = IGServer('ig_action_server')
	rospy.spin()




