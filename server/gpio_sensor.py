from time import sleep
import RPi.GPIO as GPIO

import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

var=1
counter = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def my_callback(channel):
    if var == 1:
        sleep(1.5)  # confirm the movement by waiting 1.5 sec 
        if GPIO.input(4): # and check again the input
            print("SENSOR ACTIVATED!")
            # captureImage()

            sio.emit('record', 'now')

            # stop detection for x sec
            GPIO.remove_event_detect(4)
            sleep(5) # wait 35 seconds until second detection
            GPIO.add_event_detect(4, GPIO.FALLING, callback=my_callback)

GPIO.add_event_detect(4, GPIO.FALLING, callback=my_callback)


@sio.event
def disconnect():
    print('disconnected from server')

sio.connect('http://videopavio.local:5000')
sio.wait()


# you can continue doing other stuff here
# while True:
#     pass
