#! /usr/bin/env python

import roslib; roslib.load_manifest('ig_action_msgs')
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
import turn_bs as tb_no_movebase

import traceback

# from orientation import Orientation
import time

#from messages.msg import euler
import tf

lexer = lex.lex(module=lexerIG)
parser = yacc.yacc(module=parserIG)


class IGServer(object):
	_feedback = ig_action_msgs.msg.InstructionGraphFeedback()
	_result = ig_action_msgs.msg.InstructionGraphResult()
	_init_time = None
	_tf = None

	def __init__(self, name):
		self._name = name
		self._as = actionlib.SimpleActionServer(self._name, ig_action_msgs.msg.InstructionGraphAction, execute_cb=self.execute_cb, auto_start = False)
		self._as.start()
		rospy.loginfo('IG action server is running!')	
		self._tf = tf.TransformListener()
#		rospy.Subscriber("euler_orientation", euler, self.euler_callback)
#		rospy.sleep(10)
		

	def execute_cb(self, goal):
		# Setting the rate of execution.
		r =rospy.Rate(1)
		self._success = True		

		# Appending the feedback for goal recieved.
		self.publish_feedback('Recieved new goal!')
		rospy.loginfo('BRASS | IG | Recieved a new goal: %s' % (goal.order))

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
			self.publish_feedback('Received new valid IG: %s' %(goal.order))
			self.publish_feedback('Executing graph')
			rospy.loginfo('Executing the graph')
			self.eval(ast)
		
		# end core code
		#r.sleep()

		# On success setting results topic
		if self._success:
			self.publish_result('Execution for goal completed successfully')
			rospy.loginfo('BRASS | IG | Goal completed successfully')
		else:
			self.publish_result('Execution for goal failed')
			rospy.loginfo('BRASS | IG | Goal failed')

	def publish_feedback(self, feedback):
		# Appending the feedback for goal recieved.
		self._feedback.sequence = feedback
		self._as.publish_feedback(self._feedback)

	
	def publish_result(self, result):
		# Appending the results for goal completed.
		self._result.sequence = result
		self._as.set_succeeded(self._result)

	def doaction(self, action, node):
		# we currently only support moving and saying in this simulation
		status = True
		msg = ""
		print('Executing %s'%action.operator)
		if action.operator == MOVE:
			(distance, angular, speed, delta_y, rotation) = action.params
			self.publish_feedback("%s:MOVE(%s,%s,%s,%s,%s):START" \
				%(node,distance, angular, speed, delta_y, rotation))
			status,msg = turtlebot.move(distance, angular, speed, delta_y, rotation)
			if status:
				self.publish_feedback("%s:Move(%s,%s,%s,%s,%s):SUCCESS" %(node,distance, angular, speed, delta_y, rotation))
				return True
			else:
				self.publish_feedback("%s:Move(%s,%s,%s,%s,%s): FAILED: %s" %(node,distance, angular, speed, delta_y, rotation, msg))
				return False
				
		elif action.operator == SAY:
			(s,) = action.params
			self.publish_feedback("%s:Say(\"%s\"): START" %(node,s))
			turtlebot.say(s)
			self.publish_feedback("%s:Say(\"%s\"): SUCCESS" %(node,s))
			return True
		elif action.operator == LOCATE:
			(x,y,w) = action.params
			self.publish_feedback("%s:Locate(%s,%s,%s): START" %(node,x,y,w))
			turtlebot.locate(x,y,w)
			self.publish_feedback("%s:Locate(%s,%s,%s): SUCCESS" %(node,x,y,w))
			return True
		elif action.operator == MOVETO:
			(x,y) = action.params
			self.publish_feedback("%s:MoveTo(%s,%s): START" %(node,x,y))
			status, msg = turtlebot.moveTo (x,y)
			if status:
				self.publish_feedback("%s:MoveTo(%s,%s): SUCCESS" %(node,x,y))
				return True
			else:
				self.publish_feedback("%s:MoveTo(%s,%s): FAILED: %s" %(node,x,y, msg))
				return False
		elif action.operator == MOVEABS:
			(x,y,v) = action.params # x,y coordinates on the map and velocity for movement.
			self.publish_feedback("%s:MoveAbs(%s,%s,%s): START" %(node,x,y,v))
			status,msg = turtlebot2.moveAbs(x,y,v)
			if status:
				self.publish_feedback("%s:MoveAbs(%s,%s,%s): SUCCESS" %(node,x,y,v))
				return True
			else:
				self.publish_feedback("%s:MoveAbs(%s,%s, %s): FAILED: %s" %(node,x,y,v,msg))
				return False
		elif action.operator == MOVEREL:
			(x,y,v) = action.params # x,y distance forward on the map and velocity for movement.
			self.publish_feedback("%s:MoveRel(%s,%s,%s): START" %(node,x,y,v))
			status,msg = turtlebot2.moveRel(x,y,v)
			if status:
				self.publish_feedback("%s:MoveRel(%s,%s,%s): SUCCESS" %(node,x,y,v))
				return True
			else:
				self.publish_feedback("%s:MoveRel(%s,%s, %s): FAILED: %s" %(node,x,y,v,msg))
				return False
		elif action.operator == FORWARD:
			(distance, speed) = action.params
			self.publish_feedback("%s:Forward(%s,%s): START" %(node, distance, speed))
			status,msg = tb_no_movebase.forward(distance, speed)
			if status:
				self.publish_feedback("%s:Forward(%s,%s): SUCCESS" %(node, distance, speed))
				return True
			else:
				self.publish_feedback("%s:Forward(%s,%s): FAILED" %(node, distance, speed))
				return False
		elif action.operator == TURNABS:
			(d,r) = action.params # direction and rotational velocity. d = N, S, E, W (North, South, East, West)
			self.publish_feedback("%s:TurnAbs(%s,%s): SUCCESS" %(node,d,r))
			#if self._tf.frameExists("/base_link") and self._tf.frameExists("/map"):
			(status,msg) = tb_no_movebase.turnAbs(d,r)
			if status:
				self.publish_feedback("%s:TurnAbs(%s,%s): SUCCESS" %(node,d,r))
				return True
			else:
				self.publish_feedback("%s:TurnAbs(%s,%s): FAILED: %s" %(node,d,r,msg))
				return False
		elif action.operator == TURNREL:
			(a,r) = action.params # Angle and rotational velocity.
			self.publish_feedback("%s:TurnRel(%s,%s): START" %(node,a,r))
			status, msg = tb_no_movebase.turnDegrees(a, r, True)
			if status:
				self.publish_feedback("%s:TurnRel(%s,%s): SUCCESS" %(node,a,r))
				return True
			else:
				self.publish_feedback("%s:TurnRel(%s,%s): FAILED: %s" %(node,a,r,msg))
				return False
		elif action.operator == CHARGE:
			secs, = action.params
			self.publish_feedback("%s:Charge(%s): START" %(node, secs))
			status,msg = tb_no_movebase.charge(secs)
			if status:
				self.publish_feedback("%s:Charge(%s): SUCCESS" %(node, secs))
				return True
			else:
				self.publish_feedback("%s:Charge(%s): FAILED: %s" %(node, secs, msg))
				return False
		elif action.operator == RECALIBRATE:
			mode, = action.params
			self.publish_feedback("%s:Recalibrate(%s): START" %(node, mode))
			status,msg = turtlebot.recalibrate(mode)
			if status:
				self.publish_feedback("%s:Recalibrate(%s): SUCCESS" %(node, mode))
				return True
			else:
				self.publish_feedback("%s:Recalibrate(%s): FAILED: %s" %(node, mode, msg))
				return False	
		elif action.operator == SETLOCALIZATIONFIDELITY:
			mode, = action.params
			self.publish_feedback("%s:SetLocalizationFidelity(%s): START" %(node, mode))
			(status,msg) = turtlebot.configure_localization(mode)
			if status:
				self.publish_feedback("%s:SetLocalizationFidelity(%s): SUCCESS" %(node, mode))
				return True
			else:
				self.publish_feedback("%s:SetLocalizationFidelity(%s): FAILED: %s" %(node, mode, msg))
				return False
		elif action.operator == MOVEABSH:
			(x,y,v,w) = action.params # x,y coordinates on the map and velocity for movement.
			self.publish_feedback("%s:MoveAbsH(%s,%s,%s,%s): START" %(node,x,y,v,w))
			status,msg = turtlebot2.move(x,y,v,'Absolute',w)
			if status:
				self.publish_feedback("%s:MoveAbsH(%s,%s,%s,%s): SUCCESS" %(node,x,y,v,w))
				return True
			else:
				self.publish_feedback("%s:MoveAbs(%s,%s,%s, %s): FAILED: %s" %(node,x,y,v,w,msg))
				return False
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
		elif cond.operatopr == STOP:
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
			self._success = self.doaction(a,n)
			result = STEP if self._success else FAIL
			return (result, (n2, vs, I, [a] + O))
		elif c.operator == DOUNTIL:
			(a, cnd, n2) = c.params
			b = self.checkcond(cnd)
			self._sucess = self.doaction(a,n)
			result = STEP if self._success else FAIL
			if b:
		  		return (result, (n2, vs, I, [a] + O))
			else:
		  		return (result, (n, vs, I, [a] + O))
		elif c.operator == IFELSE:
			(cnd, n2, n3) = c.params
			b = self.checkcond(cnd)
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
			elif status == FAIL:
			  print "Failed!"
			  self.publish_feedback("Terminating because of failure")
			  break
			else:
			  config = config2
		(_, _, _, O) = config



if __name__ == "__main__":
	rospy.init_node('ig_action_server')
	igserver = IGServer('ig_action_server')
	rospy.spin()




