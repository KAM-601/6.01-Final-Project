## 6.01 Final Project
## Team KAM - Kevin Mao, Angel Alvarez, Matt Farejowicz
## This will be the software that will run on the Glove Pi to read analog voltages,
## make robot motion decisions, and send to the robot.

import spidev #import SPI library
import Adafruit_LSM303
import time

RELAXED_V = 1.55 # The voltage we found when the flex sensor was fully relaxed
FLEXED_V = 2.25  # The voltage we found when the flex sensor was fully flexed
FV_MAX = .5 # The max velocity we would like for the robot
FV_MIN = -.5 # The min velocity we would like for the robot
MAX_Y = 1000
MIN_Y = -1000
RV_MAX = .5
RV_MIN = -.5

spi=spidev.SpiDev() #create an SPI device object
spi.open(0,0) #tell it which select pin and SPI channel to use
spi.max_speed_hz = 1953000 #Set SPI CLK frequency...don't change this...will only lead to heartache.

# Create a LSM303 instance.
lsm303 = Adafruit_LSM303.LSM303()

## Simple function to read the value of a channel from the MCP3008
## (channel is 0 to 7 inclusive as described in diagram above)
## value comes back to you in volts from 0 to 3.3V
def readValue(channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3)<<8)+adc[2]
    return 3.3*data/1023 #scale 10 bit ADC to 0 to 3.3V reading

## Need to measure a voltage greater than 3.3V?  Or less than 0V?
## Too bad! You'll have to shift it...you can do that using op amps!

## Function that takes a value and range and maps that value to a value in
## a different range
def mapping(val, lo, hi, mappedLo, mappedHi):
    if val > hi:
        return mappedHi
    if val < lo:
        return mappedLo # First sees if function needs to clip
    return (val - lo) / (hi - lo) * (mappedHi - mappedLo) + mappedLo #Otherwise return mapping

def moveInstruction(voltage):
    pass

def confidentConfig():
    pass

while True:
    
    accel, mag = lsm303.read()
    # Grab the X, Y, Z components from the reading and print them out.
    accel_x, accel_y, accel_z = accel
    
    voltage = readValue(0) # Read voltage on channel 0 of ADC (pin 1)
    print("Voltage after flex sensor:", voltage, "Volts")
    print("Corresponds to a FV of:", mapping(voltage, RELAXED_V, FLEXED_V, FV_MAX, FV_MIN), "m/s")
    print("Accelerometer Readings in X: ", accel_x, ", Y: ", accel_y, ", and Z: ", accel_z)
    print("Corresponds to a RV of:", mapping(accel_y, MIN_Y, MAX_Y, RV_MIN, RV_MAX), "r/s")
    print()
    time.sleep(1)  #relax for 1 second before continuing

    ## General plan:
    ## Read the flex sensor voltage, read the gyro sensor, develop confidence in
    ## the configuration, and send it to the robotBrain
