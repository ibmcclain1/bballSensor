#import RPi.GPIO
import argparse
from pythonosc import udp_client
import serial, time
import numpy as np
import tkinter as tk

from tkinter import *
from tkinter import ttk

import time

#import logging
from threading import *


parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="192.168.1.45",
  help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=5005,
  help="The port the OSC server is listening on")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)

ser = serial.Serial("/dev/serial0", 115200,timeout=0) # mini UART serial device

status = "Uninitialized "
message = 'na'

class App(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title('Basketball Sensor')
		self.geometry('680x430')
		self.resizable(0, 0)

		self.create_header_frame()
		self.create_body_frame()
		self.create_footer_frame()

		#threading()

	def create_header_frame(self):
		self.header = ttk.Frame(self)
		#grid setup
		self.header.columnconfigure(0, weight=2)
		self.header.columnconfigure(1, weight=5)
		#self.header.columnconfigure(2, weight=5)

		#label
		self.label = ttk.Label(self.header, text='Status', width = 25)
		self.label.grid(column = 0, row=0)

		#label
		self.label2 = ttk.Label(self.header, text=status, width = 100)
		self.label2.grid(column = 1, row=0)

		#Attach
		self.header.grid(column=0, row=0, padx=10, pady=10)

	def create_body_frame(self):
		self.body = ttk.Frame(self)
		#Grid Setup
		self.body.columnconfigure(0, weight=5)
		self.body.columnconfigure(1, weight=5)

		#Most recent label
		self.label = ttk.Label(self.body, text='Most recent message', width = 34)
		self.label.grid(column = 0, row = 1)

		#Most recent 
		self.label = ttk.Label(self.body, text= message, width = 100)
		self.label.grid(column = 1, row = 1)

		#Attach
		self.body.grid(column=0, row=1, padx=10, pady=10)

	def create_footer_frame(self):
		self.footer = ttk.Frame(self)


		self.footer.grid(column=0, row=2, padx=10, pady=10)

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

#### Main Loop ####

def sensorLoop():
	####  Activate sensor and measure #####
	if ser.isOpen() == False:
	    ser.open() # open serial port if not open
	status = 'Active'
	distance,strength,temperature = read_tfluna_data() # read values
	print('Distance: {0:2.2f} m, Strength: {1:2.0f} / 65535 (16-bit), Chip Temperature: {2:2.1f} C'.\
	              format(distance,strength,temperature)) # print sample data
	
	#ser.close() # close serial port
	status = 'Sensor Running'

	#####    OSC     #######
	
	if(distance > 0.1 and distance < 0.4):
		client.send_message("/goal", 1)
	else :
		client.send_message("/goal", 0)

	app.after(300, sensorLoop())

#def threading():
#	t1=Thread(target=sensorLoop)
#	t1.start()



app = App()
app.after(300, sensorLoop())
app.mainloop()
