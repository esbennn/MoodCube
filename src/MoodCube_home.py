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

def main(args):
    print("MoodCube v0.2")

    #Setup bridge
    global b
    b = Bridge('192.168.0.102')
    #b.connect()

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
    global currentSide,b, on

    if x < threshold * -1:
        if currentSide != 5:
            currentSide = 5
            print("Side 5. Yellow light.")
            if not on:
                b.set_light(1, 'on', True)
                on = True
            # b.set_light(1, {'xy': [.4, .5], 'on': True, 'bri': 220, 'effect': 'none'})
            b.set_light(1, {'effect': 'none', 'transitiontime': 400})
            b.set_light(1, {'xy': [.4, .5], 'bri': 220})
            # b.set_light(1, {'xy': [.4, .5], 'bri': 220, 'effect': 'none'})
    elif x > threshold :
        if currentSide != 2:
            currentSide = 2
            print("side 2. Colorloop.")
            if not on:
                b.set_light(1, 'on', True)
                on = True
            # b.set_light(1, {'xy': [0.22, 0.15], 'on': True, 'bri': 200, 'effect': 'none'})
            # b.set_light(1, {'xy': [0.22, 0.15], 'bri': 200, 'effect': 'none'})
            b.set_light(1, {'effect': 'colorloop','on': True})
            # b.set_light(1, {'effect': 'colorloop','on': True})
    elif y < threshold * -1:
        if currentSide != 3:
            currentSide = 3
            print("Side 3. Purple light.")
            if not on:
                b.set_light(1, 'on', True)
                on = True
            # b.set_light(1, {'xy': [0.1, 0.12], 'on': True, 'bri': 200, 'effect': 'none'})
            b.set_light(1, {'effect': 'none', 'transitiontime': 400})
            b.set_light(1, {'xy': [0.1, 0.12], 'bri': 200})
            # b.set_light(1, {'xy': [0.1, 0.12], 'bri': 200, 'effect': 'none'})
    elif y > threshold :
        if currentSide != 4:
            currentSide = 4
            # print("Side 4. Setting slightly less bright light.")
            print("Side 4. Red light.")
            if not on:
                # b.set_light(1, {'on': True, 'transitiontime': 400})
                b.set_light(1, 'on', True)
                on = True
            # b.set_light(1, {'xy': [.35, .37], 'on': True, 'bri': 120, 'effect': 'none'})
            # b.set_light(1, {'xy': [0.6, 0.12], 'on': True, 'bri': 200, 'effect': 'none'})
            b.set_light(1, {'effect': 'none', 'transitiontime': 400})
            b.set_light(1, {'xy': [0.6, 0.12], 'bri': 200})
            # b.set_light(1, {'xy': [0.6, 0.12], 'bri': 200, 'effect': 'none'})

    elif z < threshold * -1:
        if currentSide != 1:
            currentSide = 1
            print("Side 1. Turning off.")
            if on:
                b.set_light(1, 'on', False)
                on = False
            # b.set_light(1, {'on': False, 'effect': 'none'})

    elif z > threshold :
        if currentSide != 6:
            currentSide = 6
            print("Side 6. Setting Bright light.")
            if not on:
                b.set_light(1, 'on', True)
                on = True
            # b.set_light(1, {'xy': [.35, .37], 'on': True, 'bri': 254, 'effect': 'none'})
            b.set_light(1, {'effect': 'none', 'transitiontime': 400})
            b.set_light(1, {'xy': [.35, .37], 'bri': 254})
            # b.set_light(1, {'xy': [.35, .37], 'bri': 254, 'effect': 'none'})
    return 0

def test():
    global b
    b.get

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))


