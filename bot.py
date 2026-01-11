import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from playwright.async_api import async_playwright

# Environment variables
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
RUMBLE_USERNAME = os.environ["RUMBLE_USERNAME"]
RUMBLE_PASSWORD = os.environ["RUMBLE_PASSWORD"]

async def upload_to_rumble(file_path, title):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Login to Rumble
        await page.goto("https://rumble.com/login")
        await page.fill('input[name="username"]', RUMBLE_USERNAME)
        await page.fill('input[name="password"]', RUMBLE_PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(5000)

        # Go to upload page
        await page.goto("https://rumble.com/upload/")
        await page.set_input_files('input[type="file"]', file_path)
        await page.fill('input[name="title"]', title)
        await page.fill('textarea[name="description"]', "Uploaded via Telegram bot")
        await page.click('button:has-text("Publish")')

        # Wait for upload to complete (adjust if video is large)
        await page.wait_for_timeout(20000)
        print(f"Upload finished: {file_path}")

        await browser.close()

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.video.file_id
    print(f"Received video: {file_id}")

    # Download video
    file = await context.bot.get_file(file_id)
    local_filename = f"{file_id}.mp4"
    await file.download_to_drive(local_filename)
    print(f"Downloaded video: {local_filename}")

    # Reply immediately
    await update.message.reply_text("Video received! Uploading to Rumble...")

    # Upload to Rumble
    try:
        await upload_to_rumble(local_filename, f"Telegram Upload {file_id}")
        await update.message.reply_text("Video uploaded to Rumble successfully! ✅")
    except Exception as e:
        print("Upload failed:", e)
        await update.message.reply_text("Failed to upload video to Rumble ❌")

# Build bot
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.VIDEO, handle_video))
print("Bot started listening...")
app.run_polling()
