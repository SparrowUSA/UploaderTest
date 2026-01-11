import os
from telegram import Bot

# Get values from GitHub secrets and event
token = os.environ["TELEGRAM_BOT_TOKEN"]
file_id = os.environ["TELEGRAM_FILE_ID"]

# Connect to Telegram bot
bot = Bot(token=token)

# Get the file from Telegram servers
file = bot.get_file(file_id)

# Download as video.mp4
file.download("video.mp4")

print("Video downloaded as video.mp4")
