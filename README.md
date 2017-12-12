# 6.01-Final-Project
Our final project consists of a user worn glove that allows for certain hand configurations to send commands to a robot, controlled by a python SOAR interface.

## Overview

For our final project, we would like to implement a control system for the lab robot that consists of a user worn glove that allows for certain hand configurations to send commands to the robot. The overall system would be comprised of a controller glove for the user as well a controller on the robot to receive commands and feed them to the motors. The glove will have two flex sensors which read voltages based on amount of flex, and this information will be fed to the robot to control direction (sensor 1: forward/reverse and sensor 2: right/left) and speed (sensor 1: fv and sensor 2: rv). We believe being able to develop this system will show our ability to incorporate a circuit/control system. We will then work to implement Bayesian reasoning by having the glove control system first gain confidence in a configuration before actually sending the command to the robot. The way this will work is that our command configurations will be predefined for the user, and so as they move their fingers, the system will gain more confidence of the actual correct configuration the user’s hand is in, and once we hit a threshold of confidence, the command is sent to the robot.

## Requirements
Make sure to have the following materials for running the project.
  
  * KAM-601 Control Gauntlet. This device was implemented as a final project for MIT 6.01 for FALL 2017.
  * Robot from the MIT 6.01 Lab (Pioneer3DX).
  * Latest version of `soar`: This is used to control the robot itself.
  * Computer to control the robot, which will be running soar.
  * External web server: used to establish a connection between the robot and glove.
  
## Dependencies

Our code requires the following libraries to work: 

  * Python 3: We've used python 3.6.3 for this project. any versions of libraries you install should be for this version of python.

  * spidev: allows us to use SPI to connect to an ADC which converts the analog flex sensor output to a digital output we read as a voltage level.
    * follow the instructions outlined on the MIT 6.01 website: https://sixohone.mit.edu/fall17/PROJECT/spi_on_pi 

  * Adafruit_Python_GPIO Library: This is used to communicate with the glove.
    * run the following commands: 
        ``` 
         $ git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
         $ cd Adafruit_Python_GPIO
         $ python3 setup.py install
        ```
  * Adafruit Python LSM303 Library: This dependency is used to retrieve accelerometer data from the glove.
    * Follow instructions at: https://github.com/adafruit/Adafruit_Python_LSM303
  
  * lib601.dist: This dependency is used to create a probability model of the glove state.
    * Follow the installation instructions on the MIT 6.01 website: https://sixohone.mit.edu/fall17/python/install
    
## Setup

1. Install the dependencies outlined in the section above on the glove computer.

2. Make sure to have cloned this repository on the computer running SOAR and the glove controller itself.

3. The glove controller should already wait for the network on startup, but if it doesn't, you will want to add this line to `/etc/rc.local` and restart the Pi:
   * `python3 /PATH_TO_REPOSITORY/gloveBrain.py`
   
4. make sure that the glove and robot have internet access.  

5. Turning on the glove controller should cause the pi to emit light. After about 30 seconds, the green LED on the bread board should turn on. This indicates that the network is connected and that the glove is waiting for a robot to connect to it.

6. There is an external http server that is running via node.js. this is required to let the two computers connect to one another. the robot figures out the IP of the glove because the glove sends it's IP to this common server (`next205.mit.edu`). If you would like to run this code elsewhere (since i will have destroyed the server at some point), I've included a very simple web server that has routes which implement the code in the `web\` folder. If this common point no longer exists, you will then have to run this server on a different host.
    * change the `COMMON_SERVER` variable in `robotBrain.py` and `gloveBrain.py` to whatever your external server host is.
    * On the external server, run the following sequence of commands (make sure that you have `nodejs` and `npm` installed): 
     ```
     $ git clone git@github.com:KAM-601/6.01-Final-Project.git
     $ cd web
     $ npm install
     $ npm start
     ```
    * This creates the common endpoint needed to connect the glove headlessly to the robot.

7. You should be ready to run the glove headlessly, restart the glove.

8. Once the green light turns on, the glove should be all set. Connect your robot to a computer running soar.

9. load the `robotBrain.py` into soar, connect the robot and play the script. You will notice that your hand is now controlling the motion of the robot.

#### NOTE: A current bug in the software prevents you from stopping the robot in SOAR. to kill the robot, you should first bring the robot to a halt, then either kill power to the glove, kill power to the robot, or kill the soar process. This bug is due to a problem with recv() function on the client causing the thread to wait for data. a multithreaded implementation of the robot controller might prevent this problem, but as of now we have not implemented any fixes.

## Usage
 * The index finger controls the foward velocity. Extending it out will cause the robot to move forward. Retracting the index finger will cause the robot to move backwards. 
 * The middle finger controls recording. you can start recording a gesture, which is a sequence of commands by retracting the middle finger. while you have it retract, the glove will record your gestures over time. as you extend your middle finger, the robot will play those motions back to you.
 * The tilt of your hand controls the rotational velocity of the robot.


## Development Notes

* We wanted to get working Gyroscope readings. Since the Flex sensors are using SPI, We opted for I2C communication with the sensors.

* We searched the internet for communication libraries written in Python for I2C with this particular device, this lead us to the SMBUS library.

* We found that most of the libraries that we could use were either written in C or were outdated.

* We stumbled upon this piece of code for the L3GD20 sensor:
    * https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/pull/104/files

* We also found that we had to make some modifications to get the library to work properly (Python 2):
   * https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code

* After making the appropriate changes, we were getting gyroscope readings from out External Example 1

* Unfortunately, we can't reliably integrate angular position of the hand. So we are using the accelerometer to give us tilt. A possible improvement of the system would be using the accelerometer for long term angular position, and to use the gyroscope for short term changes in angle.

* We've had an issue with running the glove headlessly. In order to get the IP of the glove, we have to see the IP in the terminal. furthermore, we want to run the script on startup, and if the network does not exist yet, it would be hard to connect to anything.
  * To combat the first problem, we've added some backend code to a server that Angel is running elsewhere ('next205.mit.edu'). A handshake happens between the robot and glove to ensure this connection occurs.
  * To combat the second problem, we've added error handling on the server side that constantly tries to connect to the external server. it waits a second until it establishs a connection. This also has the added benefit of ensuring that the server is always available, and that the glove doesn't stop working even if an error occurs in the communication of the robot and the glove.

* The sockets are blocking the continual execution of the `on_step` loop as well as soar itself. Python has very limited multithreading support, and I'm not sure how to implement communication between the socket thread and the soar thread. I will leave this as a future issue for the project.


## External Code & Sources
* Code Snippet for getting the gyroscope readings:
https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/pull/104/files
* Adafruit GPIO Library:
https://github.com/adafruit/Adafruit_Python_GPIO
* SMBUS Library:
https://pypi.python.org/pypi/smbus-cffi/0.5.1
* CFFI:
https://pypi.python.org/pypi/cffi/
* Adafruit python LSM303 Library:
https://github.com/adafruit/Adafruit_Python_LSM303
* Detect outward IP address in python:
https://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-of-eth0-in-python
