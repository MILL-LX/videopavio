# other notes about ffmpeg/ffplay, rpicam and rsync:
## ffmpeg
### how-to generate a totally black movie - 30s 1920x1080 24fps h264:
`ffmpeg -t 30 -f lavfi -i color=c=black:s=1920x1080:r=24 -crf 23 -an -c:v libx264 -preset fast -movflags +faststart black_1920x1080.mp4`

### how-to generate a totally pink movie - 30s 1920x1080 24fps h264:
`ffmpeg -t 30 -f lavfi -i color=c=pink:s=1920x1080:r=24 -crf 23 -an -c:v libx264 -preset fast -movflags +faststart pink_1920x1080.mp4`

### how-to generate a totally pink movie - 30s 1920x1200 24fps h264:
`ffmpeg -t 30 -f lavfi -i color=c=pink:s=1920x1200:r=24 -crf 23 -an -c:v libx264 -preset fast -movflags +faststart pink_1920x1200.mp4`

### mix overlay chroma etc 1920x1080+1920x1200, scaling the second stream:
`ffmpeg -i pink_1920x1200.mp4 -i webcam_1920x1080.mp4 -filter_complex '[1:v]scale=1920x1200,colorkey=0x3BBD1E:0.3:0.2[ckout];[0:v][ckout]overlay[out]' -map '[out]' -an -c:v libx264 -crf 23 -preset fast  -movflags +faststart mix_c_scale_1920x1200.mp4`

### playing whatever video with ffplay, 'cropped' to fit 1920x1080 fullscreen from an original 1920x1200 original file:
`ffplay -fs -loop -1 -vf 'crop=1920:1080' mix_c_scale_1920x1200_5s.mp4`

### generating a 1920x1080 24fps pattern:
`ffmpeg -f lavfi -i cellauto=p=118:s=192x108:full=0:rule=118:r=240 -vf scale=1920x1080 -r 24 -t 5 -an -c:v libx264 -crf 23 -preset fast -pix_fmt yuv420p -movflags +faststart cel118.mp4`

## rpicam
### to show the camera's stream, directly:
`rpicam-vid -t 0 --fullscreen --width=1920 --heigh=1080`

### to record a file with date as filename:
```
echo "recording file: ";
x=`date +%F_%H%M%S`;
echo $x;
rpicam-vid --timeout=10000 --width=1920 --height=1080 --nopreview --bitrate=15000k --framerate=24 --low-latency --codec=libav -o /home/pi/videopavio/videos/$x.mp4
```
### to view the rpi camera directly as a stream using cvlc:
`rpicam-vid -t 0 --inline -o - | cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8090}' :demux=h264`

## rsync
### to rsync every mp4 and h264 in the videos folder:
`rsync --recursive --update --verbose /home/pi/videopavio/videos/*4 videopavio.local:videopavio/videos/`


## gpio, python, systemd:
### to access the GPIO we have to change our .service files:
adding inside the [Unit] block:  
`DefaultDependencies=false`  
and/or  
`WorkingDirectory=/home/pi/videopavio/`  
inside the [Service] block...




