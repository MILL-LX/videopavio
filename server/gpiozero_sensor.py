from time import sleep
from gpiozero import Button
from signal import pause
import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

button = Button(4)

def on_button_pressed():
    if (button.is_pressed):
        print("sensor detected!")
        sio.emit('record', 'now')
        sleep(600) # wait a little more than the video timeout! (500 seconds video, 600 timeout)

@sio.event
def disconnect():
    print('disconnected from server')

sio.connect('http://videopavio.local:5000')

# # Add the event listener
button.when_pressed = on_button_pressed
pause()

sio.wait()
