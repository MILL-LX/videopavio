#!/bin/sh

echo "recording file: ";

x=`date +%F_%H%M%S`;
# timeout=500000;
# timeout=1800000;
# timeout=30000;
timeout=540000;


echo $x;

rpicam-vid --hflip --timeout=$timeout --width=1920 --height=1080 --nopreview --bitrate=9000k --framerate=24 --low-latency --codec=libav --profile high --level 4.2 --denoise cdn_fast --libav-audio 0 -o /home/pi/videopavio/videos/$x.mp4 && 
rsync -e "ssh -i /home/pi/.ssh/id_rsa" --recursive --update --verbose --progress /home/pi/videopavio/videos/*4 pi@videopavio.local:/media/pi/4BCF-8A8C/videopavio/videos/
