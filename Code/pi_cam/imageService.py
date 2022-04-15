import subprocess
import shutil

class ImageService:
    def __init__(self, base):
        self.base_dir = base

    def logDir(self):
        return self.base_dir + "logs/"

    def imageDir(self):
        return self.base_dir + "images/"
        
    def configDir(self):
        return self.base_dir + "config_files/"

    def checkDiskUsage(self):
        wot = shutil.disk_usage(self.base_dir)
        return wot.used / wot.total

    libcamera-still -n -t 0 --datetime --timelapse 5000
