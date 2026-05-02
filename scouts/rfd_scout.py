import httpx
import logging
from bs4 import BeautifulSoup
from database import is_new_deal, save_deal
from notifier import send_deal

# RSS is 100% reliable and doesn't care about CSS classes
RFD_RSS_URL = "https://forums.redflagdeals.com/feed/forum/9"

def check_deals(config):
    keywords = [k.lower() for k in config.get('rfd_keywords', [])]
    
    # Note: RSS doesn't provide vote counts, so we'll match on keywords only.
    # This is the "Nuclear Option" to ensure the sniper actually finds deals.
    logging.info("Scraping RedFlagDeals via RSS Feed (Bulletproof Method)...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        with httpx.Client(headers=headers, follow_redirects=True) as client:
            response = client.get(RFD_RSS_URL, timeout=30)
            response.raise_for_status()
            
            # Parse as XML
            soup = BeautifulSoup(response.text, "xml")
            items = soup.find_all("item")
            
            logging.info(f"RFD RSS: Found {len(items)} items.")
            
            for item in items:
                title_el = item.find("title")
                link_el = item.find("link")
                
                if not title_el or not link_el: continue
                
                title = title_el.get_text().strip()
                link = link_el.get_text().strip()
                
                # Unique ID from link
                deal_id = f"rfd_rss_{link.split('/')[-2]}" if '/' in link else f"rfd_rss_{title[:20]}"
                
                # Filter Logic: Match keyword
                matches_keyword = any(k in title.lower() for k in keywords)
                
                # Since we don't have votes in RSS, we rely on keywords.
                # (Or we could notify for EVERYTHING if min_votes is set to 0)
                if matches_keyword and is_new_deal(deal_id):
                    logging.info(f"🔥 Found RFD Deal (RSS): {title}")
                    send_deal(
                        source="RedFlagDeals (RSS)",
                        title=title,
                        price="New Deal Spotted via RSS",
                        link=link,
                        color=0xFF4500
                    )
                    save_deal(deal_id)
                    
    except Exception as e:
        logging.error(f"RFD Scout Error (RSS): {e}")
