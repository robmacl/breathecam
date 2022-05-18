#!/bin/sh

cd /home/breathecam/breathecam/Code/pi_cam

# Kill launcher processes first to make sure they don't respawn the service
# after we kill it.
echo "Killing launchers:"
pkill -f pingServer_launcher.sh
pkill -f remoteDesktop_launcher.sh
pkill -f imageService_launcher.sh
pkill -f udpPinger_launcher.sh
pkill -f uploadToServer_launcher.sh

sleep 1

echo "Killing services:"
pkill -f pingServer.py
#pkill -f ??? remote desktop
pkill -f imageService.py
pkill -f udpPinger.py
pkill -f uploadToServer.py
pkill -f libcamera-still
