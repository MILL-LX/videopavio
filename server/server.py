import subprocess

import glob
import os

new_env = dict(os.environ)
new_env['DISPLAY'] = ':0.0'

unclutter = subprocess.Popen(["unclutter", "-idle", "0"])

rc_play = subprocess.Popen(["ffplay", "-fs", "-loop", "-1", "/media/pi/4BCF-8A8C/videopavio/videos/mix.mp4"])


import eventlet
import socketio

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def messaging(data):
    print('message: ', data)
    sio.emit('internal_messaging', data)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

@sio.event
def record(sid, data):
    print('entering recording mode!', data)
    sio.emit('record', 'now')
    # and we show the live camera stream on the server machine:
    rc = subprocess.Popen(["rpicam-vid", "-t", "540000", "--hflip=1", "--width=1920", "--height=1080", "--fullscreen", "--roi", "0.125,0.125,0.75,0.75"])
    # rc = subprocess.Popen(["rpicam-vid", "-t", "1800000", "--width=1920", "--height=1080", "--fullscreen", "--roi", "0.125,0.125,0.75,0.75"])

@sio.event
def start_viewcam(sid, data):
    print('entering viewing mode!', data)
    sio.emit('messaging', 'now viewing')
    # and we show the live camera stream on the server machine:
    rc = subprocess.Popen(["rpicam-vid", "-t", "0", "--hflip=1", "--width=1920", "--height=1080", "--fullscreen", "--roi", "0.125,0.125,0.75,0.75"])

@sio.event
def kill_viewcam(sid, data):
    print('stopping viewing mode!', data)
    sio.emit('messaging', 'now killing viewcam view')
    # and we show the live camera stream on the server machine:
    rc = subprocess.Popen(["killall", "rpicam-vid"])

@sio.event
def mix(sid, data):
    print('starting mixing mode!', data)

    list_of_files = glob.glob('/media/pi/4BCF-8A8C/videopavio/videos/2*.mp4') # * means all if need specific format then *.csv
    sorted_files = sorted(list_of_files, key=os.path.getmtime)
    latest_file = sorted_files[-1]
    print('latest_file: ')
    print(sorted_files[-1])

    rc_tutti = subprocess.Popen(["cp /media/pi/4BCF-8A8C/videopavio/videos/mix.mp4 /media/pi/4BCF-8A8C/videopavio/videos/mix_temp.mp4 && ffmpeg -i /media/pi/4BCF-8A8C/videopavio/videos/mix_temp.mp4 -i " + latest_file + " -filter_complex '[1:v]colorkey=0x3BBD1E:0.3:0.2[ckout];[0:v][ckout]overlay[out]' -map '[out]' -c:v libx264 -y /media/pi/4BCF-8A8C/videopavio/videos/mix_temp_2.mp4 && killall ffplay && mv -f /media/pi/4BCF-8A8C/videopavio/videos/mix_temp_2.mp4 /media/pi/4BCF-8A8C/videopavio/videos/mix.mp4 && ffplay -fs -loop -1 /media/pi/4BCF-8A8C/videopavio/videos/mix.mp4"], stdout=subprocess.PIPE, shell=True)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)


