# slack-alarm

Watches Slack DMs from specified users and plays an alarm sound when a new message arrives. Useful for staying alert to important pings while away from your desk.

## Setup

1. **Clone & create a virtual environment**
   ```bash
   python -m venv venv
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** with your Slack bot token:
   ```
   SLACK_TOKEN=xoxb-your-token-here
   ```

4. **Edit `config.json`** to configure:
   - `alarm_sender_ids` — Slack user IDs to watch for messages
   - `check_interval` — How often to poll, in seconds (default: `5`)
   - `buzzer_sound_path` — Path to the alarm sound file (default: `buzzer.mp3`)

## Run

```powershell
.\start_alarm.ps1
```

Or directly:

```bash
python main.py
```

## Notes

- Requires a Slack app with `channels:history`, `im:history`, and `im:read` OAuth scopes.
- Logs are written to `poke_watcher.log`.
- Stop with `Ctrl+C`.

---

## Termux (Android)

Use `main_termux.py` and `start_alarm.sh` instead of the Windows versions. No `winsound` or `playsound` dependency — alarms are delivered via Android vibration, a persistent notification, and an audio player if available.

### 1. Install Termux packages

```bash
pkg update && pkg upgrade
pkg install python git mpv termux-api
```

> Also install the **[Termux:API](https://f-droid.org/packages/com.termux.api/)** companion app from F-Droid and grant it **Notifications** and **Vibration** permissions in Android Settings.

### 2. Clone the repo (or copy files)

```bash
git clone https://github.com/your-username/slack-alarm.git
cd slack-alarm
```

### 3. (Optional) Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 4. Install Python dependencies

```bash
pip install -r requirements_termux.txt
```

### 5. Create `.env`

```bash
echo "SLACK_TOKEN=xoxb-your-token-here" > .env
```

### 6. Copy your alarm sound

Put `buzzer.mp3` (or any audio file) in the project folder and make sure `buzzer_sound_path` in `config.json` points to it.

### 7. Run

```bash
bash start_alarm.sh
```

Or directly:

```bash
python main_termux.py
```

### Audio player priority

The script tries players in this order and uses the first one found:

| Player | Install |
|---|---|
| `termux-media-player` | included with `termux-api` |
| `mpv` | `pkg install mpv` |
| `ffplay` | `pkg install ffmpeg` |

If none are available, the alarm falls back to a repeating visual printout in the terminal.

### Keep it running in the background

Use a Termux wake-lock so Android doesn't kill the process:

```bash
termux-wake-lock
bash start_alarm.sh
```

To run it in a persistent session, use `tmux`:

```bash
pkg install tmux
tmux new -s alarm
bash start_alarm.sh
# Detach with Ctrl+B then D
```
