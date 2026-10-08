# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Videopavio: a multi-Raspberry Pi (Trixie) recording and mixing installation. There is no build system, package manifest, linter or test suite. The scripts are deployed to Pis as systemd services and can only be exercised on that hardware (`rpicam-vid`, GPIO, `ffplay`, an X display). Don't try to run them on the dev Mac. Dependencies are apt packages (`python3-socketio`, `python3-eventlet`, plus `gpiozero`, `curtsies`, `unclutter`, `ffmpeg`, `libcamera-apps`), not pip. Setup and deploy steps are in [README.md](README.md); ffmpeg/rpicam/rsync snippets are in [extras/notes_and_tricks.md](extras/notes_and_tricks.md).

## Architecture

Two roles communicate over Socket.IO on `config.SERVER_URL` (default `http://videopavio.local:5000`). All paths, ports, durations, GPIO pins and chroma-key values live in [config.py](config.py) and can be overridden with `VIDEOPAVIO_*` env vars. Every script adds the repo root to `sys.path` to import it.

- **Server Pi** ([server/server.py](server/server.py)) is an eventlet Socket.IO server. The installation `state` is only `idle` / `recording`, broadcast as the `state` event. Mixing is a background queue that never blocks it, and its progress is broadcast as `backlog` (`{mixing, pending}`). It handles:
  - `record`: ignored unless `idle`. Sets `recording`, broadcasts `record`/`now` and shows the local camera for `RECORD_MS`. A watchdog returns to `idle` after `RECORD_TIMEOUT_S` if neither `recorded` nor `record_failed` arrives.
  - `recorded`: sent by the recorder as soon as capture ends (before upload). Stops the camera and sets `idle`, so a new interaction can start while upload and mix continue.
  - `record_failed`: sent on script failure; resets to `idle`.
  - `mix`: sent by the recorder after a successful upload; only sets a flag. A single `mix_worker` greenlet serializes mixing (`nice`d, `MIX_THREADS` threads, optional `MIX_HEIGHT` downscale), so requests coalesce. It overlays every unmixed `2*.mp4` (tracked in `mixed.txt`) onto `mix.mp4` via `mix_tmp.mp4`. `mix.mp4` is replaced only if ffmpeg succeeds, the previous one is kept as `mix_prev.mp4`. `ffplay` restarts through `refresh_player()`, which defers while the camera is on screen. ffmpeg is capped by `MIX_TIMEOUT_S`; a failing clip is retried after 60 s, and after `MIX_MAX_ATTEMPTS` failures it is moved to `videos/rejected/`. If `mix.mp4` is missing it is seeded from `SEED_VIDEO` (default `white_videos/white_5_minutes.mp4` under the videos dir). A mix is also requested at startup to clear any backlog.
  - `start_viewcam` / `kill_viewcam` / `messaging`: manual camera view and message relay.
- **Sensor** ([server/gpiozero_sensor.py](server/gpiozero_sensor.py)) is a separate service on the server Pi. The button emits `record` only when the last `state` was `idle`. The LED is on only while `idle`, i.e. off just during capture.
- **Manual control** ([server/keyboard.py](server/keyboard.py)): curtsies client (`r`/`m`/`v`/`s`).
- **Recorder Pi(s)** ([recorder/recorder_socketio.py](recorder/recorder_socketio.py)) calls [recorder/grava_com_bash.sh](recorder/grava_com_bash.sh) in two modes. `record <file>` captures to `*.mp4.part` and renames on success; the recorder then emits `recorded` and queues the file. `upload <file>` rsyncs it with `--remove-source-files`, run by a background thread with `UPLOAD_ATTEMPTS` retries, so the camera is free for the next interaction. After each upload it emits `mix`. Files whose upload ultimately fails stay in the recorder's videos dir and are not re-sent automatically.

Pipeline: **button (only if idle) → `record` → capture → `recorded` (installation free again) ∥ upload → `mix` → background overlay onto `mix.mp4` → `ffplay` reloads**. `mix.mp4` is cumulative.

## Gotchas

- The scripts can only run on the Pis (hardware, X display). Only syntax-check them on the dev Mac (`python3 -m py_compile`, `sh -n`). The refactor is untested on real hardware.
- The server's USB path (UUID `4BCF-8A8C`) and the `pi` user are config defaults and must match the Pis. The recorder needs SSH keys exchanged with the server.
- The `mix` glob is `2*.mp4`, so recordings must keep date-based names. `.part` files and `mix*.mp4` never match.
- `mixed.txt` in the videos folder records which clips are already mixed. On first run only the newest clip is pending. Delete the file to re-evaluate.
- `videopavio_server.service` needs `DISPLAY=:0.0`. The sensor service needs `DefaultDependencies=false` for GPIO access.
- `videos/white_videos/` holds blank seed videos for the initial `mix.mp4`.
