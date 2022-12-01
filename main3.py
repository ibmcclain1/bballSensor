import argparse
from pythonosc import udp_client
import serial, time
import numpy as np

import time

import tfmplus as tfmP   # Import the `tfmplus` module v0.1.0
from tfmplus import *    # and command and paramter defintions

serialPort = "/dev/serial0"  # Raspberry Pi normal serial port
serialRate = 115200          # TFMini-Plus default baud rate

#OSC Setup
parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="192.168.1.45",
  help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=7001,
  help="The port the OSC server is listening on")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)

# create the sensor and give it a port and (optional) operating mode

# - - - Set and Test serial communication - - - -
print( "Serial port: ", end= '')
if( tfmP.begin( serialPort, serialRate)):
    print( "ready.")
else:
    print( "not ready")
    sys.exit()   #  quit the program if serial not ready

# - - Perform a system reset - - - - - - - -
print( "Soft reset: ", end= '')
if( tfmP.sendCommand( SOFT_RESET, 0)):
    print( "passed.")
else:
    tfmP.printReply()
# - - - - - - - - - - - - - - - - - - - - - - - -
time.sleep(0.5)  # allow 500ms for reset to complete

# - - Get and Display the firmware version - - - - - - -
print( "Firmware version: ", end= '')
if( tfmP.sendCommand( GET_FIRMWARE_VERSION, 0)):
    print( str( tfmP.version[ 0]) + '.', end= '') # print three numbers
    print( str( tfmP.version[ 1]) + '.', end= '') # separated by a dot
    print( str( tfmP.version[ 2]))
else:
    tfmP.printReply()
# - - - - - - - - - - - - - - - - - - - - - - - -

# - - Set the data-frame rate to 20Hz - - - - - - - -
print( "Data-Frame rate: ", end= '')
if( tfmP.sendCommand( SET_FRAME_RATE, FRAME_20)):
    print( str(FRAME_20) + 'Hz')
else:
    tfmP.printReply()
# - - - - - - - - - - - - - - - - - - - - - - - -
time.sleep(0.5)     # Wait half a second.

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - -  the main program loop begins here  - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
try:
    while True:
        time.sleep(0.05)   # Loop delay 50ms to match the 20Hz data frame rate
        # Use the 'getData' function to get data from device
        if( tfmP.getData()):
            print( f" Dist: {tfmP.dist:{3}}cm ", end= '')   # display distance,
            print( " | ", end= '')
            print( f"Flux: {tfmP.flux:{4}d} ",   end= '')   # display signal strength/quality,
            print( " | ", end= '')
            print( f"Temp: {tfmP.temp:{2}}°C",  )   # display temperature,

            if(dist > 10 and dist < 40):
                client.send_message("/goal", 1)
            else :
                client.send_message("/goal", 0)
        else:                  # If the command fails...
          tfmP.printFrame()    # display the error and HEX data
#
except KeyboardInterrupt:
    print( 'Keyboard Interrupt')
#    
except: # catch all other exceptions
    eType = sys.exc_info()[0]  # return exception type
    print( eType)
#
finally:
    print( "That's all folks!")
    sys.exit()                   # clean up the OS and exit
#
# - - - - - -  the main program sequence ends here  - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -