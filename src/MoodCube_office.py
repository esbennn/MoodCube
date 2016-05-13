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

def main(args):
    print("MoodCube v0.3")

    #Setup bridge
    global b, lights, lamp, tv
    b = Bridge('192.168.0.102')
    #b.connect()

    lights = list(b.lights)
    lamp = lights[0]
    # tv = lights[1]

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
        if len(jsond[5]) > 4:
            x = jsond[5][3]
            y = jsond[5][4]
            z = jsond[5][5]
            # print("x: %f | y: %f | z: %f" % (x,y,z))
            determineSide(x,y,z)
        else :
            print('Inactive')

    return 0


def determineSide(x, y, z):
    global currentSide,b,lights,lamp,on

    if x < threshold * -1:
        if currentSide != 4:
            currentSide = 4
            # print("Side 4. Kitchen mode, full brightness.")
            print("Side 4. Red.")
            # if not on:
            #     b.set_light(1, 'on', True)
            #     on = True
            # b.set_light(1, {'xy': [.4, .5], 'on': True, 'bri': 220, 'effect': 'none'})
            # b.set_light(1, {'effect': 'none', 'transitiontime': 400})
            # b.set_light(1, {'xy': [.4, .5], 'bri': 220})
            # b.set_light(1, {'xy': [.4, .5], 'bri': 220, 'effect': 'none'})
            # if tv.on:
            #     tv.on = False

            if not lamp.on:
                lamp.on = True

            lamp.xy = [.6,.3]
            lamp.brightness = fullBrightness

            if not lamp.effect is "none":
            	lamp.effect = 'none'

    elif x > threshold :
        if currentSide != 3:
            currentSide = 3
            print("side 3. Colorloop.")
            # print("side 3. Tv mode, bright.")
            # if not on:
            #     b.set_light(1, 'on', True)
            #     on = True
            # b.set_light(1, {'xy': [0.22, 0.15], 'on': True, 'bri': 200, 'effect': 'none'})
            # b.set_light(1, {'xy': [0.22, 0.15], 'bri': 200, 'effect': 'none'})
            # b.set_light(1, {'effect': 'colorloop','on': True})
            # b.set_light(1, {'effect': 'colorloop','on': True})
            # if kitchen.on:
            #     kitchen.on = False

            if not lamp.on:
                lamp.on = True

            # lamp.xy = normalLight
            lamp.effect = 'colorloop'
            lamp.brightness = fullBrightness


    elif y < threshold * -1:
        if currentSide != 6:
            currentSide = 6
            # print("Side 6. Tv mode, less bright.")
            print("Side 6. Blue.")
            # if not on:
            #     b.set_light(1, 'on', True)
            #     on = True
            # b.set_light(1, {'xy': [0.1, 0.12], 'on': True, 'bri': 200, 'effect': 'none'})
            # b.set_light(1, {'effect': 'none', 'transitiontime':kitchen 400})
            # b.set_light(1, {'xy': [0.1, 0.12], 'bri': 200})
            # b.set_light(1, {'xy': [0.1, 0.12], 'bri': 200, 'effect': 'none'})
            # if lamp.on:
            #     kitchen.on = False

            if not lamp.on:
                lamp.on = True

            lamp.xy = [.1, .1]
            lamp.brightness = fullBrightness

            if not lamp.effect is "none":
            	lamp.effect = 'none'

    elif y > threshold :
        if currentSide != 1:
            currentSide = 1
            print("Side 1. Setting slightly less bright light.")
            for l in lights:
                if not l.on:
                    l.on = True


            for l in lights:
                l.xy = normalLight
                l.brightness = halfBrightness

            if not lamp.effect is "none":
            	lamp.effect = 'none'
            # print("Side 4. Only .")
            # if not on:
                # b.set_light(1, {'on': True, 'transitiontime': 400})
                # b.set_light(1, 'on', True)
                # on = True
            # b.set_light(1, {'xy': [.35, .37], 'on': True, 'bri': 120, 'effect': 'none'})
            # b.set_light(1, {'xy': [0.6, 0.12], 'on': True, 'bri': 200, 'effect': 'none'})
            # b.set_light(1, {'effect': 'none', 'transitiontime': 400})
            # b.set_light(1, {'xy': [0.6, 0.12], 'bri': 200})
            # b.set_light(1, {'xy': [0.6, 0.12], 'bri': 200, 'effect': 'none'})

    elif z < threshold * -1:
        if currentSide != 5:
            currentSide = 5
            print("Side 5. Turning all off.")
            # if tv.on:
            #     tv.on = False
            for l in lights:
                if l.on:
                    l.on = False
            # if on:
            #     b.set_light(1, 'on', False)
            #     on = False
            # b.set_light(1, {'on': False, 'effect': 'none'})

            if not lamp.effect is "none":
            	lamp.effect = 'none'

    elif z > threshold :
        if currentSide != 2:
            currentSide = 2
            print("Side 2. Setting Bright light on both.")
            # if not on:
            #     b.set_light(1, 'on', True)
            #     on = True
            # b.set_light(1, {'xy': [.35, .37], 'on': True, 'bri': 254, 'effect': 'none'})
            # b.set_light(1, {'effect': 'none', 'transitiontime': 400})
            # b.set_light(1, {'xy': [0.4596, 0.4105], 'bri': 254})
            # b.set_light(1, {'xy': [.35, .37], 'bri': 254, 'effect': 'none'})
            for l in lights:
                if not l.on:
                    l.on = True

            for l in lights:
                l.xy = normalLight
                l.brightness = fullBrightness

            if not lamp.effect is "none":
            	lamp.effect = 'none'

    return 0

# def test():
#     global b
#     b.get

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

