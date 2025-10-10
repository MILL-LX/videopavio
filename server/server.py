import subprocess

import eventlet
import socketio

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

@sio.event
def connect(sid, environ):
    print('connect ', sid)

# @sio.event
# def my_message(sid, data):
#     print('message ', data)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

@sio.event
def record(sid, data):
    print('entering recording mode!', data)
    sio.emit('record', 'now')
    rc = subprocess.Popen(["rpicam-vid", "-t", "15000", "--width=1920", "--height=1080", "--fullscreen"])

@sio.event
def mix(sid, data):
    print('starting mixing mode!', data)
    rc = subprocess.call(["cp", "/home/pi/videopavio/videos/mix.mp4", "/home/pi/videopavio/videos/mix_temp.mp4"])
    rc = subprocess.Popen(["ffmpeg", "-i", "/home/pi/videopavio/videos/mix_temp.mp4", "-i", "/home/pi/videopavio/videos/2025-10-09_191912.mp4", "-filter_complex", "[1:v]colorkey=0x3BBD1E:0.3:0.2[ckout];[0:v][ckout]overlay[out]", "-map", "[out]", "-c:v", "libx264", "-y", "/home/pi/videopavio/videos/mix_temp_2.mp4"])
    rc = subprocess.call(["mv", "/home/pi/videopavio/videos/mix_temp_2.mp4", "/home/pi/videopavio/videos/mix.mp4"])

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)


