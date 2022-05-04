#!/bin/sh

echo `date` ": uploadToServer started" >>logs/uploadToServer.out

while :
do
	python3 uploadToServer.py
	echo `date` ": uploadToServer exited, restarting" >>logs/uploadToServer.out
done
