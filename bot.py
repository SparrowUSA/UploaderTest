import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

GITHUB_REPO = "SparrowUSA/UploaderTest"
GITHUB_TOKEN = os.environ["MY_GITHUB_TOKEN"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await update.message.reply_text("Video received! Uploading to Rumble...")

# Build and run the bot
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.VIDEO, handle_video))
app.run_polling()
