import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# GitHub repo for triggering workflow
GITHUB_REPO = "SparrowUSA/UploaderTest"

# Environment variables (set in Railway)
GITHUB_TOKEN = os.environ["MY_GITHUB_TOKEN"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

# Async handler for incoming video messages
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the video file ID from Telegram
    file_id = update.message.video.file_id
    print(f"Received video: {file_id}")

    # Download video from Telegram
    file = await context.bot.get_file(file_id)
    local_filename = f"{file_id}.mp4"
    await file.download_to_drive(local_filename)
    print(f"Video downloaded: {local_filename}")

    # Trigger GitHub Actions workflow
    response = requests.post(
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
    print(f"Triggered GitHub workflow, status code: {response.status_code}")

    # Reply to user
    await update.message.reply_text("Video received! Uploading to Rumble...")

# Build and run the bot
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.VIDEO, handle_video))
print("Bot started listening...")
app.run_polling()
