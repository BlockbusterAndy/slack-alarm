#!/data/data/com.termux/files/usr/bin/bash
# Slack Alarm — Termux launcher
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Activate venv if present ──────────────────────────────────────────────────
if [ -d "venv" ]; then
    # shellcheck disable=SC1091
    source venv/bin/activate
fi

# ── Dependency check ──────────────────────────────────────────────────────────
if ! python -c "import slack_sdk" 2>/dev/null; then
    echo "[setup] Installing Python dependencies..."
    pip install -r requirements_termux.txt
fi

# ── termux-api hint ───────────────────────────────────────────────────────────
if ! command -v termux-vibrate &>/dev/null; then
    echo "[hint] For vibration + Android notifications install termux-api:"
    echo "       pkg install termux-api"
    echo "       Also enable the Termux:API companion app on your device."
fi

# ── Audio player hint ─────────────────────────────────────────────────────────
if ! command -v termux-media-player &>/dev/null && \
   ! command -v mpv &>/dev/null && \
   ! command -v ffplay &>/dev/null; then
    echo "[hint] No audio player found. Install one for sound:"
    echo "       pkg install mpv        # recommended"
    echo "       pkg install ffmpeg     # provides ffplay"
fi

# .env must exist
if [ ! -f ".env" ]; then
    echo "[error] .env file not found."
    echo "        Create it with:  echo 'SLACK_TOKEN=xoxb-...' > .env"
    exit 1
fi

echo "[slack-alarm] Starting watcher..."
python main_termux.py
