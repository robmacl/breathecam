#!/bin/sh

echo `date` ": imageService started" >>logs/imageService.out

while :
do
	python3 imageService.py
	echo `date` ": imageService exited, restarting" >>logs/imageService.out
done
