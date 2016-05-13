import socket
import json
from phue import Bridge

from time import sleep

port = 4260
host = ""
currentSide = 0
threshold = .6
b = None # Bridge()
on = False
lights = None
lamp = None
tv = None
normalLight = [0.4596, 0.4105]
fullBrightness = 254
halfBrightness = 145

brightness = 254

def main(args):
    print("MoodCube Beta")

    #Setup bridge
    global b, lights, lamp, tv, brightness
    b = Bridge('192.168.0.102')
    #b.connect()

    lights = list(b.lights)
    lamp = lights[0]
    # tv = lights[1]

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


        #
        if 'ACCEL' in jsond[0][0]:
            x = jsond[0][2]
            y = jsond[0][3]
            z = jsond[0][4]
            determineSide(x, y, z)


        elif 'GYRO' in jsond[0][0]:
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
    global brightness
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
        diff = value / 10
        if lamp.on and 255 > lamp.brightness + diff > 0:
            print("Altering brightness...")
            # print(diff)
            currentbrightness = lamp.brightness
            # print(currentbrightness)
            # brightness =  int(currentbrightness + diff)
            # print(brightness)
            # lamp.brightness = brightness
            lamp.brightness = int(currentbrightness + diff)
            # lamp.brightness = lamp.brightness + diff

            # lamp.brightness += diff


    return 0

def determineSide(x, y, z):
    global currentSide,b,lights,lamp,on

    if x < threshold * -1:
        if currentSide != 4:
            currentSide = 4
            print("Side 4. Red.")

            if not lamp.on:
                lamp.on = True

            lamp.xy = [.6,.3]
            # lamp.brightness = fullBrightness

            if not lamp.effect is "none":
            	lamp.effect = 'none'

    elif x > threshold :
        if currentSide != 3:
            currentSide = 3
            print("side 3. Colorloop.")

            if not lamp.on:
                lamp.on = True

            lamp.effect = 'colorloop'
            # lamp.brightness = fullBrightness


    elif y < threshold * -1:
        if currentSide != 6:
            currentSide = 6
            print("Side 6. Blue.")

            if not lamp.on:
                lamp.on = True

            lamp.xy = [.1, .1]
            # lamp.brightness = fullBrightness

            if not lamp.effect is "none":
            	lamp.effect = 'none'

    elif y > threshold :
        if currentSide != 1:
            currentSide = 1
            print("Side 1. Yellow/Green.")
            for l in lights:
                if not l.on:
                    l.on = True


            for l in lights:
                l.xy = [.4,.55]
                # l.brightness = halfBrightness

            if not lamp.effect is "none":
            	lamp.effect = 'none'


    elif z < threshold * -1:
        if currentSide != 5:
            currentSide = 5
            print("Side 5. Turning all off.")
            if not lamp.effect is "none":
                lamp.effect = 'none'
            for l in lights:
                if l.on:
                    l.on = False


    elif z > threshold :
        if currentSide != 2:
            currentSide = 2
            print("Side 2. Setting Bright light on both.")
            for l in lights:
                if not l.on:
                    l.on = True

            for l in lights:
                l.xy = normalLight
                # l.brightness = fullBrightness

            if not lamp.effect is "none":
            	lamp.effect = 'none'

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

