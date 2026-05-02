import httpx
import os
import logging

# Discord Webhook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1500231860381417502/4FY3X-Ja03vL3E_DZL1c5ril7mjL7IGDiCYQ62OShscesMJyI7JRxym2oTnHkqdqr9w8"

def send_deal(source, title, price, link, color=0x3498db):
    if not WEBHOOK_URL:
        logging.warning("DISCORD_WEBHOOK_URL not set. Skipping notification.")
        return
    
    payload = {
        "embeds": [{
            "title": f"🎯 {title}",
            "description": f"**Source:** {source}\n**Info:** {price}",
            "url": link,
            "color": color,
            "footer": {"text": "Modular Deal Sniper"}
        }]
    }
    try:
        response = httpx.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to send Discord notification: {e}")

def send_error(msg):
    if not WEBHOOK_URL: return
    try:
        httpx.post(WEBHOOK_URL, json={"content": f"⚠️ **Sniper Alert:** {msg}"})
    except:
        pass
