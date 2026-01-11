import os
from playwright.sync_api import sync_playwright

# Get Rumble login info and video path from GitHub secrets
email = os.environ["RUMBLE_EMAIL"]
password = os.environ["RUMBLE_PASSWORD"]
video_path = os.environ["VIDEO_PATH"]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Go to Rumble login
    page.goto("https://rumble.com")
    page.click("text=Log In")

    page.fill('input[type="email"]', email)
    page.fill('input[type="password"]', password)
    page.click('button[type="submit"]')

    page.wait_for_load_state("networkidle")

    # Go to upload page
    page.goto("https://rumble.com/upload.php")
    page.set_input_files('input[type="file"]', video_path)

    # Wait a few seconds for upload to finish
    page.wait_for_timeout(20000)

    browser.close()

print("Uploaded to Rumble successfully")
