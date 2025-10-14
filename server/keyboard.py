from curtsies import Input
import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

@sio.event
def disconnect():
    print('disconnected from server')

def main():
    sio.connect('http://videopavio.local:5000')

    @sio.on('internal_messaging')
    def on_messaging(sid, data):
        print('internal message: ', sid, data)

    with Input(keynames='curses') as input_generator:
        for e in input_generator:
            print(repr(e))
            if (e == 'r'):
                print('sending message to clients')
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
