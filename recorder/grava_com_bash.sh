#!/bin/sh

echo "recording file: ";

x=`date +%F_%H%M%S`;

echo $x;

rpicam-vid --timeout=10000 --width=1920 --height=1080 --nopreview --bitrate=15000k --framerate=24 --low-latency --codec=libav -o /home/pi/videopavio/videos/$x.mp4 && 
rsync -e "ssh -i /home/pi/.ssh/THE_PRIVATE_KEY_NAME" --recursive --update --verbose /home/pi/videopavio/videos/*4 pi@opencv.local:videopavio/videos/
