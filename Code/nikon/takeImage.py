import time
import os
import glob
import sys
import subprocess
import ast
import requests
from datetime import datetime
from time import gmtime, strftime, mktime


HOME_DIR = "/home/pi/nikon/"
LOG_DIR = HOME_DIR+"logs/"
LOG_DIR_OLD = LOG_DIR+"old/"
IMAGE_DIR = HOME_DIR + "images/"
IMAGE_DIR_OLD = "/root/"
CONFIG_DIR = "config_files/"

interval = 5

f = open(HOME_DIR+CONFIG_DIR+'id.txt','r')
id = (f.readline()).strip()
p = '{\'id\': \"'+id+'\"}'
payload = ast.literal_eval(p)
f.close()

s = open(HOME_DIR+CONFIG_DIR+'pingserver.txt','r')
pingurl = s.readline().strip()
s.close()

uuid = "".join("{:02x}".format(ord(c)) for c in id)
pingpayload = "id="+id + "&uuid=" + uuid



def removePics():
    try:
        fileList = glob.glob(IMAGE_DIR_OLD+"*.JPG")
        fileList = fileList + glob.glob(IMAGE_DIR_OLD+"*.jpg")
        if len(fileList) > 0:
            for f in fileList:
                write("removing old image file: "+f)
                os.remove(f)
        else:
            write("no old image files to delete")
    except:
        write("error removing old image file "+f)
        pass

def movePics(newName):
    write("rename & move picture to 'images' folder ("+str(newName)+")")
    fileToRename = glob.glob(IMAGE_DIR_OLD+"*.JPG")
    fileToRename = fileToRename + glob.glob(IMAGE_DIR_OLD+"*.jpg")
    numberOfFilesToRename = len(fileToRename)
    try:
        if numberOfFilesToRename > 0:
            write("renaming file "+fileToRename[0])
            os.rename(fileToRename[0],IMAGE_DIR+str(newName)+".jpg")
        else:
            write("no files to rename...")
            exit()
    except:
        write("error renaming file: "+fileToRename[0])


def write(s):
    currentTime = time.time()
    print str(currentTime)+": "+s
    logFile.flush()



def checkDiskUsage():
    df = subprocess.check_output("df", shell=True).split('\n')
    foundUsage = False
    for d in df:
        if not d.find('/dev/root') == -1:
            rootString = d.split(" ")
            for r in rootString:
                if not r.find('%') == -1:
                    return int(r.split('%')[0])
            break
    if not foundUsage:
        return -1
    else:
        return 0

def checkInternet():
    try:
        print "Sending ping to server"

        r = requests.post(pingurl, data=pingpayload, timeout = 5)
        response2 = str(r.json)
        if (response2.find("200") > 0):
            print "Got a 200 from server, ping successful"
            return 1
    except:
        print "Unexpected error: "+str(sys.exc_info()[0])

    return 0

################# setup logging #################
listOfFilesToMove = glob.glob(LOG_DIR+"download_*.txt")
numberOfFilesToMove = len(listOfFilesToMove)
try:
    for x in range(0,numberOfFilesToMove):
        fileToMove = listOfFilesToMove[x].split(LOG_DIR)[1]
        print "Moving file "+fileToMove
        os.rename(LOG_DIR+fileToMove,LOG_DIR_OLD+fileToMove)
except:
    print "error moving log file"
    pass

log_Path = LOG_DIR+"download_"+str(int(time.time()))+".txt"
logFile = open(log_Path, "a")
console = sys.stdout # This way we can restore the stdout back to the original console when we need it
sys.stdout = logFile
sys.stderr = logFile

###################################################

nousb()

while not checkInternet():
    write("waiting for time sync")
    time.sleep(5.0)

time.sleep(30)

write("Removing old files on computer")
removePics()

while True:
    startTime = time.time()
    if ((int(startTime) % interval) == 0):
        usage = checkDiskUsage()
        write("Disk Usage = "+str(usage)+"%")
        if usage < 90:

            write("Take & download an image")
            write("\r\n"+subprocess.check_output(captureImageAndDownload, shell=True))

            movePics(int(startTime))

            endTime = time.time()
            write("******************* process took "+str(endTime-startTime)+" seconds ****************")
        else:
            write("Disk too full...")
            time.sleep(5.0)
    else:
        time.sleep(0.1)
