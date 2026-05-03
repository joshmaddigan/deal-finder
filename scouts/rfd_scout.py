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
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        with httpx.Client(headers=headers, follow_redirects=True) as client:
            response = client.get(RFD_URL, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            threads = soup.select("li.topic")

            for thread in threads:
                # Title is in h3.thread_title
                title_el = thread.select_one("h3.thread_title")
                # Link is on a.topic-card-info (the main clickable wrapper)
                link_el = thread.select_one("a.topic-card-info, a.thread_info")
                # Votes
                vote_el = thread.select_one("span.vote-btn-down, dl.post_voting, .vote_count, .voting-count")

                if not title_el or not link_el:
                    continue

                title = title_el.get_text().strip()
                href = link_el.get("href", "")
                if not href:
                    continue

                link = "https://forums.redflagdeals.com" + href
                deal_id = f"rfd_{thread.get('data-thread-id', href.split('/')[-2])}"

                # Extract votes
                votes = 0
                if vote_el:
                    try:
                        vote_text = vote_el.get_text().strip()
                        votes = int(vote_text.replace("+", "").replace("-", "0").strip() or 0)
                    except:
                        pass

                matches_keyword = any(k in title.lower() for k in keywords)
                logging.info(f"Checking: {title[:55]}... | Votes: {votes} | Match: {matches_keyword}")

                if (matches_keyword or votes >= min_votes) and is_new_deal(deal_id):
                    logging.info(f"Found RFD Deal: {title} ({votes} votes)")
                    send_deal(
                        source="RedFlagDeals",
                        title=title,
                        price=f"Votes: {votes} (CAD)",
                        link=link,
                        color=0xFF4500
                    )
                    save_deal(deal_id)

    except Exception as e:
        logging.error(f"RFD Scout Error: {e}")
