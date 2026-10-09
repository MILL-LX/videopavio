"""Configuração partilhada por server, sensor, keyboard e recorder.

Todos os valores podem ser sobrepostos por variáveis de ambiente VIDEOPAVIO_*.
"""
import os


def _env(name, default):
    return os.environ.get('VIDEOPAVIO_' + name, default)


SERVER_HOST = _env('SERVER_HOST', 'videopavio.local')
SERVER_PORT = int(_env('SERVER_PORT', '5000'))
SERVER_URL = 'http://%s:%d' % (SERVER_HOST, SERVER_PORT)

# Pasta de vídeos no servidor (pen USB) e na(s) câmara(s) remota(s)
SERVER_VIDEOS_DIR = _env('SERVER_VIDEOS_DIR', '/media/pi/4BCF-8A8C/videopavio/videos')
RECORDER_VIDEOS_DIR = _env('RECORDER_VIDEOS_DIR', '/home/pi/videopavio/videos')
SSH_KEY = _env('SSH_KEY', '/home/pi/.ssh/id_rsa')
SSH_USER = _env('SSH_USER', 'pi')

# Duração da gravação (ms) - usada pelo recorder e pela pré-visualização no servidor
# TESTE PROVISÓRIO: 60 s. Valor de produção: 1200000 (20 min)
# RECORD_MS = int(_env('RECORD_MS', '60000')) # 60 segundos
RECORD_MS = int(_env('RECORD_MS', '1200000')) # 20 minutos yoyiy±!!
# Resolução da gravação (recorder) e da pré-visualização (servidor). Para aliviar os Pis: 1280x720
RECORD_WIDTH = int(_env('RECORD_WIDTH', '1280'))
RECORD_HEIGHT = int(_env('RECORD_HEIGHT', '720'))
# Se o servidor ficar em "recording" mais do que isto sem receber 'recorded', volta a "idle"
RECORD_TIMEOUT_S = int(_env('RECORD_TIMEOUT_S', str(RECORD_MS // 1000 + 300)))
# Recorder: tentativas e pausa (s) no envio por rsync
UPLOAD_ATTEMPTS = int(_env('UPLOAD_ATTEMPTS', '5'))
UPLOAD_RETRY_S = int(_env('UPLOAD_RETRY_S', '30'))

# Mix: tempo máximo do ffmpeg (0 desativa) e nº de falhas antes de rejeitar um clip
MIX_TIMEOUT_S = int(_env('MIX_TIMEOUT_S', '0'))   # 0 = sem limite (o mix cresce a cada camada)
MIX_MAX_ATTEMPTS = int(_env('MIX_MAX_ATTEMPTS', '3'))
# O mix corre em segundo plano com pouca prioridade, para não prejudicar a reprodução/gravação
MIX_NICE = int(_env('MIX_NICE', '19'))
MIX_THREADS = int(_env('MIX_THREADS', '2'))
# Altura (px) do vídeo misturado; 0 mantém a resolução original. 720 é bem mais leve que 1080
MIX_HEIGHT = int(_env('MIX_HEIGHT', '0'))
# Vídeo usado para criar mix.mp4 quando este não existe
SEED_VIDEO = _env('SEED_VIDEO', 'white_videos/white_20m_1280x720.mp4')

# Chroma key
KEY_COLOR = _env('KEY_COLOR', '0x3BBD1E')
KEY_PARAMS = _env('KEY_PARAMS', '0.3:0.2')

# Zooom / ROI
ROI_VALUES = _env('ROI_VALUES', '0,0,1,1')

# GPIO (sensor)
BUTTON_PIN = int(_env('BUTTON_PIN', '4'))
LED_PIN = int(_env('LED_PIN', '23'))
