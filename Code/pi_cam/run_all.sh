#!/bin/sh
# Must run as root
echo "Running run_all" >/tmp/run_test

cd /home/breathecam/breathecam/Code/pi_cam

# hack wait for other services to start so that we can run
#sleep 60

echo "Running mkdir" >>/tmp/run_test
su -c "mkdir -p logs" breathecam 2>&1 >>/tmp/run_test

echo "Running pingserver" >>/tmp/run_test
# pingServer_launcher needs to run as root so that it can reboot
./pingServer_launcher.sh &


#./remoteDesktop_launcher.sh &

echo "Running imageservice" >>/tmp/run_test
su -c "./imageService_launcher.sh 2>&1 >>logs/imageService.out" breathecam &

#./udpPinger_launcher.sh &

echo "Running upload" >>/tmp/run_test
su -c "./uploadToServer_launcher.sh 2>&1 >>logs/uploadToServer.out" breathecam & 
