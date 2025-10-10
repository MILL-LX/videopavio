import subprocess

import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

@sio.event
def record(data):
    print('message received with ', data)
    if (data == 'now'):
        sio.emit('messaging', 'we will start the recording!')
        rc = subprocess.call('/home/pi/videopavio/recorder/grava_com_bash.sh')
        sio.emit('messaging', 'rsync is done!')

@sio.event
def disconnect():
    print('disconnected from server')

sio.connect('http://opencv.local:5000')
sio.wait()
