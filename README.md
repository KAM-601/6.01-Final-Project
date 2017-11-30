# 6.01-Final-Project
Our final project consists of a user worn glove that allows for certain hand configurations to send commands to a robot, controlled by a python SOAR interface.

## Overview

For our final project, we would like to implement a control system for the lab robot that consists of a user worn glove that allows for certain hand configurations to send commands to the robot. The overall system would be comprised of a controller glove for the user as well a controller on the robot to receive commands and feed them to the motors. The glove will have two flex sensors which read voltages based on amount of flex, and this information will be fed to the robot to control direction (sensor 1: forward/reverse and sensor 2: right/left) and speed (sensor 1: fv and sensor 2: rv). We believe being able to develop this system will show our ability to incorporate a circuit/control system. We will then work to implement Bayesian reasoning by having the glove control system first gain confidence in a configuration before actually sending the command to the robot. The way this will work is that our command configurations will be predefined for the user, and so as they move their fingers, the system will gain more confidence of the actual correct configuration the user’s hand is in, and once we hit a threshold of confidence, the command is sent to the robot.

## Setup

## Development Notes
