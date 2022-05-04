import subprocess
from shutil import disk_usage
import time
import logging
from serviceConfig import ServiceConfig
import os
from os.path import exists

class ImageService:
    # Command and options for image capture, -o <file> is added below
    grab_cmd = "libcamera-still -n -t 1"

    # Grab image every this many seconds
    interval = 5;

    def __init__(self, config):
        self.config = config
        self.log = config.logger
        self.last_grab = 0

    def checkDiskUsage(self):
        wot = disk_usage(self.config.base_dir())
        return wot.used / wot.total

    def grabOne(self):
        ofile = self.config.image_dir() + str(int(time.time())) + ".jpg"
        cmd = self.grab_cmd + " -o " + ofile
        self.log.info("Running " + cmd)
        result = ofile
        try:
            proc = subprocess.run(cmd.split(), capture_output=True, text=True,
                                  timeout=30)

        except subprocess.TimeoutExpired:
            self.log.error("Timeout while running " + cmd)
            result = ""

        else:
            if not(exists(ofile)) :
                self.log.error("See capture_error.txt, no output from: %s", cmd)
                with open(self.config.log_dir() + 'capture_error.txt', 'a') as f:
                    f.write('\n\n' + proc.stderr)
                result = ""
        
        return result


    def grabLoop(self):
        os.makedirs(self.config.image_dir(), exist_ok=True)
        while True:
            startTime = time.time()
            if startTime > (self.last_grab + self.interval):
                usage = self.checkDiskUsage()
                if usage < 0.9 :
                    ofile = self.grabOne()
                    self.last_grab = startTime
                    endTime = time.time()
                    self.log.info("Grab took %.2f seconds", endTime - startTime);
                else:
                    self.log.warning("Disk Usage %d%%, not grabbing new image",
                                     int(usage * 100));
                    time.sleep(5.0)
            else:
                time.sleep(0.1)

    def run(self):
        self.grabLoop()


if __name__ == '__main__':
    svc = ImageService(ServiceConfig('./', 'image'))
    svc.run()
