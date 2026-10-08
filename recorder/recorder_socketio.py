import os
import sys
import time
import queue
import logging
import threading
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import socketio

import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('recorder')

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'grava_com_bash.sh')

sio = socketio.Client(reconnection=True)
recording = False
uploads = queue.Queue()     # ficheiros gravados à espera de seguir para o servidor


def script_env():
    return dict(os.environ,
                RECORD_MS=str(config.RECORD_MS),
                RECORD_WIDTH=str(config.RECORD_WIDTH),
                RECORD_HEIGHT=str(config.RECORD_HEIGHT),
                REMOTE=config.SSH_USER + '@' + config.SERVER_HOST + ':' + config.SERVER_VIDEOS_DIR + '/',
                SSH_KEY=config.SSH_KEY)


def safe_emit(event, data):
    try:
        sio.emit(event, data)
    except Exception as e:
        log.warning('could not emit %s (%s)', event, e)


def upload_worker():
    """Envia as gravações em fundo, para a câmara ficar livre para a próxima interação."""
    while True:
        final = uploads.get()
        for attempt in range(1, config.UPLOAD_ATTEMPTS + 1):
            rc = subprocess.call(['/bin/sh', SCRIPT, 'upload', final], env=script_env())
            if rc == 0:
                safe_emit('messaging', 'rsync is done!')
                safe_emit('mix', 'mix')
                break
            log.error('upload of %s failed (code %s), attempt %d/%d',
                      final, rc, attempt, config.UPLOAD_ATTEMPTS)
            time.sleep(config.UPLOAD_RETRY_S)
        else:
            log.error('giving up on %s; file kept locally', final)


@sio.event
def connect():
    log.info('connection established')


@sio.event
def disconnect():
    log.info('disconnected from server')


@sio.event
def record(data):
    global recording
    log.info('message received with %s', data)
    if data != 'now' or recording:
        return
    recording = True
    rc = 1
    try:
        safe_emit('messaging', 'we will start the recording!')
        os.makedirs(config.RECORDER_VIDEOS_DIR, exist_ok=True)
        final = os.path.join(config.RECORDER_VIDEOS_DIR, time.strftime('%F_%H%M%S') + '.mp4')
        rc = subprocess.call(['/bin/sh', SCRIPT, 'record', final], env=script_env())
    finally:
        recording = False
    if rc == 0:
        safe_emit('recorded', final)    # o servidor fica livre já; o envio segue em fundo
        uploads.put(final)
    else:
        log.error('recording script failed with code %s', rc)
        safe_emit('record_failed', 'script exit code %s' % rc)


threading.Thread(target=upload_worker, daemon=True).start()

while True:
    try:
        sio.connect(config.SERVER_URL)
        break
    except Exception as e:
        log.warning('server not available (%s), retrying...', e)
        time.sleep(5)

sio.wait()
