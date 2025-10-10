import subprocess

import glob
import os

new_env = dict(os.environ)
new_env['DISPLAY'] = ':0.0'

rc_play = subprocess.Popen(["ffplay", "-fs", "-loop", "-1", "/home/pi/videopavio/videos/mix.mp4"])


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
def messaging(sid, data):
    print('message: ', data)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

@sio.event
def record(sid, data):
    print('entering recording mode!', data)
    sio.emit('record', 'now')
    # and we show the live camera stream on the server machine:
    rc = subprocess.Popen(["rpicam-vid", "-t", "30000", "--width=1920", "--height=1080", "--fullscreen", "--roi", "0.20,0.20,0.55,0.55"])

@sio.event
def start_viewcam(sid, data):
    print('entering viewing mode!', data)
    sio.emit('messaging', 'now viewing')
    # and we show the live camera stream on the server machine:
    rc = subprocess.Popen(["rpicam-vid", "-t", "0", "--width=1920", "--height=1080", "--fullscreen", "--roi", "0.20,0.20,0.55,0.55"])

@sio.event
def kill_viewcam(sid, data):
    print('stopping viewing mode!', data)
    sio.emit('messaging', 'now killing viewcam view')
    # and we show the live camera stream on the server machine:
    rc = subprocess.Popen(["killall", "rpicam-vid"])

@sio.event
def mix(sid, data):
    print('starting mixing mode!', data)
    rc_copy = subprocess.Popen(["cp", "/home/pi/videopavio/videos/mix.mp4", "/home/pi/videopavio/videos/mix_temp.mp4"])
    rc_copy.wait()

    list_of_files = glob.glob('/home/pi/videopavio/videos/2*.mp4') # * means all if need specific format then *.csv
    sorted_files = sorted(list_of_files, key=os.path.getmtime)
    latest_file = sorted_files[-1]
    print('latest_file: ')
    print(sorted_files[-1])

    rc_mix = subprocess.Popen(["ffmpeg", "-i", "/home/pi/videopavio/videos/mix_temp.mp4", "-i", latest_file, "-filter_complex", "[1:v]colorkey=0x3BBD1E:0.3:0.2[ckout];[0:v][ckout]overlay[out]", "-map", "[out]", "-c:v", "libx264", "-y", "/home/pi/videopavio/videos/mix_temp_2.mp4"])
    rc_mix.wait()
    rc_kill = subprocess.call(["killall", "ffplay"])
    rc_mv = subprocess.call(["mv", "-f", "/home/pi/videopavio/videos/mix_temp_2.mp4", "/home/pi/videopavio/videos/mix.mp4"])
    rc_play = subprocess.Popen(["ffplay", "-fs", "-loop", "-1", "/home/pi/videopavio/videos/mix.mp4"])

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)


