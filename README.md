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
