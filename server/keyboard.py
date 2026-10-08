import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from curtsies import Input
import socketio

import config

sio = socketio.Client()


@sio.event
def connect():
    print('connection established')


@sio.event
def disconnect():
    print('disconnected from server')


@sio.on('internal_messaging')
def on_messaging(data):
    print('internal message: ', data)


@sio.on('backlog')
def on_backlog(data):
    print('mix backlog: ', data)


@sio.on('state')
def on_state(data):
    print('server state: ', data)


def main():
    sio.connect(config.SERVER_URL)

    with Input(keynames='curses') as input_generator:
        for e in input_generator:
            print(repr(e))
            if (e == 'r'):
                print('sending record message')
                sio.emit('record', 'record')
            elif (e == 'm'):
                print('sending mixing message')
                sio.emit('mix', 'mix')
            elif (e == 'v'):
                print('sending viewcam message')
                sio.emit('start_viewcam', 'start_viewcam')
            elif (e == 's'):
                print('stopping viewcam message')
                sio.emit('kill_viewcam', 'kill_viewcam')


if __name__ == '__main__':
    main()
