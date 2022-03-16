#!/bin/sh

i=0

while  [ $i -lt 5 ]
do
	echo "Starting up python script: $i"
	sudo python /home/pi/nikon/takeImage.py
	echo "Python script ended: $i"
	i=`expr $i + 1`
	sleep 30
done

echo "Too many failures… restart"
sudo reboot
