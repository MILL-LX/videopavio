#!/bin/sh

echo "recording file: ";

x=`date +%F_%H%M%S`;
# timeout=1800000;
timeout=30000;

echo $x;

rpicam-vid --timeout=$timeout --width=1920 --height=1080 --nopreview --bitrate=15000k --framerate=24 --low-latency --codec=libav -o /home/pi/videopavio/videos/$x.mp4 && 
rsync -e "ssh -i /home/pi/.ssh/id_ed25519" --recursive --update --verbose /home/pi/videopavio/videos/*4 pi@opencv.local:videopavio/videos/
