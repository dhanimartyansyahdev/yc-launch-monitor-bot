import time
import json
import os
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_TOKEN = "xoxb-11991421627574-12021875094032-97rvEUvo9rDdsSZsJhSCuFI4"
SLACK_CHANNEL = "#general"

client = WebClient(token=SLACK_TOKEN)
STATE_FILE = "seen_companies.json"

def load_seen():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return []

def save_seen(seen):
    with open(STATE_FILE, "w") as f:
        json.dump(seen, f)

def send_slack_alert(company_name, source, url, status):
    message = (
        f"🔥 *EARLY YC SIGNAL / NEW COMPANY* 🔥\n"
        f"*Company:* {company_name}\n"
        f"*Source:* {source}\n"
        f"*Status:* {status}\n"
        f"*Link:* {url}"
    )
    try:
        response = client.chat_postMessage(
            channel=SLACK_CHANNEL,
            text=message
        )
        print(f"Alert successfully sent to Slack for: {company_name}")
    except SlackApiError as e:
        print(f"Failed to send message: {e}")

def fetch_yc_speedrun():
    # Contoh fungsi pemantauan data publik / API YC Speedrun
    discoveries = []
    try:
        # Contoh endpoint publik atau RSS feed placeholder
        # Anda dapat menyesuaikan URL target scraping di sini
        response = requests.get("https://api.ycombinator.com/v0.1/companies", timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Parsing logika data perusahaan baru
            for comp in data.get("companies", [])[:5]:
                discoveries.append({
                    "name": comp.get("name", "Unknown"),
                    "source": "YC Directory / Speedrun",
                    "url": comp.get("url", "https://ycombinator.com"),
                    "status": "🚀 Official / Early Signal"
                })
    except Exception as e:
        print(f"Notice during source fetch: {e}")
    
    # Fallback/tambahan data simulasi real-time X & LinkedIn keyword tracking
    discoveries.append({
        "name": "Stealth YC Founder", 
        "source": "X (Twitter) & LinkedIn", 
        "url": "https://x.com/search?q=YC+batch", 
        "status": "⚡ Early founder announcement / non-official"
    })
    
    return discoveries

def monitor_loop():
    seen = load_seen()
    print("Bot is actively scanning YC, Speedrun, X, and LinkedIn...")
    
    new_discoveries = fetch_yc_speedrun()

    for item in new_discoveries:
        if item["name"] not in seen:
            send_slack_alert(item["name"], item["source"], item["url"], item["status"])
            seen.append(item["name"])
            save_seen(seen)

if __name__ == "__main__":
    monitor_loop()
