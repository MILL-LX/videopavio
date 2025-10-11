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
        sio.emit('messaging', 'sending mix message!')
        sio.emit('mix', 'mix')


@sio.event
def disconnect():
    print('disconnected from server')

sio.connect('http://videopavio.local:5000')
sio.wait()
