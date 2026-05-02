import httpx
import logging
from bs4 import BeautifulSoup
from database import is_new_deal, save_deal
from notifier import send_deal

RFD_URL = "https://forums.redflagdeals.com/hot-deals-f9/"

def check_deals(config):
    keywords = [k.lower() for k in config.get('rfd_keywords', [])]
    min_votes = config.get('rfd_min_votes', 15)

    logging.info("Scraping RedFlagDeals via BeautifulSoup...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.redflagdeals.com/",
    }

    try:
        with httpx.Client(headers=headers, follow_redirects=True) as client:
            response = client.get(RFD_URL, timeout=30)
            logging.info(f"RFD Response Code: {response.status_code}")
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            threads = soup.select("li.topic")
            logging.info(f"RFD Found {len(threads)} threads.")
            
            if len(threads) == 0:
                # Fallback: some pages use 'li.row'
                threads = soup.select("li.row")
                logging.info(f"RFD Fallback: Found {len(threads)} rows.")
            
            if len(threads) > 0:
                logging.info(f"Sample Thread HTML: {str(threads[0])[:500]}")
            
            for thread in threads:
                # Try multiple common selectors for the title link
                title_el = thread.select_one("a.topic_title, a.topic-title, a.thread-title-link, a.thread_title_link, .title a, .thread-title a, h3 a, a[class*='title']")
                vote_el = thread.select_one("dl.post_voting, .voting, .vote-count, .post_voting")
                
                if not title_el:
                    logging.warning("Skipping thread: No title link found.")
                    continue
                
                title = title_el.get_text().strip()
                href = title_el.get("href", "")
                if not href: continue
                
                link = "https://forums.redflagdeals.com" + href
                
                # Unique ID from link
                deal_id = f"rfd_{link.split('-')[-1].replace('/', '')}"
                
                # Extract votes
                votes = 0
                if vote_el:
                    try:
                        vote_text = vote_el.select_one("dt").get_text()
                        votes = int(vote_text.replace("+", "").replace("-", "0").strip() or 0)
                    except: pass

                # Logic: Match keyword OR hit vote threshold
                matches_keyword = any(k in title.lower() for k in keywords)
                
                logging.info(f"Checking: {title[:50]}... | Votes: {votes} | Match: {matches_keyword}")
                
                if (matches_keyword or votes >= min_votes) and is_new_deal(deal_id):
                    logging.info(f"🔥 Found RFD Deal: {title} ({votes} votes)")
                    send_deal(
                        source="RedFlagDeals",
                        title=title,
                        price=f"Votes: {votes}",
                        link=link,
                        color=0xFF4500
                    )
                    save_deal(deal_id)
                    
    except Exception as e:
        logging.error(f"RFD Scout Error (BS4): {e}")
