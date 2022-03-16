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



def removePics():
    try:
        fileList = glob.glob("*.JPG")
        fileList = fileList + glob.glob("*.jpg")
        if len(fileList) > 0:
            for f in fileList:
                print " removing: "+f
                os.remove(f)
    except:
        print "error removing file "+f
    pass

def movePics():
    fileToRename = glob.glob("*.JPG")
    fileToRename = fileToRename + glob.glob("*.jpg")
    if len(fileToRename) > 0:
        os.rename(fileToRename[0],"images/"+str(int(time.time()))+".jpg")

def checkDiskUsage():
    df = subprocess.check_output("df", shell=True).split('\n')
    foundUsage = False
    for d in df:
        if not d.find('/dev/root') == -1:
            rootString = d.split(" ")
            print rootString
            for r in rootString:
                if not r.find('%') == -1:
                    return int(r.split('%')[0])
            break
    if not foundUsage:
        return -1
    else:
        return 0

removePics()

print "Tell camera to save to memory"
os.system(saveToMemoryRAM)

while True:
    startTime = time.time()
    os.system(captureImageAndDownload)
    
    movePics()
    
    endTime = time.time()
    print "******************* took "+str(endTime-startTime)+" seconds to take image ****************"
