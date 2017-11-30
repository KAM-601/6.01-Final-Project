## 6.01 Final Project
## Team KAM - Kevin Mao, Angel Alvarez, Matt Farejowicz
## This will be the software that will run on the Glove Pi to read analog voltages,
## make robot motion decisions, and send to the robot.

## Example analog read below!

import spidev #import SPI library

spi=spidev.SpiDev() #create an SPI device object
spi.open(0,0) #tell it which select pin and SPI channel to use
spi.max_speed_hz = 1953000 #Set SPI CLK frequency...don't change this...will only lead to heartache.

#simple function to read the value of a channel from the MCP3008 (channel is 0 to 7 inclusive as described in diagram above)
#value comes back to you in volts from 0 to 3.3V
def readValue(channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3)<<8)+adc[2]
    return 3.3*data/1023 #scale 10 bit ADC to 0 to 3.3V reading

#need to measure a voltage greater than 3.3V?  Or less than 0V?  Too bad! You'll have to shift it...you can do that using op amps!

#simple use case

import time

while True:
    print("Flex" + str(readValue(0))) #read and print voltage on channel 5 of ADC (pin 6)
    print("GYRO" + str(readValue(1)))
    time.sleep(1)  #relax for 1 second before continuing
