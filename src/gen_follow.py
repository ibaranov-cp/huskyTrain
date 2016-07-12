#!/usr/bin/env python

import roslib
import rospy
import pickle
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
from sensor_msgs.msg import Joy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from ddynamic_reconfigure_python.ddynamic_reconfigure import DDynamicReconfigure

mode_flag = 0
pose_array = []

def mode(data):
    global mode_flag
    global pose_array
    if data.buttons[5] == 1:
        #rospy.loginfo("Recording!")
        mode_flag = 1
    elif data.buttons[4] == 1:
        #pose_array = pickle.load(open("poses.p","rb"))
        #rospy.loginfo("Playback!")
        mode_flag = 2
        print pose_array
    else:
        #if mode_flag == 1: pickle.dump(pose_array,open( "poses.p", "wb" ))
        mode_flag = 0

def dyn_rec_callback(config, level):
    rospy.loginfo("Received reconf call: " + str(config))
    return config

# Nasty rate limit hack
rate = 0

def monitor(data):
    global pose_array
    global rate
    if mode_flag ==1:
        rate = rate + 1
    if rate >= 80:
        rate = 0
        pose_array.append(data)

def looper():
    rospy.init_node('gen_follow', anonymous=True)

    # Create a D(ynamic)DynamicReconfigure
    ddynrec = DDynamicReconfigure("example_dyn_rec")

    # Variables for tracking
    ddynrec.add_variable("pos_tolerance", "float/double variable", 1.0, 0.01, 10.0)
    ddynrec.add_variable("ang_tolerance", "float/double variable", 1.0, 0.01, 6.28)
    ddynrec.add_variable("track_speed", "float/double variable", 0.5, 0.05, 1.0)

    # Start DDynamic reconfigure server
    ddynrec.start(dyn_rec_callback)

    #Listen to the controller and robot_localization data
    rospy.Subscriber("/joy_teleop/joy", Joy, mode)
    rospy.Subscriber("/odometry/filtered", Odometry, monitor)

    #Main Loop
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        rate.sleep()

if __name__ == '__main__':
    looper()
