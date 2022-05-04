#!/bin/sh
# Must run as root

cd /home/breathecam/breathecam/Code/pi_cam

# hack wait for other services to start so that we can run
sleep 60

runuser -c "mkdir -p logs" breathecam

# pingServer_launcher needs to run as root so that it can reboot
./pingServer_launcher.sh &

#./remoteDesktop_launcher.sh &

runuser -c "./imageService_launcher.sh 2>&1 >>logs/imageService.out" breathecam &

#./udpPinger_launcher.sh &

runuser -c "./uploadToServer_launcher.sh 2>&1 >>logs/uploadToServer.out" breathecam & 
