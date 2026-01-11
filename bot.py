import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from playwright.async_api import async_playwright

# Environment variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
RUMBLE_USERNAME = os.environ.get("RUMBLE_USERNAME")
RUMBLE_PASSWORD = os.environ.get("RUMBLE_PASSWORD")

if not TELEGRAM_BOT_TOKEN or not RUMBLE_USERNAME or not RUMBLE_PASSWORD:
    raise Exception("One or more environment variables are missing!")

async def upload_to_rumble(file_path, title):
    print("Starting Playwright upload...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Login
            print("Going to Rumble login page...")
            await page.goto("https://rumble.com/login")
            await page.fill('input[name="username"]', RUMBLE_USERNAME)
            await page.fill('input[name="password"]', RUMBLE_PASSWORD)
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(5000)
            print("Login done.")

            # Upload page
            await page.goto("https://rumble.com/upload/")
            await page.set_input_files('input[type="file"]', file_path)
            await page.fill('input[name="title"]', title)
            await page.fill('textarea[name="description"]', "Uploaded via Telegram bot")
            await page.click('button:has-text("Publish")')
            print("Upload started...")

            # Wait for upload to complete (adjust timeout if needed)
            await page.wait_for_timeout(20000)
            print(f"Upload finished: {file_path}")

            await browser.close()
    except Exception as e:
        print("Playwright upload error:", e)
        raise e  # re-raise to handle in main handler

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file_id = update.message.video.file_id
        print(f"Received video: {file_id}")

        # Download video
        file = await context.bot.get_file(file_id)
        local_filename = f"{file_id}.mp4"
        await file.download_to_drive(local_filename)
        print(f"Downloaded video: {local_filename}")

        # Reply immediately after download
        try:
            await update.message.reply_text("Video received! Uploading to Rumble...")
        except Exception as e:
            print("Telegram reply failed:", e)

        # Upload to Rumble
        try:
            await upload_to_rumble(local_filename, f"Telegram Upload {file_id}")
            try:
                await update.message.reply_text("Video uploaded to Rumble successfully! ✅")
            except Exception as e:
                print("Telegram final reply failed:", e)
        except Exception as e:
            try:
                await update.message.reply_text(f"Failed to upload video: {e} ❌")
            except Exception as te:
                print("Telegram error reply failed:", te)

    except Exception as e:
        print("Handler error:", e)
        try:
            await update.message.reply_text(f"Unexpected error: {e} ❌")
        except Exception as te:
            print("Telegram error reply failed:", te)

# Build and run the bot
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.VIDEO, handle_video))
print("Bot started listening...")
app.run_polling()
