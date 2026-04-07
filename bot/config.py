import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", 0))
LOG_FILE = os.getenv("LOG_FILE", "/var/log/bacon-bot.log")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env")
