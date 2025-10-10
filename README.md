# videopavio
Double Raspberry recording and streaming system.

One raspberry runs a python socket.io server, and the necessary sensors or buttons.

The other(s) raspberry(s) act as recorder(s), running a client socket.io that waits for orders and runs a simple bash script to record and rsync the files back to the server.

The idea is to have a server connected to a screen, showing videoloops and/or it's internal camera feed depending on sensor state.

The recorder(s) wait for socket.io messages and when prompted record and send the files back to the server.

# server role:
cd /lib/systemd/system/

sudo nano videopavio_server.service

[Unit]

Description=Videopavio Server

After=multi-user.target
 
[Service]

Type=simple

ExecStart=/usr/bin/python /home/pi/videopavio/server/server.py

Restart=on-abort
 

[Install]

WantedBy=multi-user.target


cd /lib/systemd/system/

sudo nano videopavio_sensors.service

[Unit]

Description=Videopavio Server Sensors and buttons

After=multi-user.target
 
[Service]

Type=simple

ExecStart=/usr/bin/python /home/pi/videopavio/server/sensors.py

Restart=on-abort
 
[Install]

WantedBy=multi-user.target


# recorder role

cd /lib/systemd/system/

sudo nano videopavio_recorder.service

[Unit]

Description=Videopavio Recorder

After=multi-user.target
 
[Service]

Type=simple

ExecStart=/usr/bin/python /home/pi/videopavio/recorder/recorder_socketio.py

Restart=on-abort
 
[Install]

WantedBy=multi-user.target


# both roles - activate the needed services
sudo chmod 644 /lib/systemd/system/videopavio*

sudo systemctl daemon-reload

sudo systemctl enable videopavio_server.service

sudo systemctl start videopavio_server.service

sudo systemctl enable videopavio_sensors.service

sudo systemctl start videopavio_sensors.service

sudo systemctl enable videopavio_recorder.service

sudo systemctl start videopavio_recorder.service

sudo systemctl status videopavio_recorder.service

# notes and tricks

to show the camera's stream, directly:
rpicam-vid -t 0 --fullscreen --width=1920 --heigh=1080

to record a file with date as filename:
echo "recording file: ";
x=`date +%F_%H%M%S`;
echo $x;
rpicam-vid --timeout=10000 --width=1920 --height=1080 --nopreview --bitrate=15000k --framerate=24 --low-latency --codec=libav -o /home/pi/videopavio/videos/$x.mp4

to rsync every mp4 and h264 in the videos folder:
rsync --recursive --update --verbose /home/pi/videopavio/videos/*4 opencv.local:videopavio/videos/
