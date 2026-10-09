import os
import sys
import glob
import shutil
import logging

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import eventlet
eventlet.monkey_patch()

import subprocess
import socketio

import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('videopavio')

VIDEOS = config.SERVER_VIDEOS_DIR
MIX = os.path.join(VIDEOS, 'mix.mp4')
MIX_PREV = os.path.join(VIDEOS, 'mix_prev.mp4')
MIX_TMP = os.path.join(VIDEOS, 'mix_tmp.mp4')
MIXED_LOG = os.path.join(VIDEOS, 'mixed.txt')
REJECTED = os.path.join(VIDEOS, 'rejected')
SEED = os.path.join(VIDEOS, config.SEED_VIDEO)

CAM_ARGS = ["--hflip=1", "--width=%d" % config.RECORD_WIDTH, "--height=%d" % config.RECORD_HEIGHT,
            "--fullscreen",
            "--roi", config.ROI_VALUES]

sio = socketio.Server()
app = socketio.WSGIApp(sio)

state = 'idle'            # idle | recording  (o mix corre em segundo plano, não bloqueia)
mixing = False
mix_requested = False
player_stale = False      # mix.mp4 mudou mas o ffplay ainda não foi reiniciado
failures = {}             # nome do clip -> nº de falhas de mix
state_epoch = 0           # invalida watchdogs antigos
cam = None
player = None

unclutter = subprocess.Popen(["unclutter", "-idle", "0"])


# ---------- estado ----------

def set_state(new):
    global state, state_epoch
    state = new
    state_epoch += 1
    log.info('state -> %s', new)
    sio.emit('state', new)
    if new == 'recording':
        eventlet.spawn(recording_watchdog, state_epoch)
    elif player_stale:
        refresh_player()


def emit_backlog():
    """Informa os clientes: se está a misturar e quantos clips faltam."""
    try:
        n = len(pending_files())
    except OSError:
        n = -1
    sio.emit('backlog', {'mixing': mixing, 'pending': n})


def recording_watchdog(epoch):
    eventlet.sleep(config.RECORD_TIMEOUT_S)
    if state == 'recording' and state_epoch == epoch:
        log.warning('recording timeout, back to idle')
        stop_cam()
        set_state('idle')


# ---------- processos ----------

def start_player():
    global player
    stop_player()
    player = subprocess.Popen(["ffplay", "-fs", "-loop", "-1", MIX])


def refresh_player():
    """Reinicia o ffplay com o novo mix.mp4, mas só quando não há gravação no ecrã."""
    global player_stale
    if state == 'recording':
        player_stale = True      # fica para quando a gravação terminar
        return
    player_stale = False
    start_player()


def stop_player():
    global player
    if player and player.poll() is None:
        player.terminate()
        player.wait()
    player = None


def stop_cam():
    global cam
    if cam and cam.poll() is None:
        cam.terminate()
    cam = None


def start_cam(timeout_ms):
    global cam
    stop_cam()
    cam = subprocess.Popen(["rpicam-vid", "-t", str(timeout_ms)] + CAM_ARGS)


# ---------- mix ----------

def pending_files():
    """Gravações (2*.mp4) ainda por misturar, da mais antiga para a mais recente."""
    files = sorted(glob.glob(os.path.join(VIDEOS, '2*.mp4')))
    if not os.path.exists(MIXED_LOG):
        # primeira execução: só a gravação mais recente fica por misturar
        with open(MIXED_LOG, 'w') as f:
            f.write(''.join(os.path.basename(p) + '\n' for p in files[:-1]))
    with open(MIXED_LOG) as f:
        done = set(line.strip() for line in f)
    return [p for p in files if os.path.basename(p) not in done]


def ensure_mix():
    """Garante que mix.mp4 existe, copiando o vídeo de arranque se necessário."""
    if os.path.exists(MIX):
        return True
    if not os.path.exists(SEED):
        log.error('mix.mp4 missing and seed video not found: %s', SEED)
        return False
    log.warning('mix.mp4 missing, seeding from %s', SEED)
    shutil.copyfile(SEED, MIX_TMP)
    os.replace(MIX_TMP, MIX)
    return True


def reject(path):
    os.makedirs(REJECTED, exist_ok=True)
    log.error('rejecting %s after %d failures', path, failures.get(os.path.basename(path), 0))
    shutil.move(path, os.path.join(REJECTED, os.path.basename(path)))
    failures.pop(os.path.basename(path), None)


def mix_one(path):
    """Mistura `path` sobre mix.mp4. Só troca o ficheiro se o ffmpeg terminar bem."""
    if config.MIX_HEIGHT:
        scale = "scale=-2:%d," % config.MIX_HEIGHT
        graph = ("[0:v]%s[bg];[1:v]%scolorkey=%s:%s[ckout];[bg][ckout]overlay[out]"
                 % (scale[:-1], scale, config.KEY_COLOR, config.KEY_PARAMS))
    else:
        graph = ("[1:v]colorkey=%s:%s[ckout];[0:v][ckout]overlay[out]"
                 % (config.KEY_COLOR, config.KEY_PARAMS))
    cmd = ["nice", "-n", str(config.MIX_NICE),
           "ffmpeg", "-y", "-threads", str(config.MIX_THREADS), "-i", MIX, "-i", path,
           "-filter_complex", graph,
           "-map", "[out]", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
           "-threads", str(config.MIX_THREADS),
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-f", "mp4", MIX_TMP]
    log.info('mixing %s', path)
    try:
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                timeout=config.MIX_TIMEOUT_S or None)
    except subprocess.TimeoutExpired:
        log.error('ffmpeg timed out after %ds', config.MIX_TIMEOUT_S)
        return False
    if result.returncode != 0:
        log.error('ffmpeg failed: %s', result.stderr.decode(errors='replace')[-500:])
        return False
    os.replace(MIX, MIX_PREV)
    os.replace(MIX_TMP, MIX)
    with open(MIXED_LOG, 'a') as f:
        f.write(os.path.basename(path) + '\n')
    return True


def request_mix():
    global mix_requested
    mix_requested = True


def mix_worker():
    """Fila de fundo: mistura os clips pendentes um a um, sem bloquear a instalação.

    A instalação continua a passar o último mix.mp4 e a aceitar novas gravações
    enquanto isto corre. Pedidos repetidos fundem-se num só ciclo.
    """
    global mix_requested, mixing
    while True:
        while not mix_requested:
            eventlet.sleep(1)
        mix_requested = False
        mixing = True
        emit_backlog()
        try:
            created = not os.path.exists(MIX)
            changed = False
            retry = False
            if ensure_mix():
                changed = created
                for path in pending_files():
                    if mix_one(path):
                        changed = True
                        emit_backlog()
                        continue
                    name = os.path.basename(path)
                    failures[name] = failures.get(name, 0) + 1
                    if failures[name] >= config.MIX_MAX_ATTEMPTS:
                        reject(path)    # clip estragado não bloqueia os seguintes
                        continue
                    retry = True
                    break
            if changed:
                refresh_player()
            if retry:
                eventlet.spawn_after(60, request_mix)
        except Exception:
            log.exception('mix failed')
        mixing = False
        emit_backlog()


# ---------- eventos ----------

@sio.event
def connect(sid, environ):
    log.info('connect %s', sid)
    sio.emit('state', state, to=sid)
    sio.emit('backlog', {'mixing': mixing, 'pending': len(pending_files())}, to=sid)


@sio.event
def disconnect(sid):
    log.info('disconnect %s', sid)


@sio.event
def messaging(sid, data):
    log.info('message: %s', data)
    sio.emit('internal_messaging', data)


@sio.event
def record(sid, data):
    if state != 'idle':
        log.info('record ignored, state is %s', state)
        return
    log.info('entering recording mode! %s', data)
    set_state('recording')
    sio.emit('record', 'now')
    start_cam(config.RECORD_MS)


@sio.event
def recorded(sid, data):
    """O recorder terminou de gravar: a instalação fica logo livre; o envio e o mix seguem em fundo."""
    log.info('recording finished, installation free')
    if state == 'recording':
        stop_cam()
        set_state('idle')


@sio.event
def record_failed(sid, data):
    log.warning('recorder failed: %s', data)
    if state == 'recording':
        stop_cam()
        set_state('idle')


@sio.event
def start_viewcam(sid, data):
    if state != 'idle':
        return
    log.info('entering viewing mode!')
    sio.emit('messaging', 'now viewing')
    start_cam(0)


@sio.event
def kill_viewcam(sid, data):
    log.info('stopping viewing mode!')
    sio.emit('messaging', 'now killing viewcam view')
    stop_cam()


@sio.event
def mix(sid, data):
    log.info('mix requested')
    request_mix()


if __name__ == '__main__':
    eventlet.spawn(mix_worker)
    request_mix()           # mistura o que ficou pendente de antes do arranque
    if ensure_mix():
        start_player()
    eventlet.wsgi.server(eventlet.listen(('', config.SERVER_PORT)), app)
