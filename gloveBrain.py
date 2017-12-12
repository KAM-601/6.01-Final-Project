## 6.01 Final Project
## Team KAM - Kevin Mao, Angel Alvarez, Matt Farejowicz
## This will be the software that will run on the Glove Pi to read analog voltages,
## make robot motion decisions, and send to the robot.

import time
import spidev # SPI library
import Adafruit_LSM303 # Library used to read from 9-DOF IMU (Accelerometer)
import RPi.GPIO as GPIO # Library to operate LED's
from lib601.dist import * # Library to handle probabilistic reasoning
import socket
import http.client

#-----------------------------------
# CHANGE FOR DIFFERENT EXTERNAL HOST
#-----------------------------------
COMMON_SERVER = "next205.mit.edu"



RELAXED_V = 1.65 # The voltage we found when the flex sensor was fully relaxed
FLEXED_V = 2.3  # The voltage we found when the flex sensor was fully flexed
FV_MIN = -.75 # The min velocity we would like for the fv of the robot
FV_MAX = .75 # The max velocity we would like for the robot
MIN_Y = -1000 # The min g reading we found on the accelerometer
MAX_Y = 1000 # The max g reading we found on the accelerometer
RV_MIN = -1 # The min velocity we would like for the rv of the robot
RV_MAX = 1 # The max velocity we would like for the rv of the robot
num_states = 7 # The number of states we would like in our prob models
CONFIDENCE_THRESHOLD = .95 # The threshold we consider good enough to be confident in a configuration

# Create initial uniform belief for the user's intended fv and rv
fv_states = [i for i in range(num_states)]
rv_states = [i for i in range(num_states)]
fv_belief = uniform_dist(fv_states)
rv_belief = uniform_dist(rv_states)

#create traj for recording the reversing actions, lastv to store the last command,
#and reversing to indicate whether it is doing the reverse motion
traj = []
lastv = (0,0)
reversing = False

# Initialize dicts to map states to voltages, and to store obs models in various states
fv_dict = {}
rv_dict = {}
obs_dict = {}

spi=spidev.SpiDev() # Create an SPI device object
spi.open(0,0) # Tell it which select pin and SPI channel to use
spi.max_speed_hz = 1953000 # Set SPI CLK frequency...don't change this...

# Create a LSM303 instance.
lsm303 = Adafruit_LSM303.LSM303()

# Initialize LED pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)

def initialize():
    ''' Function that will create our obs dicts and mapping dicts '''
    fv_step = (FLEXED_V - RELAXED_V)/num_states
    rv_step = (MAX_Y - MIN_Y)/num_states
    for i in range(num_states):
        fv_dict[i] = round(RELAXED_V+fv_step*(1/2+i), 4)
        rv_dict[i] = int(MIN_Y+rv_step*(1/2+i))
        obs_dict[i] = mixture(delta_dist(i), uniform_dist(fv_states), .8)

initialize()

def discretize(value, size, max_bin=float('inf'), value_min = 0):
    ''' Discretize values into boxes of size "size" '''
    return max(min(int((value - value_min)/size), max_bin), 0)

def update(dist, obs):
    ''' Update belief by Bayesian Reasoning. '''
    dist_after_obs = {}
    belief_dict = {}
    new_tot = 0
    for el in dist.support():
        belief_dict[el] = dist.prob(el)
        new_tot += belief_dict[el] * obs_dict[obs].prob(el)

    for el in dist.support():
        new_prob = belief_dict[el] * obs_dict[obs].prob(el) / new_tot
        dist_after_obs[el] = new_prob

    return DDist(dist_after_obs)

def readValue(channel):
    '''Simple function to read the value of a channel from the MCP3008
    (channel is 0 to 7 inclusive as described in diagram above)
    value comes back to you in volts from 0 to 3.3V'''
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3)<<8)+adc[2]
    return 3.3*data/1023 #scale 10 bit ADC to 0 to 3.3V reading

def mapping(val, lo, hi, mappedLo, mappedHi):
    ''' Function that takes a value and range and maps that value to a value in a different range '''
    if val > hi:
        return mappedHi
    if val < lo:
        return mappedLo # First sees if function needs to clip
    return (val - lo) / (hi - lo) * (mappedHi - mappedLo) + mappedLo #Otherwise return mapping

# ------------------------
# MAIN LOOP OF THE PROGRAM
# ------------------------

def loop(robot_data):
    ''' Function that is called by the network code. 
        Will be called synchronously as long as the robot is connected.
        
        PARAMS: robot_data - data sent back by the robot, currently, we don't actually get this data,
        because it would stall the server.

        RETURNS: a String to be sent to the robot OR None
    '''


    global fv_belief, rv_belief,traj,reversing,lastv

    accel, mag = lsm303.read() # Grab the accel and mag data from sensor
    accel_x, accel_y, accel_z = accel # Split accel data into x,y,z
    voltage0 = readValue(0) # Read voltage on channel 0 of ADC (pin 1)
    voltage1 = readValue(1)  # Read voltage on channel 0 of ADC (pin 1)
    record_threshold = 1.75 # Threshold in volts to begin recording
    recording = (voltage1>record_threshold)

    if ((not recording) and (not reversing) and (len(traj)>0)):
        print("relaxed")
        time.sleep(1)
        reversing = True
    if reversing:
        if len(traj) == 0:
            reversing = False
        else:
            print("reversing")
            (lastfv,lastrv) = traj.pop()
            lastfv = -lastfv if (lastfv is not None) else None
            lastrv = -lastrv if (lastrv is not None) else None
            time.sleep(.05)
            if (lastfv is None and lastrv is None):
                return None
            else:
                return "lastfv: " + str(lastfv) + " " + "lastrv: " + str(lastrv)

    if not reversing:

        #print("Voltage after flex sensor:", voltage0, "Volts")
        #print("Accelerometer Readings in Y: ", accel_y)

        fv = lastv[0]   # last known readings of fv
        rv = lastv[1]   # last known readings of rv

        # print("Corresponds to a FV of:", mapping(voltage0, RELAXED_V, FLEXED_V, FV_MAX, FV_MIN), "m/s")
        # print("Corresponds to a RV of:", mapping(accel_y, MIN_Y, MAX_Y, RV_MIN, RV_MAX), "r/s")
        
        fv_belief = update(fv_belief, discretize(voltage0, (FLEXED_V-RELAXED_V)/num_states, num_states-1, RELAXED_V))
        fv_max_elt = fv_belief.max_prob_elt()
        
        #print("Most confident fv state is", fv_max_elt, "with a prob of:", fv_belief.prob(fv_max_elt))
        
        if fv_belief.prob(fv_max_elt) > CONFIDENCE_THRESHOLD:
            fv_belief = uniform_dist(fv_states)
            fv = mapping(fv_dict[fv_max_elt], RELAXED_V, FLEXED_V, FV_MAX, FV_MIN)
            
        rv_belief = update(rv_belief, discretize(accel_y, (MAX_Y-MIN_Y)/num_states, num_states-1, MIN_Y))
        rv_max_elt = rv_belief.max_prob_elt()
        
        #print("Most confident rv state is", rv_max_elt, "with a prob of:", rv_belief.prob(rv_max_elt))
        
        if rv_belief.prob(rv_max_elt) > CONFIDENCE_THRESHOLD:
            rv_belief = uniform_dist(rv_states)
            rv = mapping(rv_dict[rv_max_elt], MIN_Y, MAX_Y, RV_MIN, RV_MAX)
            
        time.sleep(.05)
        GPIO.output(18,GPIO.LOW)

        if (fv, rv) == lastv:        # if we haven't updated fv or rv, then send no data
            (fv,rv) = (None,None)

        if recording:
            print("traj appending")
            traj.append((fv,rv))

        if (fv is None and rv is None):  
            return None
        else:
            lastv = (fv,rv)
            GPIO.output(18,GPIO.HIGH)
            return "fv: " + str(fv) + " " + "rv: " + str(rv)

# ------------------------
# SERVER CODE DO NOT TOUCH
# ------------------------

def get_ip_address():
    ''' Get the outward facing IP address '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # we don't actually care about connecting to the google DNS, instead we are pulling off the IP from the socket name
    s.connect(("8.8.8.8", 80))
    
    # exploit garbage collector to remove our socket on return
    return s.getsockname()[0]

def send_ip_address(External_Host, Current_IP):
    ''' Sends IP to the common external host. '''

    h1 = http.client.HTTPConnection(External_Host)
    h1.request('POST', '/glove?newIP="' + Current_IP + '"')
    res = h1.getresponse()

    response_status = res.status
    response_recieved = res.read().decode('UTF-8')
    if (response_status == 200 and response_recieved == 'success'):
        return
    else:
        raise Exception('Failed to update the common point')

def beginConnection(sock):
    ''' create a connection with a listening socket. This is considered the main loop of the program. '''

    connection, addr = sock.accept()
    print("Connection to " + str(addr) + " initialized")
    with connection:
        while True:
            toRobot = loop('')
            print(toRobot)

            if toRobot is not None:
                connection.sendall(toRobot.encode())
    connection.close()

HOSTNAME = ""
PORT = 6010

def ServeLoop():
    ''' Performs error handling of network code '''
    # Wait until we are on the network, and successfully shared IP with common point

    while True:
        try:
            HOSTNAME = get_ip_address()
            print("Hostname detected: " + HOSTNAME)
            send_ip_address(COMMON_SERVER, HOSTNAME)
            print("Common point updated")
            break
        except Exception as e:
            print('Failed to connect to the network, starting again in 1 second:')
            print(str(e))
            time.sleep(1)
            pass

    # create the server socket

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOSTNAME, PORT))
            s.listen(1)
            GPIO.output(23,GPIO.HIGH)
            print("Now Listening on: " + str(HOSTNAME) + ":" + str(PORT))
            while True:
                beginConnection(s)
                print("Connection to " + str(addr) + " closed")
    except Exception as e:
        print('Error with socket connection, Waiting for a new connection')
        print(str(e))
    return True

# This is the secret loop that is actually doing everything

serve = True

while serve:
    serve = ServeLoop()
    time.sleep(3)
