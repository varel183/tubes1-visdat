import subprocess
import time
from playwright.sync_api import sync_playwright

print("Starting HTTP server on port 8089...")
server = subprocess.Popen(["python", "-m", "http.server", "8089"])
time.sleep(2)

try:
    with sync_playwright() as p:
        print("Launching browser...")
        try:
            browser = p.chromium.launch(channel="msedge", headless=True)
        except Exception as e:
            print("Failed to launch Edge. Please run: playwright install chromium")
            raise e
            
        page = browser.new_page(viewport={"width": 1000, "height": 3200}, device_scale_factor=2)
        print("Navigating to index.html...")
        page.goto("http://localhost:8089/index.html", wait_until="networkidle")
        
        print("Waiting 2.5 seconds for Chart.js animation to complete...")
        time.sleep(2.5)
        
        print("Taking screenshot...")
        page.screenshot(path="poster_final.png", full_page=True)
        
        print("Screenshot saved to poster_final.png!")
        browser.close()
finally:
    print("Stopping server...")
    server.terminate()
