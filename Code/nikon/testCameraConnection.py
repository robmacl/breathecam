import serial
import time
import glob
import os

import subprocess

gphoto2 = "gphoto2 --auto-detect"
saveToMemorySD   = gphoto2+" --set-config capturetarget=1"
saveToMemoryRAM  = gphoto2+" --set-config capturetarget=0"
listFiles = gphoto2 + " --list-files"
folderprefix = " --folder='"
folderend = "\'"
captureImageAndDownload = gphoto2+" --capture-image-and-download"





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

print "turn usb back on"
ser.write('u')

time.sleep(2.0)

print "Tell camera to save to memory"
os.system(saveToMemoryRAM)
