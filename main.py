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


parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="192.168.1.45",
  help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=5005,
  help="The port the OSC server is listening on")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)

ser = serial.Serial("/dev/ttyAMA0", 115200,timeout=0) # mini UART serial device

status = "Uninitialized "
message = 'na'

###Rpi display check for startup####
#if os.environ.get('DISPLAY','') == '':
 #   print('no display found. Using :0.0')
  #  os.environ.__setitem__('DISPLAY', ':0.0')

######### GUI ############

def read_tfluna_data():
    while True:
        counter = ser.in_waiting # count the number of bytes of the serial port
        if counter > 8:
            bytes_serial = ser.read(9) # read 9 bytes
            ser.reset_input_buffer() # reset buffer

            if bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59: # check first two bytes
                distance = bytes_serial[2] + bytes_serial[3]*256 # distance in next two bytes
                strength = bytes_serial[4] + bytes_serial[5]*256 # signal strength in next two bytes
                temperature = bytes_serial[6] + bytes_serial[7]*256 # temp in next two bytes
                temperature = (temperature/8.0) - 256.0 # temp scaling and offset
                return distance/100.0,strength,temperature

######### END GUI ############

#### Main Loop ####

def sensorLoop():
	####  Activate sensor and measure #####
	if ser.isOpen() == False:
	    ser.open() # open serial port if not open
	status = 'Active'
	distance,strength,temperature = read_tfluna_data() # read values
	sensorStatus = ('Distance: {0:2.2f} m, Strength: {1:2.0f} / 65535 (16-bit), Chip Temperature: {2:2.1f} C'.\
	              format(distance,strength,temperature)) # print sample data
	
	print(sensorStatus)

	ser.close() # close serial port
	status = 'Sensor Running'

	#####    OSC     #######
	
	if(distance > 0.1 and distance < 0.4):
		client.send_message("/goal", 1)
	else :
		client.send_message("/goal", 0)

	#root.after(15, sensorLoop)

if __name__ == '__main__':
    while True:
    	sensorLoop()
    	time.sleep(0.01)

