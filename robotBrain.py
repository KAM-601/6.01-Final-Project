## 6.01 Final Project
## Team KAM - Kevin Mao, Angel Alvarez, Matt Farejowicz
## This will be the software that will run on the Robot to receive instructions
## and feed them to the robot's motors.
from soar.robot.pioneer import PioneerRobot
import socket
import http.client

robot = PioneerRobot()
robot.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def on_load():  
    pass

def on_start():
    # --------------------------------
    # GET IP ADDRESS FROM COMMON POINT
    # --------------------------------
    h1 = http.client.HTTPConnection('next205.mit.edu')
    h1.request('GET', '/glove')
    res = h1.getresponse()
    HOST = res.read().decode('UTF-8').strip('"')

    PORT = 6010    # The same port as the server
    
    robot.s.connect((HOST, PORT))
    robot.s.sendall(b'ready')
  
def on_step(step_duration):
    #somewhere her I have to make sure dat is the latest data
    data = robot.s.recv(4096)
    if not data: on_stop()
    print(len(data))

    data = data.decode('UTF-8')
    data = data.split(' ')
    print(data)
    if len(data) != 4:
        print("invalid: early return.")
        return
    
    # Receives some instructions from gloveBrain.py
    if data[1] != 'None':
        robot.fv = float(data[1])
        print(robot.fv)
    if data[3] != 'None':
        robot.rv = float(data[3])
        print(robot.rv)
def on_stop():
    print("starting stop sequence")
    robot.fv = 0
    robot.rv = 0
    robot.s.close()

def on_shutdown():
    robot.fv = 0
    robot.rv = 0
    
