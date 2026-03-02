import io
import time
import json
import logging
import os
import sys
import winsound
from playsound import playsound
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


# --- SOUND ---
def play_alarm(sound_path):
    """
    Plays the sound in a continuous loop until the user 
    manually stops the program with Ctrl+C.
    """
    logger.warning("🚨 ALARM ACTIVATED! Persistent alert mode. Press Ctrl+C to stop.")
    try:
        while True:  # Continuous loop for persistent alarm
            playsound(sound_path)
            # Short pause between repeats so it doesn't crash the audio driver
            time.sleep(1) 
    except KeyboardInterrupt:
        # This allows the user to stop the loop with Ctrl+C
        raise 
    except Exception as e:
        logger.warning(f"Could not play sound '{sound_path}': {e}")
        while True:
            print("\n" + "🚨 " * 20)
            print("         WAKE UP! NEW MESSAGE!")
            print("🚨 " * 20 + "\n")
            time.sleep(2)


# --- CORE WATCHER ---
def check_for_pokes(client, config):
    alarm_sender_ids = set(config["alarm_sender_ids"])
    check_interval = config.get("check_interval", 5)
    buzzer_sound_path = config.get("buzzer_sound_path", "buzzer.mp3")

    logger.info("Watching for incoming pings... Happy napping! 😴")
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
                    # Once a message is found, enter the infinite alarm loop
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
        logger.info("Shutting down gracefully. Sweet dreams! 😴")