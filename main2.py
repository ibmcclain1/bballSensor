#import RPi.GPIO
import argparse
from pythonosc import udp_client
import serial, time
import numpy as np

import time

#import logging
from threading import *
import sys
import os

#OSC Setup
parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="192.168.1.45",
  help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=5005,
  help="The port the OSC server is listening on")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)

ser = serial.Serial("/dev/serial0", 115200)


# we define a new function that will get the data from LiDAR and publish it
def read_data():
    while True:
        counter = ser.in_waiting # count the number of bytes of the serial port
        if counter > 8:
            bytes_serial = ser.read(9)
            ser.reset_input_buffer()

            if bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59: # this portion is for python3
                print("Printing python3 portion")            
                distance = bytes_serial[2] + bytes_serial[3]*256 # multiplied by 256, because the binary data is shifted by 8 to the left (equivalent to "<< 8").                                              # Dist_L, could simply be added resulting in 16-bit data of Dist_Total.
                strength = bytes_serial[4] + bytes_serial[5]*256
                temperature = bytes_serial[6] + bytes_serial[7]*256
                temperature = (temperature/8) - 256
                print("Distance:"+ str(distance))
                print("Strength:" + str(strength))
                if temperature != 0:
                    print("Temperature:" + str(temperature))
                ser.reset_input_buffer()

            if bytes_serial[0] == "Y" and bytes_serial[1] == "Y":
                distL = int(bytes_serial[2].encode("hex"), 16)
                distH = int(bytes_serial[3].encode("hex"), 16)
                stL = int(bytes_serial[4].encode("hex"), 16)
                stH = int(bytes_serial[5].encode("hex"), 16)
                distance = distL + distH*256
                strength = stL + stH*256
                tempL = int(bytes_serial[6].encode("hex"), 16)
                tempH = int(bytes_serial[7].encode("hex"), 16)
                temperature = tempL + tempH*256
                temperature = (temperature/8) - 256
                print("Printing python2 portion")
                print("Distance:"+ str(distance) + "\n")
                print("Strength:" + str(strength) + "\n")
                print("Temperature:" + str(temperature) + "\n")
                ser.reset_input_buffer()

            if(distance > 10 and distance < 40):
                client.send_message("/goal", 1)
            else :
                client.send_message("/goal", 0)
        else:
          print('Serial Read Issue, are all wires properly connected? Counter is'+ str(counter))
        print ('overrun delay')
        time.sleep(.01)


if __name__ == "__main__":
    try:
        if ser.isOpen() == False:
            ser.open()
        read_data()
    except:
        pass