
from curtsies import Input

import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

# @sio.event
# def my_message(data):
#     print('message received with ', data)
#     sio.emit('my response', {'response': 'my response'})

@sio.event
def disconnect():
    print('disconnected from server')


def main():
    sio.connect('http://opencv.local:5000')
    with Input(keynames='curses') as input_generator:
        for e in input_generator:
            print(repr(e))
            if (e == 'r'):
                print('sending message to clients')
                sio.emit('record', 'record')
            elif (e == 'm'):
                print('sending mixing message')
                sio.emit('mix', 'mix')                

if __name__ == '__main__':
    main()