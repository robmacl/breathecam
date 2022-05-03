#!/bin/sh
cd /home/pi/breathecam/Code/pi_cam

./pingServer_launcher.sh &
#./remoteDesktop_launcher.sh &
./imageService_launcher.sh &
#./udpPinger_launcher.sh &
./uploadToServer_launcher.sh &
