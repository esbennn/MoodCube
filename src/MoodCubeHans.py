import socket
import json
import random
from phue import Bridge
from collections import deque
from time import sleep, time

port = 4260
host = ""
currentSide = 0
lowerThreshold = .8
upperThreshold = 1.2
shakeThreshold = 2
shakeDelay = 1.5
b = None # Bridge()

on = True
lights = None
dinner = None
sofa = None
window = None

light_names = None

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
    print("MoodCube Beta Hans")

    #Setup bridge
    global b, lights, sofa, dinner, window, light_names
    b = Bridge('192.168.0.165')
    #b.connect()

    lights = list(b.lights)
    dinner = lights[0]
    sofa = lights[1]
    window = lights[2]

    light_names = b.get_light_objects('name')

    # tv = lights[1]

    # for l in lights:
    #     l.on = False
        # l.on = True

    # brightness = lamp.brightness

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
            print("Side 4. Same random on all")

            sideFour()


    elif upperThreshold > x > lowerThreshold :

        if currentSide != 3:
            currentSide = 3
            print("Side 3. Different randoms on all.")

            sideThree()


    elif -1 * upperThreshold <  y < lowerThreshold * -1:
        if currentSide != 6:
            currentSide = 6
            print("Side 6. Tv.")

            sideSix()

    elif upperThreshold > y > lowerThreshold :

        if currentSide != 1:
            currentSide = 1
            print("Side 1. Relax.")

            sideOne()

    elif -1 * upperThreshold <  z < lowerThreshold * -1:

        if currentSide != 5:
            currentSide = 5
            print("Side 5. Blue by couch.")

            sideFive()


    elif upperThreshold > z > lowerThreshold :
        if currentSide != 2:
            currentSide = 2
            print("Side 2. Wake up time.")

            sideTwo()


    return 0

def sideOne():
    global on, sofa, window, dinner
    if on:
        for light in ['Pixar', 'Stander', 'Loft']:
            # print(light_names[light].name)
            if not light_names[light].on:
                light_names[light].on = True
            light_names[light].effect = 'none'
            light_names[light].xy = [.6030, .5280]
            light_names[light].brightness = 254

        light_names['Hvid'].on = True
        light_names['Hvid'].brightness = 203

    return 0

def sideSix():
    global on, sofa, window, dinner
    if on:
        for light in ['Pixar', 'Loft']:
            # print(light_names[light].name)
            # if not light_names[light].on:
            light_names[light].on = True
            light_names[light].effect = 'none'
            # light_names[light].xy = [.6030, .5280]
            # light_names[light].brightness = 254

        light_names['Pixar'].xy = [.9550, .7240]
        light_names['Loft'].xy = [.6030, .5280]
        light_names['Pixar'].brightness = 30
        light_names['Loft'].brightness = 40

        for light in ['Stander', 'Hvid']:
            light_names[light].on = False

    return 0

def sideTwo():
    global on, sofa, window, dinner
    if on:
        # r = [random.random(), random.random()]
        for l in lights:
            if not l.on :
                l.on = True
            l.brightness = 254
            l.xy = [0,.5080]
            l.effect = 'none'
            # # sleep(.1)
            # l.xy = normalLight
            # # sleep(.1)
            # l.effect = 'colorloop'

    return 0

def sideFive():
    global on, sofa, window, dinner
    if on:

        for light in ['Pixar', 'Loft']:
            if not light_names[light].on:
                light_names[light].on = True
            light_names[light].effect = 'none'
            light_names[light].xy = [.6030, .5280]
            light_names[light].brightness = 254

        light_names['Hvid'].on = True
        light_names['Hvid'].brightness = 203

        light_names['Stander'].on = True
        light_names['Stander'].xy = [.1410, 0]
        light_names['Stander'].brightness = 254

    return 0

def sideThree():
    global on, sofa, window, dinner
    if on:
        for light in ['Pixar', 'Stander', 'Loft']:
            r = [random.random(), random.random()]
            if not light_names[light].on:
                light_names[light].on = True
            light_names[light].effect = 'none'
            light_names[light].xy = r
            light_names[light].brightness = 254

        light_names['Hvid'].on = False

    return 0

def sideFour():
    global on, sofa, window, dinner
    if on:
        r = [random.random(), random.random()]
        for light in ['Pixar', 'Stander', 'Loft']:
            if not light_names[light].on:
                light_names[light].on = True
            light_names[light].effect = 'none'
            light_names[light].xy = r
            light_names[light].brightness = 254

        light_names['Hvid'].on = False

    return 0





def detectShake(x, y, z):
    global xs, ys, zs, lastshaketime, on

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

        if on:
            on = False
            for l in lights:
                l.on = False
        else:
            on = True

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

        # for light in lights:
        #     if light.on:
        #         light.on = False
        #     else:
        #         light.on = True

        # sleep(1.5)

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

