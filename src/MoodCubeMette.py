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
dinner = None
sofa = None
window = None

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
    print("MoodCube Beta Mette")

    #Setup bridge
    global b, lights, sofa, dinner, window
    b = Bridge('192.168.0.11')
    #b.connect()

    lights = list(b.lights)
    dinner = lights[0]
    sofa = lights[1]
    window = lights[2]

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

        now = time()

        #
        if 'ACCEL' in jsond[0][0]:
            x = jsond[0][2]
            y = jsond[0][3]
            z = jsond[0][4]

            if  abs(x) > upperThreshold or abs(y) > upperThreshold or  abs(z) > upperThreshold :

                if now-lastshaketime > shakeDelay:
                    detectShake(x, y, z)

            else:
                #Clear shake-deques to ensure shakes must be concurrent
                xs.clear()
                ys.clear()
                zs.clear()
            determineSide(x, y, z)


        elif 'GYRO' in jsond[0][0]:
            if now - lastbrightnesschange > brightnessdelay:

                x = jsond[0][2]
                y = jsond[0][3]
                z = jsond[0][4]
                determineRotation(x,y,z)

            # print("x: %f | y: %f | z: %f" % (x, y, z))
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
        for l in lights:
            if l.on and 255 > l.brightness + diff > 0:
                print("Altering brightness...")
                currentbrightness = l.brightness
                l.brightness = int(currentbrightness + diff)

                lastbrightnesschange = time()


    return 0

def determineSide(x, y, z):
    global currentSide,b,lights,dinner,sofa,window,on

    if -1 * upperThreshold < x < lowerThreshold * -1:


        if currentSide != 4:
            currentSide = 4
            print("Side 4. Sofa og window. Normalt lys.")

            sideFour()


    elif upperThreshold > x > lowerThreshold :

        if currentSide != 3:
            currentSide = 3
            print("Side 3. Alle lamper. Normalt lys.")

            sideThree()

    elif -1 * upperThreshold <  y < lowerThreshold * -1:
        if currentSide != 6:
            currentSide = 6
            print("Side 6. Sofa og window. Random.")

            sideSix()

    elif upperThreshold > y > lowerThreshold :

        if currentSide != 1:
            currentSide = 1
            print("Side 1. Alle. Random.")

            sideOne()

    elif -1 * upperThreshold <  z < lowerThreshold * -1:

        if currentSide != 5:
            currentSide = 5
            print("Side 5. Sofa and window. Colorloop.")

            sideFive()

    elif upperThreshold > z > lowerThreshold :
        if currentSide != 2:
            currentSide = 2
            print("Side 2. All. Colorloop.")

            sideTwo()


    return 0

def sideOne():
    global on, sofa, window, dinner
    if on:
        r = [random.random(), random.random()]
        for l in lights:
            if not l.on:
                l.on = True
            if not l.effect is "none":
                l.effect = "none"

            l.xy = r

    return 0

def sideSix():
    global on, sofa, window, dinner
    if on:
        r = [random.random(), random.random()]
        if not sofa.on:
            sofa.on = True
        sofa.effect = 'colorloop'
        if not sofa.effect is "none":
            sofa.effect = "none"
        sofa.xy = r
        if not window.on:
            window.on = True
        window.effect = 'colorloop'
        if not window.effect is "none":
            window.effect = "none"
        window.xy = r
        if dinner.on:
            dinner.on = False

    return 0

def sideTwo():
    global on, sofa, window, dinner
    if on:
        for l in lights:
            if not l.on :
                l.on = True
            l.effect = 'none'
            l.xy = normalLight
            l.effect = 'colorloop'

    return 0

def sideFive():
    global on, sofa, window, dinner
    if on:
        r = [random.random(), random.random()]
        if not sofa.on:
            sofa.on = True
        sofa.effect = 'none'
        sofa.xy = normalLight
        sofa.effect = 'colorloop'
        if not window.on:
            window.on = True
        window.effect = 'none'
        window.xy = normalLight
        window.effect = 'colorloop'
        if dinner.on:
            dinner.on = False

    return 0

def sideThree():
    global on, sofa, window, dinner
    if on:
        for l in lights:
            if not l.on:
                l.on = True
            l.effect = "none"

            l.xy = normalLight

    return 0

def sideFour():
    global on, sofa, window, dinner
    if on:
        if not sofa.on:
            sofa.on = True
        if not sofa.effect is "none":
            sofa.effect = "none"
        sofa.xy = normalLight
        if not window.on:
            window.on = True
        if not window.effect is "none":
            window.effect = "none"
        window.xy = normalLight

        if dinner.on:
            dinner.on = False
    return 0

def detectShake(x, y, z):
    global xs, ys, zs, lastshaketime, on

    xs.append(x)
    ys.append(y)
    zs.append(z)

    ThresholdCount = 0

    for val in xs:
        if abs(val) > upperThreshold:
            ThresholdCount += 1

    for val in ys:
        if abs(val) > upperThreshold:
            ThresholdCount += 1

    for val in zs:
        if abs(val) > upperThreshold:
            ThresholdCount += 1

    if ThresholdCount > shakeThreshold:

        lastshaketime = time()
        # print(ThresholdCount)

        #Clear deques to avoid more immediate shakes
        xs.clear()
        ys.clear()
        zs.clear()

        if on:
            on = False
            for l in lights:
                l.on = False
        else:
            on = True

        print("Shake detected! On: %s" % (on))

        if currentSide is 1:
            sideOne()
        elif currentSide is 2:
            sideTwo()
        elif currentSide is 3:
            sideThree()
        elif currentSide is 4:
            sideFour()
        elif currentSide is 5:
            sideFive()
        else:
            sideSix()


    return 0

class F:
    nl = True
    def write(self, x):
        file = open('log.txt', 'a')
        timestamp = datetime.now().strftime('%a %b %d. @ %H:%M:%S')
        if x == '\n':
            old_f.write(x)
            file.write(x)
            self.nl = True
        elif self.nl:
            old_f.write("[%s] " % str(timestamp) + x)
            file.write("[%s] " % str(timestamp) + x)
            self.nl = False
        else:
            old_f.write(x)
            file.write(x)
        file.close()

if __name__ == '__main__':
    import sys
    old_f = sys.stdout
    sys.stdout = F()
    sys.exit(main(sys.argv))

