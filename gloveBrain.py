## 6.01 Final Project
## Team KAM - Kevin Mao, Angel Alvarez, Matt Farejowicz
## This will be the software that will run on the Glove Pi to read analog voltages,
## make robot motion decisions, and send to the robot.

import time
import spidev #import SPI library
import Adafruit_LSM303
import RPi.GPIO as GPIO
from lib601.dist import *

RELAXED_V = 1.55 # The voltage we found when the flex sensor was fully relaxed
FLEXED_V = 2.25  # The voltage we found when the flex sensor was fully flexed
FV_MIN = -.5 # The min velocity we would like for the fv of the robot
FV_MAX = .5 # The max velocity we would like for the robot
MIN_Y = -1000 # The min g reading we found on the accelerometer
MAX_Y = 1000 # The max g reading we found on the accelerometer
RV_MIN = -.5 # The min velocity we would like for the rv of the robot
RV_MAX = .5 # The max velocity we would like for the rv of the robot
num_states = 25 # The number of states we would like in our prob models
CONFIDENCE_THRESHOLD = .95
fv_states = [i for i in range(num_states)]
rv_states = [i for i in range(num_states)]

# Create initial uniform belief for the user's intended fv and rv
fv_belief = uniform_dist(fv_states)
rv_belief = uniform_dist(rv_states)

# Initialize dicts to map states to voltages, and to store obs models in various states
fv_dict = {}
rv_dict = {}
obs_dict = {}

spi=spidev.SpiDev() # Create an SPI device object
spi.open(0,0) # Tell it which select pin and SPI channel to use
spi.max_speed_hz = 1953000 # Set SPI CLK frequency...don't change this...

# Create a LSM303 instance.
lsm303 = Adafruit_LSM303.LSM303()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)


# Function that will create our obs dicts and mapping dicts
def initialize():
    fv_step = (FLEXED_V - RELAXED_V)/num_states
    rv_step = (MAX_Y - MIN_Y)/num_states
    for i in range(num_states):
        fv_dict[i] = round(RELAXED_V+fv_step*(1/2+i), 4)
        rv_dict[i] = int(MIN_Y+rv_step*(1/2+i))
        if abs(i-(num_states-1)/2) >= 10:
            obs_dict[i] = mixture(triangle_dist(i, int(num_states/12), 0, num_states-1), uniform_dist(fv_states), .8)
        else:
            obs_dict[i] = mixture(triangle_dist(i, int(num_states/5), 0, num_states-1), uniform_dist(fv_states), .8)

initialize()

# Method to discretize values into boxes of size "size"
def discretize(value, size, max_bin=float('inf'), value_min = 0):
    return max(min(int((value - value_min)/size), max_bin), 0)

# Method to clip x to be within lo and hi limits, inclusive
def clip(x, lo, hi):
    return max(lo, min(x, hi))

# Function to update belief by Bayesian Reasoning
def update(dist, obs):
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

# Simple function to read the value of a channel from the MCP3008
# (channel is 0 to 7 inclusive as described in diagram above)
# value comes back to you in volts from 0 to 3.3V
def readValue(channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3)<<8)+adc[2]
    return 3.3*data/1023 #scale 10 bit ADC to 0 to 3.3V reading

## Need to measure a voltage greater than 3.3V?  Or less than 0V?
## Too bad! You'll have to shift it...you can do that using op amps!

# Function that takes a value and range and maps that value to a value in
# a different range
def mapping(val, lo, hi, mappedLo, mappedHi):
    if val > hi:
        return mappedHi
    if val < lo:
        return mappedLo # First sees if function needs to clip
    return (val - lo) / (hi - lo) * (mappedHi - mappedLo) + mappedLo #Otherwise return mapping

def moveInstruction(voltage):
    pass

# -----------------------------
# SERVER CODE DO NOT TOUCH
# -----------------------------
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # we don't actually care about connecting to the google DNS, instead we are using the
    s.connect(("8.8.8.8", 80))
    # garbage collector to remove our socket on return
    return s.getsockname()[0]

HOSTNAME = get_ip_address()
PORT = 6010

# create the server socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOSTNAME, PORT))
    s.listen(1)
    print("Now Listening on: " + str(HOSTNAME) + ":" + str(PORT))
    while True:
        connection, addr = s.accept()
        print("Connection to " + str(addr) + " initialized")
        with connection:
            while True:
                data = connection.recv(1024)
                data = data.decode('UTF-8')
                
                ### MAIN LOOP OF THE PROGRAM
                toRobot = loop(data)
                ###

                if data == 'stop':
                    connection.close()
                    break
                if toRobot != None:
                    connection.sendall(toRobot.encode())
        connection.close()
    print("Connection to " + str(addr) + " closed")


# ---------------------------------------------------------
# YOU CAN MODIFY BELOW THIS LINE, MAIN LOOP OF THE PROGRAM
# ---------------------------------------------------------

def loop(robot_data):

    accel, mag = lsm303.read() # Grab the accel and mag data from sensor
    accel_x, accel_y, accel_z = accel # Split accel data into x,y,z
    voltage = readValue(0) # Read voltage on channel 0 of ADC (pin 1)

    print("Voltage after flex sensor:", voltage, "Volts")
    print("Accelerometer Readings in Y: ", accel_y)

    # print("Corresponds to a FV of:", mapping(voltage, RELAXED_V, FLEXED_V, FV_MAX, FV_MIN), "m/s")
    # print("Corresponds to a RV of:", mapping(accel_y, MIN_Y, MAX_Y, RV_MIN, RV_MAX), "r/s")
    fv_belief = update(fv_belief, discretize(voltage, (FLEXED_V-RELAXED_V)/num_states, num_states-1, RELAXED_V))
    fv_max_elt = fv_belief.max_prob_elt()
    print("Most confident fv state is", fv_max_elt, "with a prob of:", fv_belief.prob(fv_max_elt))
    if fv_belief.prob(fv_max_elt) > CONFIDENCE_THRESHOLD:
        #Send mapping(fv_dict[fv_max_elt], RELAXED_V, FLEXED_V, FV_MAX, FV_MIN) to robot?
        GPIO.output(18,GPIO.HIGH)
        fv_belief = uniform_dist(fv_states)

    rv_belief = update(rv_belief, discretize(accel_y, (MAX_Y-MIN_Y)/num_states, num_states-1, MIN_Y))
    rv_max_elt = rv_belief.max_prob_elt()
    print("Most confident rv state is", rv_max_elt, "with a prob of:", rv_belief.prob(rv_max_elt))
    if rv_belief.prob(rv_max_elt) > CONFIDENCE_THRESHOLD:
        #Send mapping(rv_dict[rv_max_elt], MIN_Y, MAX_Y, RV_MIN, RV_MAX) to robot?
        GPIO.output(23,GPIO.HIGH)
        rv_belief = uniform_dist(rv_states)

    print()
    time.sleep(.02)  #relax for .1 second before continuing
    GPIO.output(23,GPIO.LOW)
    GPIO.output(18,GPIO.LOW)

    ## General plan:
    ## Read the flex sensor voltage, read the gyro sensor, develop confidence in
    ## the configuration, and send it to the robotBrain
