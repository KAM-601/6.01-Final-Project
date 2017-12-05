# 6.01-Final-Project
Our final project consists of a user worn glove that allows for certain hand configurations to send commands to a robot, controlled by a python SOAR interface.

## Overview

For our final project, we would like to implement a control system for the lab robot that consists of a user worn glove that allows for certain hand configurations to send commands to the robot. The overall system would be comprised of a controller glove for the user as well a controller on the robot to receive commands and feed them to the motors. The glove will have two flex sensors which read voltages based on amount of flex, and this information will be fed to the robot to control direction (sensor 1: forward/reverse and sensor 2: right/left) and speed (sensor 1: fv and sensor 2: rv). We believe being able to develop this system will show our ability to incorporate a circuit/control system. We will then work to implement Bayesian reasoning by having the glove control system first gain confidence in a configuration before actually sending the command to the robot. The way this will work is that our command configurations will be predefined for the user, and so as they move their fingers, the system will gain more confidence of the actual correct configuration the user’s hand is in, and once we hit a threshold of confidence, the command is sent to the robot.

## Setup

1. Make sure you install the Adafruit_Python_GPIO Library:
    ```
     $ git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
     $ cd Adafruit_Python_GPIO
     $ python3 setup.py install
2. Install the Adafruit Python LSM303 Library:
    * Follow instructions at: https://github.com/adafruit/Adafruit_Python_LSM303


## Development Notes

* We wanted to get working Gyroscope readings. Since the Flex sensors are using SPI, We opted for I2C communication with the sensors.

* We searched the internet for communication libraries written in Python for I2C with this particular device, this lead us to the SMBUS library.

* We found that most of the libraries that we could use were either written in C or were outdated.

* We stumbled upon this piece of code for the L3GD20 sensor:
    * https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/pull/104/files

* We also found that we had to make some modifications to get the library to work properly (Python 2):
   * https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code

* After making the appropriate changes, we were getting gyroscope readings from out External Example 1


## External Code & Sources
Code Snippet for getting the gyroscope readings:
https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/pull/104/files
Adafruit GPIO Library:
https://github.com/adafruit/Adafruit_Python_GPIO
SMBUS Library
https://pypi.python.org/pypi/smbus-cffi/0.5.1
CFFI
https://pypi.python.org/pypi/cffi/
Adafruit python LSM303 Library
https://github.com/adafruit/Adafruit_Python_LSM303