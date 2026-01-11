import os
import requests
from telegram.ext import Updater, MessageHandler, Filters

# Your GitHub repo
GITHUB_REPO = "SparrowUSA/UploaderTest"

# Get tokens from Railway environment variables
GITHUB_TOKEN = os.environ["MY_GITHUB_TOKEN"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

# Function to handle incoming video messages
def handle_video(update, context):
    file_id = update.message.video.file_id

    # Trigger GitHub Actions workflow
    requests.post(
        f"https://api.github.com/repos/{GITHUB_REPO}/dispatches",
        headers={
            "Accept": "application/vnd.github.everest-preview+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
        },
        json={
            "event_type": "telegram_video_received",
            "client_payload": {"file_id": file_id},
        },
    )

    # Reply to user
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Video received! Uploading to Rumble..."
    )

# Set up the bot
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.video, handle_video))

# Start the bot
updater.start_polling()
updater.idle()
