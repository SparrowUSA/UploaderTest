import os
import requests
from telegram.ext import Updater, MessageHandler, Filters

# Your GitHub repo here
GITHUB_REPO = "SparrowUSA/UploaderTest"       # <-- change this to your GitHub username/repo
GITHUB_TOKEN = os.environ["MY_GITHUB_TOKEN"]  # <-- matches the secret you just created

def handle_video(update, context):
    file_id = update.message.video.file_id

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
    update.message.reply_text("Video received! Uploading to Rumble...")

updater = Updater(os.environ["TELEGRAM_BOT_TOKEN"], use_context=True)
updater.dispatcher.add_handler(MessageHandler(Filters.video, handle_video))
updater.start_polling()
updater.idle()
