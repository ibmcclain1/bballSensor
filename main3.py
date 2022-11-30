import argparse
from pythonosc import udp_client
import serial, time
import numpy as np

import time

from tfmini import TFmini



#OSC Setup
parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="192.168.1.45",
  help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=7001,
  help="The port the OSC server is listening on")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)

# create the sensor and give it a port and (optional) operating mode
tf = TFmini('/dev/ttyAMA0', mode=TFmini.STD_MODE)

try:
    print('='*25)
    while True:
        d = tf.read()
        if d:
            print(f'Distance: {d:5}')
        else:
            print('No valid response')
        time.sleep(0.1)

except KeyboardInterrupt:
    tf.close()
    print('bye!!')


