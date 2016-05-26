import socket
import json
import random
from datetime import datetime

from phue import Bridge
from collections import deque
from time import sleep, time

port = 4260
host = ""
currentSide = 0
lowerThreshold = .6
upperThreshold = 1.2
shakeThreshold = 2
shakeDelay = 1.5
b = None # Bridge()
on = False
lights = None
lamp = None
tv = None
normalLight = [0.4596, 0.4105]
fullBrightness = 254
halfBrightness = 145
brightness = 254
brightnessdelay = .2

lastshaketime = time()
lastbrightnesschange = time()

xs = deque({},5)
ys = deque({},5)
zs = deque({},5)

def main(args):
    print("MoodCube Beta")

    #Setup bridge
    global b, lights, lamp, tv, brightness
    b = Bridge('192.168.0.102')
    #b.connect()

    lights = list(b.lights)
    lamp = lights[0]
    tv = lights[1]

    brightness = lamp.brightness

    #Setup UDP socket to receive data from the EventBus
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print ("Listening on port", port );
    sleep(1)
    count = 0
    print("Receiving data...")
    while True:
        data, addr = s.recvfrom(1024)
        jsond = json.loads(str(data, 'utf-8'))
        # print (jsond[5])

        # print(jsond)
        # print(jsond[0][0])

        now = time()

        #
        if 'ACCEL' in jsond[0][0]:
            x = jsond[0][2]
            y = jsond[0][3]
            z = jsond[0][4]

            # if upperThreshold*-1 > x > upperThreshold or upperThreshold*-1 > y > upperThreshold or upperThreshold*-1 > z > upperThreshold:
            # if  x > upperThreshold or x < upperThreshold * -1 or y > upperThreshold or y < upperThreshold*-1 or  z > upperThreshold or z < upperThreshold*-1:
            if  abs(x) > upperThreshold or abs(y) > upperThreshold or  abs(z) > upperThreshold :

                # print(now - lastshaketime)
                if now-lastshaketime > shakeDelay:
                    detectShake(x, y, z)
                # print("x: %f | y: %f | z: %f" % (x, y, z))
                # print('ds')
                # print(xs)
                # print(ys)
                # print(zs)

            else:
                # print('no ds')
                #Clear shake-deques to ensure shakes must be concurrent
                xs.clear()
                ys.clear()
                zs.clear()
            determineSide(x, y, z)

                # print("x: %f | y: %f | z: %f" % (x, y, z))

        elif 'GYRO' in jsond[0][0]:
            if now - lastbrightnesschange > brightnessdelay:

                x = jsond[0][2]
                y = jsond[0][3]
                z = jsond[0][4]
                determineRotation(x,y,z)

            # print("x: %f | y: %f | z: %f" % (x, y, z))

        # if len(jsond[5]) > 4:

            # x = jsond[5][3]
            # y = jsond[5][4]
            # z = jsond[5][5]
            # print("x: %f | y: %f | z: %f" % (x,y,z))
            # determineSide(x,y,z)
        else :
            print('Inactive')

    return 0

def determineRotation(x,y,z):
    global brightness, lastbrightnesschange
    value = 0

    if currentSide is 2:
        value = z * -1
    elif currentSide is 5:
        value = z
    elif currentSide is 3:
        value = x * -1
    elif currentSide is 4:
        value = x
    elif currentSide is 6:
        value = y
    elif currentSide is 1:
        value = y * -1

    # print(value)
    if value > 25 or value < -25:
        diff = value / 5
        if lamp.on and 255 > lamp.brightness + diff > 0:
            print("Altering brightness...")
            # print(diff)
            currentbrightness = lamp.brightness
            # print(currentbrightness)
            # brightness =  int(currentbrightness + diff)
            # print(brightness)
            # lamp.brightness = brightness
            lamp.brightness = int(currentbrightness + diff)

            lastbrightnesschange = time()
            # lamp.brightness = lamp.brightness + diff

            # lamp.brightness += diff
            # sleep()


    return 0

def determineSide(x, y, z):
    global currentSide,b,lights,lamp,on

    if -1 * upperThreshold < x < lowerThreshold * -1:

        if lamp.on:
            if currentSide != 4:
                currentSide = 4
                print("Side 4. Red.")

                # if not lamp.on:
                #     lamp.on = True

                # lamp.brightness = fullBrightness

                if not lamp.effect is "none":
                    lamp.effect = 'none'

                lamp.xy = [.6,.3]

    elif upperThreshold > x > lowerThreshold :

        if lamp.on:
            if currentSide != 3:
                currentSide = 3
                print("side 3. Colorloop.")

                # if not lamp.on:
                #     lamp.on = True

                lamp.effect = 'colorloop'
            # lamp.brightness = fullBrightness


    elif -1 * upperThreshold <  y < lowerThreshold * -1:
        #     lamp.on = True
        # if not lamp.on:
        if lamp.on:
            if currentSide != 6:
                currentSide = 6

                print("Side 6. Blue.")
                # lamp.brightness = fullBrightness

                if not lamp.effect is "none":
                    lamp.effect = 'none'

                lamp.xy = [.1, .1]

    elif upperThreshold > y > lowerThreshold :

        # for l in lights:
        #     if not l.on:
        #         l.on = True

        if lamp.on:
            if currentSide != 1:
                currentSide = 1
                print("Side 1. Yellow/Green.")

                    # l.brightness = halfBrightness

                if not lamp.effect is "none":
                    lamp.effect = 'none'

                for l in lights:
                    l.xy = [.4, .55]

    elif -1 * upperThreshold <  z < lowerThreshold * -1:

        # print("Side 5. Turning all off.")
        if lamp.on:
            if currentSide != 5:
                currentSide = 5

                print("Side 5. Random color.")
                if not lamp.effect is "none":
                    lamp.effect = 'none'
                # for l in lights:
                #     if l.on:
                #         l.on = False
                lamp.xy = [random.random(), random.random()]


    elif upperThreshold > z > lowerThreshold :
        # for l in lights:
        #     if not l.on:
        #         l.on = True
        if lamp.on:
            if currentSide != 2:
                currentSide = 2
                print("Side 2. Setting Bright light on both.")


                if not lamp.effect is "none":
                    lamp.effect = 'none'

                for l in lights:
                    l.xy = normalLight
                    # l.brightness = fullBrightness

    return 0

def detectShake(x, y, z):
    global xs, ys, zs, lastshaketime

    xs.append(x)
    ys.append(y)
    zs.append(z)

    ThresholdCount = 0
    # yThresholdCount = 0
    # zThresholdCount = 0

    for val in xs:
        if abs(val) > upperThreshold:
            ThresholdCount += 1

    for val in ys:
        if abs(val) > upperThreshold:
            ThresholdCount += 1

    for val in zs:
        if abs(val) > upperThreshold:
            ThresholdCount += 1

    # print(xThresholdCount)

    # if xThresholdCount > shakeThreshold or yThresholdCount > shakeThreshold or zThresholdCount > shakeThreshold:
    if ThresholdCount > shakeThreshold:
        print("Shake detected!")



        lastshaketime = time()
        # print(lastshaketime)
        print(ThresholdCount)
        #Clear deques to avoid more immediate shakes
        xs.clear()
        ys.clear()
        zs.clear()
        # print(xs)
        # print(ys)
        # print(zs)

        for light in lights:
            if light.on:
                light.on = False
            else:
                light.on = True

        # sleep(1.5)

    return 0


class F:
    nl = True
    def write(self, x):
        timestamp = datetime.now().strftime('%a %b %d. @ %H:%M:%S')
        # old_f.write("[%s]:" % str(timestamp) + x)
        if x == '\n':
            old_f.write(x)
            self.nl = True
        elif self.nl:
            old_f.write("[%s] " % str(timestamp) + x)
            self.nl = False
        else:
            old_f.write(x)


if __name__ == '__main__':
    import sys
    old_f = sys.stdout
    sys.stdout = F()
    sys.exit(main(sys.argv))





