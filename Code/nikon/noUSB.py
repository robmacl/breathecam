import serial
import time
import glob

ser = serial.Serial('/dev/ttyUSB0')

print "turn camera off"
ser.write('C')
time.sleep(0.5)

print "turn usb off"
ser.write('U')
time.sleep(2.0)

print "turn camera back on"
ser.write('c')
time.sleep(3.0)

print "press power button"
ser.write('s')
time.sleep(6.0)

