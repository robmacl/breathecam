import subprocess
from shutil import disk_usage
import time
import logging
from os.path import exists
from serviceConfig import ServiceConfig

class ImageService:
    # Command and options for image capture, -o <file> is added below
    grab_cmd = "libcamera-still -n -t 1"

    # Grab image every this many seconds
    interval = 5;

    def __init__(self, config):
        self.config = config
        self.last_grab = 0

    def checkDiskUsage(self):
        wot = disk_usage(self.config.baseDir())
        return wot.used / wot.total

    def grabOne(self):
        ofile = self.config.imageDir() + str(int(time.time()*1e3)) + ".jpg"
        cmd = self.grab_cmd + " -o " + ofile
        logging.info("Running " + cmd)
        proc = subprocess.run(cmd.split(), stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
        if exists(ofile):
            return ofile
        else:
            logging.warning("Output file not created: %s", cmd)
            return ""
            
    def grabLoop(self):
        while True:
            startTime = time.time()
            if startTime > (self.last_grab + self.interval):
                usage = self.checkDiskUsage()
                if usage < 0.9 :
                    ofile = self.grabOne()
                    self.last_grab = startTime
                    # movePics(int(startTime))
                    endTime = time.time()
                    logging.info("Grab took %.2f seconds",
                                 endTime - startTime);
                else:
                    logging.warning("Disk Usage %d%%, not grabbing new image",
                                    int(usage * 100));
                    time.sleep(5.0)
            else:
                time.sleep(0.1)

    def run(self):
        while not exists("/run/systemd/timesync/synchronized"):
           logging.info("waiting for time sync")
           time.sleep(5.0)
        self.grabLoop()


if __name__ == '__main__':
    svc = ImageService(ServiceConfig('./', 'image'))
    svc.run()
