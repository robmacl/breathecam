import subprocess
from shutil import disk_usage
import time
import logging
from serviceConfig import ServiceConfig
import os
from os.path import exists
import ArducamMux

class ImageService:
    def __init__(self, config):
        self.config = config
        self.log = config.logger
        self.last_grab = 0
        bc = config.parser["breathecam"]
        self.grab_cmd = bc["grab_cmd"]
        self.camera_mux = int(bc["camera_mux"])
        self.mux_channels = [int(x) for x in bc["mux_channels"].split()]
        self.rotation = [int(x) for x in bc["rotation"].split()]

    def checkDiskUsage(self):
        wot = disk_usage(self.config.base_dir())
        return wot.used / wot.total

    def grabMulti(self):
        now = int(time.time())
        channels = self.mux_channels
        for cam in range(len(channels)):
            self.grabOne(now, cam)

    def grabOne(self, now, cam):
        ofile_base = self.config.image_dir() + str(now)
        if self.camera_mux:
            chan = self.mux_channels[cam]
            ofile = ofile_base + "_" + str(cam+1) + ".jpg"
            ArducamMux.select(chan)
        else:
            ofile = ofile_base + ".jpg"

        cmd = self.grab_cmd + " -o " + ofile
        rot = self.rotation[cam]
        if rot != 0:
            cmd += " --rotation " + str(rot)
        
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
            if startTime > (self.last_grab + self.config.interval()):
                usage = self.checkDiskUsage()
                if usage < 0.9 :
                    self.grabMulti()
                    self.last_grab = startTime
                    endTime = time.time()
                    self.log.info("Grab took %.2f seconds", endTime - startTime);
                else:
                    self.log.warning("Disk Usage %d%%, not grabbing new image",
                                     int(usage * 100));
                    time.sleep(60)
            else:
                time.sleep(0.1)

    def run(self):
        self.grabLoop()


if __name__ == '__main__':
    svc = ImageService(ServiceConfig('./', 'image'))
    svc.run()
