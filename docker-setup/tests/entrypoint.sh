#!/bin/bash
set -e

DISPLAY_NUM=99
export DISPLAY=":${DISPLAY_NUM}"
VNC_PORT="${VNC_PORT:-5900}"

echo "[entrypoint] Starting Xvfb on display ${DISPLAY} ..."
Xvfb "${DISPLAY}" -screen 0 1920x1080x24 -ac &
XVFB_PID=$!
sleep 1

if [ "${HEADLESS}" = "false" ]; then
    echo "[entrypoint] Headed mode — starting x11vnc on port ${VNC_PORT} ..."
    x11vnc -display "${DISPLAY}" -nopw -listen 0.0.0.0 -port "${VNC_PORT}" \
           -forever -shared -quiet &
fi

cd /app
export PYTHONPATH=/app

echo "[entrypoint] Python path: ${PYTHONPATH}"
echo "[entrypoint] Working dir: $(pwd)"
echo "[entrypoint] Tests dir contents: $(ls /app/tests/ 2>/dev/null || echo 'NOT FOUND')"

# Pass --headed flag to playwright if HEADLESS=false
HEADED_FLAG=""
if [ "${HEADLESS}" = "false" ]; then
    HEADED_FLAG="--headed"
fi

echo "[entrypoint] Running: pytest $* ${HEADED_FLAG}"
pytest "$@" ${HEADED_FLAG}
EXIT_CODE=$?

kill "${XVFB_PID}" 2>/dev/null || true
exit "${EXIT_CODE}"