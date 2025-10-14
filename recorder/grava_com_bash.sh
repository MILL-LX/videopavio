#!/bin/sh

echo "recording file: ";

x=`date +%F_%H%M%S`;
timeout=500000;
# timeout=1800000;
# timeout=30000;

echo $x;

rpicam-vid --timeout=$timeout --width=1920 --height=1080 --nopreview --bitrate=11000k --framerate=24 -o /home/pi/videopavio/videos/$x.mp4 && 
rsync -e "ssh -i /home/pi/.ssh/id_rsa" --recursive --update --verbose /home/pi/videopavio/videos/*4 pi@videopavio.local:videopavio/videos/
