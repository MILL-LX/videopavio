from time import sleep
from gpiozero import Button, LED
from signal import pause


import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

button = Button(4)
led = LED(23)
led.on()


def on_button_pressed():
    if (button.is_pressed):
        print("sensor detected!")
        sio.emit('messaging', 'sensor detected!')
        sio.emit('record', 'now')
        led.off()
        # sleep(150) # wait 5 minutes
        sleep(3600) # 9min recording + 10min transfer + 20min mixing... one hour!
        led.on()



@sio.event
def disconnect():
    print('disconnected from server')

sio.connect('http://videopavio.local:5000')


# # Add the event listener
button.when_pressed = on_button_pressed
pause()

sio.wait()


# you can continue doing other stuff here
# while True:
#     button.when_pressed = on_button_pressed
#     pause()
#     pass
