import os
import sys
import logging
from signal import pause

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import socketio
from gpiozero import Button, LED

import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('sensor')

sio = socketio.Client(reconnection=True)
button = Button(config.BUTTON_PIN)
led = LED(config.LED_PIN)
led.off()           # só acende quando o servidor diz que está livre
state = 'unknown'


@sio.event
def connect():
    log.info('connection established')


@sio.event
def disconnect():
    log.info('disconnected from server')
    led.off()


@sio.on('state')
def on_state(new_state):
    """LED aceso = pronto para gravar; apagado = a gravar/misturar ou sem servidor."""
    global state
    state = new_state
    log.info('server state: %s', state)
    if state == 'idle':
        led.on()
    else:
        led.off()


def on_button_pressed():
    if state != 'idle':
        log.info('button ignored, server state is %s', state)
        return
    log.info('sensor detected!')
    sio.emit('messaging', 'sensor detected!')
    sio.emit('record', 'now')


button.when_pressed = on_button_pressed

while True:
    try:
        sio.connect(config.SERVER_URL)
        break
    except Exception as e:
        log.warning('server not available (%s), retrying...', e)
        sio.sleep(5)

pause()
