#!/bin/sh

# Unlike with the imageService and uploadToServer, we don't restart if the
# process exits, instead we reboot.  This is because pingServer is also a
# watchdog that detects if the other two are not doing their jobs.  Possibly
# rebooting might fix it.
echo `date` ": ping service started, user " `whoami`>>logs/pingServer.out
chown breathecam logs/pingServer.out

su -c "python3 pingServer.py 2>&1 >>logs/pingServer.out" breathecam

echo `date` ": ping service exited (probable watchdog trigger), rebooting, user" `whoami` >>logs/pingServer.out
reboot --force

sleep 15
echo `date` ": OOPS! we didn't reboot, strange...  reboot returned $?" >>logs/pingServer.out
