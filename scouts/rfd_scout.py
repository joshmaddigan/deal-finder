import logging
from playwright.sync_api import sync_playwright
from database import is_new_deal, save_deal
from notifier import send_deal

RFD_URL = "https://forums.redflagdeals.com/hot-deals-f9/"

def check_deals(config):
    keywords = [k.lower() for k in config.get('rfd_keywords', [])]
    min_votes = config.get('rfd_min_votes', 15)

    logging.info("Scraping RedFlagDeals...")
    
    with sync_playwright() as p:
        # Explicitly use chromium to avoid headless shell issues on some environments
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(RFD_URL, timeout=60000)
            # Select all deal threads
            threads = page.query_selector_all("li.topic")
            
            for thread in threads:
                title_el = thread.query_selector("a.topic_title")
                vote_el = thread.query_selector("dl.post_voting")
                
                if not title_el: continue
                
                title = title_el.inner_text().strip()
                link = "https://forums.redflagdeals.com" + title_el.get_attribute("href")
                
                # Unique ID from link
                deal_id = f"rfd_{link.split('-')[-1].replace('/', '')}"
                
                # Extract votes
                votes = 0
                if vote_el:
                    try:
                        vote_text = vote_el.query_selector("dt").inner_text()
                        votes = int(vote_text.replace("+", "").replace("-", "0") or 0)
                    except: pass

                # Logic: Match keyword OR hit vote threshold
                matches_keyword = any(k in title.lower() for k in keywords)
                
                if (matches_keyword or votes >= min_votes) and is_new_deal(deal_id):
                    logging.info(f"🔥 Found RFD Deal: {title} ({votes} votes)")
                    send_deal(
                        source="RedFlagDeals",
                        title=title,
                        price=f"Votes: {votes}",
                        link=link,
                        color=0xFF4500 # Orange-Red
                    )
                    save_deal(deal_id)
        except Exception as e:
            logging.error(f"RFD Scout Error: {e}")
        finally:
            browser.close()
