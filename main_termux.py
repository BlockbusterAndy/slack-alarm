import io
import time
import json
import logging
import os
import sys
import subprocess
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# --- LOGGING SETUP ---
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("poke_watcher.log", encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


# --- LOAD CONFIG ---
def load_config(path="config.json"):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file '{path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config: {e}")
        sys.exit(1)


# --- LOAD ENV ---
load_dotenv()
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
if not SLACK_TOKEN:
    logger.error("SLACK_TOKEN not found. Add it to your .env file.")
    sys.exit(1)


# --- TERMUX HELPERS ---
def termux_vibrate(duration_ms=1000):
    """Vibrate the device using termux-vibrate."""
    try:
        subprocess.run(
            ["termux-vibrate", "-d", str(duration_ms), "-f"],
            timeout=5,
            check=False
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass  # termux-api not installed or unavailable


def termux_notify(title, content):
    """Send a persistent Android notification via termux-notification."""
    try:
        subprocess.run(
            [
                "termux-notification",
                "--title", title,
                "--content", content,
                "--id", "slack-alarm",
                "--priority", "high",
                "--ongoing",
            ],
            timeout=5,
            check=False
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass  # termux-api not installed or unavailable


def termux_notify_remove():
    """Dismiss the ongoing notification."""
    try:
        subprocess.run(
            ["termux-notification-remove", "slack-alarm"],
            timeout=5,
            check=False
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass


def play_sound_once(sound_path):
    """
    Play a sound file once using termux-media-player.
    Falls back to mpv, then ffplay if not available.
    Returns True if playback started successfully.
    """
    players = [
        ["termux-media-player", "play", sound_path],
        ["mpv", "--no-terminal", "--really-quiet", sound_path],
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", sound_path],
    ]
    for cmd in players:
        try:
            result = subprocess.run(
                cmd,
                timeout=30,
                check=False,
                stderr=subprocess.DEVNULL
            )
            if result.returncode == 0:
                return True
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            return True  # Assume it played long enough
    return False


# --- SOUND ALARM ---
def play_alarm(sound_path):
    """
    Plays the sound in a continuous loop, vibrates, and sends a
    persistent notification until the user stops with Ctrl+C.
    """
    logger.warning("ALARM ACTIVATED! Persistent alert mode. Press Ctrl+C to stop.")

    termux_notify(
        title="Slack Alarm Triggered!",
        content="New message from a watched user. Open Termux to dismiss."
    )

    try:
        while True:
            # Vibrate + play sound each cycle
            termux_vibrate(1500)
            played = play_sound_once(sound_path)

            if not played:
                # No audio player found — fall back to visual alarm
                print("\n" + "* " * 20)
                print("         WAKE UP! NEW SLACK MESSAGE!")
                print("* " * 20 + "\n")

            time.sleep(1)

    except KeyboardInterrupt:
        termux_notify_remove()
        raise


# --- CORE WATCHER ---
def check_for_pokes(client, config):
    alarm_sender_ids = set(config["alarm_sender_ids"])
    check_interval = config.get("check_interval", 5)
    buzzer_sound_path = config.get("buzzer_sound_path", "buzzer.mp3")

    logger.info("Watching for incoming pings... Happy napping!")
    last_check_ts = str(time.time())

    while True:
        try:
            response = client.conversations_list(types="im")
            channels = response.get("channels", [])

            for channel in channels:
                if channel.get("user") not in alarm_sender_ids:
                    continue

                history = client.conversations_history(
                    channel=channel["id"],
                    oldest=last_check_ts,
                    limit=5
                )

                messages = history.get("messages", [])
                if messages:
                    play_alarm(buzzer_sound_path)

            last_check_ts = str(time.time())

        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

        time.sleep(check_interval)


# --- ENTRY POINT ---
if __name__ == "__main__":
    config = load_config()
    client = WebClient(token=SLACK_TOKEN)

    try:
        check_for_pokes(client, config)
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully. Sweet dreams!")
