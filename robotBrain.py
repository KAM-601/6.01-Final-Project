## 6.01 Final Project
## Team KAM - Kevin Mao, Angel Alvarez, Matt Farejowicz
## This will be the software that will run on the Robot to receive instructions
## and feed them to the robot's motors.
from soar.robot.pioneer import PioneerRobot
import socket

robot = PioneerRobot()

def on_load():
    
    
    pass

def on_start():
    pass

def on_step(step_duration):
    # Receives some instructions from gloveBrain.py
    robot.fv = forward_velocity
    robot.rv = rotational_velocity

def on_stop():
    pass

def on_shutdown():
    pass
