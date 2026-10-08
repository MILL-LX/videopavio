#!/bin/sh
# Uso: grava_com_bash.sh record <ficheiro.mp4>   - grava (para .part, renomeia no fim)
#      grava_com_bash.sh upload <ficheiro.mp4>   - envia para o servidor com rsync
# Variáveis (definidas por recorder_socketio.py a partir de config.py):
#   RECORD_MS, RECORD_WIDTH, RECORD_HEIGHT, REMOTE (user@host:/pasta/), SSH_KEY
set -e

mode="$1"
final="$2"
[ -n "$mode" ] && [ -n "$final" ] || { echo "uso: $0 record|upload ficheiro.mp4" >&2; exit 2; }

RECORD_MS="${RECORD_MS:-60000}"
RECORD_WIDTH="${RECORD_WIDTH:-1920}"
RECORD_HEIGHT="${RECORD_HEIGHT:-1080}"
REMOTE="${REMOTE:-pi@videopavio.local:/media/pi/4BCF-8A8C/videopavio/videos/}"
SSH_KEY="${SSH_KEY:-/home/pi/.ssh/id_rsa}"

case "$mode" in
  record)
    part="$final.part"
    echo "recording file: $final"
    # grava para .part: um ficheiro incompleto nunca tem extensão .mp4
    rpicam-vid --hflip --timeout="$RECORD_MS" --width="$RECORD_WIDTH" --height="$RECORD_HEIGHT" --nopreview \
        --bitrate=9000k --framerate=24 --low-latency --codec=libav --profile high --level 4.2 \
        --denoise cdn_fast --libav-audio 0 --libav-format mp4 -o "$part"
    mv "$part" "$final"
    ;;
  upload)
    # o rsync usa ficheiro temporário no destino e renomeia no fim
    rsync -e "ssh -i $SSH_KEY" --verbose --progress --remove-source-files "$final" "$REMOTE"
    ;;
  *)
    echo "modo desconhecido: $mode" >&2; exit 2 ;;
esac
