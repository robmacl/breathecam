import subprocess
import shutil
import time
import logging
from os.path import exists

class ImageService:
    # Command and options for image capture, -o <file> is added below
    grab_cmd = "libcamera-still -n -t 0"

    # Grab image every this many seconds
    interval = 5;

    def __init__(self, base):
        self.base_dir = base
        # init logging
        # filename='example.log'
        logging.basicConfig(encoding='utf-8', level=logging.DEBUG,
                            format='%(asctime)s: %(message)s')
        self.last_grab = 0

    def logDir(self):
        return self.base_dir + "logs/"

    def imageDir(self):
        return self.base_dir + "images/"
        
    def configDir(self):
        return self.base_dir + "config_files/"

    def checkDiskUsage(self):
        wot = shutil.disk_usage(self.base_dir)
        return wot.used / wot.total

    def grabOne(self):
        ofile = self.imageDir() + str(int(time.time()*1e3)) + ".jpg"
        cmd = grab_cmd + " -o " + ofile
        logging.info("Running " + cmd)
        proc = subprocess.run(cmd)
        if exists(ofile):
            return ofile
        else:
            logging.warning("Failed to create output file")
            return ""
            
    def grabLoop(self):
        while True:
            startTime = time.time()
            if startTime > (last_grab + interval):
                usage = checkDiskUsage()
                logging.info("Disk Usage = "+str(usage)+"%")
                if usage < 0.9 :
                    ofile = self.grabOne()
                    last_grab = startTime
                    # movePics(int(startTime))
                    endTime = time.time()
                    logging.info("Grab took " + str(endTime - startTime) + " seconds")
                else:
                    logging.warning("Disk too full, not grabbing new image")
                    time.sleep(5.0)
            else:
                time.sleep(0.1)

    def run(self):
        while not exists("/run/systemd/timesync/synchronized"):
           logging.info("waiting for time sync")
           time.sleep(5.0)
           grabLoop()
