from test import L3GD20
import time
from math import *

def getAvgDrift(gyro):

    print('getAvgDrift begin')

    gyroXAngle = gyroYAngle = gyroZAngle = 0

    sampleCnt = 500

    for i in range(0, sampleCnt):
        readout = gyro.read()
        gyroXAngle += readout[0]
        gyroYAngle += readout[1]
        gyroZAngle += readout[2]
        time.sleep(0.02)

    print('getAvgDrift end')
        
    return (
        gyroXAngle / sampleCnt,
        gyroYAngle / sampleCnt,
        gyroZAngle / sampleCnt
    )


if __name__ == '__main__':

    gyro = L3GD20()

    avgDrift = getAvgDrift(gyro)

    gyroXAngle = gyroYAngle = gyroZAngle = 0
    loopCnt = 0;
    
    lastTime = time.time() * 1000

    theta = 0.05
    psi = 0.5
    phi = 0.5
    
    while True:

        readout = gyro.read()
        
        currentTime = time.time() * 1000
        timeDiff = currentTime - lastTime
        lastTime = currentTime

        #gyroXAngle += (readout[0] - avgDrift[0]) * gyro.GAIN * (timeDiff / 1000)
        #gyroYAngle += (readout[1] - avgDrift[1]) * gyro.GAIN * (timeDiff / 1000)
        #gyroZAngle += (readout[2] - avgDrift[2]) * gyro.GAIN * (timeDiff / 1000)
        C = -cos(phi)*cos(psi)*sin(theta)-sin(theta)*sin(phi)*sin(psi) 
        if C == 0:
            print("zero error")
            continue
        
        phi += (-sin(phi)/C*(readout[0] - avgDrift[0])-cos(phi)/C*(readout[1] - avgDrift[1])) * gyro.GAIN * (timeDiff / 1000)*pi/180
        theta += (-cos(psi)*sin(theta)/C*(readout[0] - avgDrift[0])+sin(theta)*sin(psi)/C*(readout[1] - avgDrift[1])) * gyro.GAIN * (timeDiff / 1000)*pi/180
        psi += (cos(theta)*sin(phi)/C*(readout[0] - avgDrift[0])+cos(theta)*cos(phi)/C*(readout[1] - avgDrift[1])+(readout[2] - avgDrift[2])) * gyro.GAIN * (timeDiff / 1000)*pi/180
        
        if (loopCnt > 0 and (loopCnt % 25) == 0):
            print('phi: ' + str(phi) + ' theta: ' + str(theta)+ ' psi: ' + str(psi)+' C: '+ str(C))
            loopCnt = 0

        loopCnt += 1

        time.sleep(0.02)
