import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CTFD_URL = os.getenv("CTFD_URL")
CTFD_API_KEY = os.getenv("CTFD_API_KEY")
ANNOUNCE_CHANNEL_ID = int(os.getenv("ANNOUNCE_CHANNEL_ID", "0"))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "30"))  # seconds
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()  # Default to INFO

if not all([DISCORD_TOKEN, CTFD_URL, CTFD_API_KEY, ANNOUNCE_CHANNEL_ID]):
    raise ValueError("Missing one or more required environment variables.")
