## 6.01 Final Project
## Team KAM - Kevin Mao, Angel Alvarez, Matt Farejowicz
## This will be the software that will run on the Robot to receive instructions
## and feed them to the robot's motors.
from soar.robot.pioneer import PioneerRobot
import socket

HOST =  '18.111.2.126'#input('Please provide a host to connect to: ')
PORT = 6010    # The same port as the server

robot = PioneerRobot()
robot.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

##def loop(data):
##  return None
##
##  while True:
##    data = s.recv(1024)
##    data = data.decode('UTF-8')
##
##    ### RUN THE MAIN LOOP OF THE RECIEVER
##    print(data)
##    sendData = loop(data)
##
##    if sendData != None:
##      s.sendall(sendData.encode('UTF-8'))


def on_load():  
    pass

def on_start():
    robot.s.connect((HOST, PORT))
    robot.s.sendall(b'ready')
  

def on_step(step_duration):
    #somewhere her I have to make sure dat is the latest data
    data = robot.s.recv(4096)
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
    pass

def on_shutdown():
    pass
