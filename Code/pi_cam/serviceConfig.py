import logging
import time
import glob
import os
import os.path
from sys import exc_info

class ServiceConfig:
    '''Wraps common code for reading configuration and logger initialization.'''
    def __init__(self, base_dir, logname):
        self._base_dir = os.path.realpath(base_dir) + '/';
        self._log_start(logname)
        self._id = ""
        self._url = ""
        self._read_config()
        logging.info('Log started: ID=%s URL=%s', self._id, self._url);

    def _log_start(self, logname):
        # Save old log files and open a new one. We only move files for
        # our 'logname' to avoid a race condition with other processes where
        # we move their newly opened logs.  If we used threads then there
        # could be just one logger, which would simplify things.
        try:
            os.makedirs(self.logDir(), exist_ok = True)
            old_logdir = self.logDir() + 'old/' 
            os.makedirs(old_logdir, exist_ok = True)

            listOfFilesToMove = glob.glob(self.logDir() + logname + "_*.txt")
            for fileToMove in listOfFilesToMove:
                print("Saving old log "+ fileToMove)
                base = os.path.basename(fileToMove)
                os.rename(self.logDir() + base, old_logdir + base)
        except:
            print("Error moving log file" + str(exc_info()[0]))

        logfile = (self.logDir() + logname + '_' +
                   str(int(time.time())) + ".txt")
        # encoding='utf-8', 
        logging.basicConfig(level=logging.DEBUG,
                            filename=logfile,
                            format='%(asctime)s %(name)s %(levelname)s: %(message)s')

    def _read_config(self):
        f = open(self.configDir() + 'id.txt', 'r')
        self._id = (f.readline()).strip()
        f.close()
        g = open(self.configDir() + 'server.txt', 'r')
        self._url = g.readline().strip()
        g.close()

    def baseDir(self):
        return self._base_dir

    def cameraID(self):
        return self._id

    def serverURL(self):
        return self._url

    def logDir(self):
        return self._base_dir + "logs/"

    def imageDir(self):
        return self._base_dir + "images/"
        
    def configDir(self):
        return self._base_dir + "config_files/"


if __name__ == '__main__':
    conf = ServiceConfig('./', 'test');
