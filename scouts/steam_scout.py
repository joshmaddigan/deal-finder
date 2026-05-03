import httpx
import logging
from database import is_new_deal, save_deal
from notifier import send_deal

STEAM_API = "https://store.steampowered.com/api/featuredcategories/?cc=CA"

def check_deals(config):
    min_discount = config.get('steam_min_discount', 75)
    logging.info("Checking Steam Specials API (CAD)...")
    
    try:
        target_currency = config.get('target_currency', 'CAD')
        response = httpx.get(STEAM_API, timeout=30)
        data = response.json()
        
        specials = data.get('specials', {}).get('items', [])
        
        for item in specials:
            discount = item.get('discount_percent', 0)
            currency = item.get('currency', 'USD')
            
            # Strict currency filter
            if currency != target_currency:
                continue

            if discount >= min_discount:
                deal_id = f"steam_{item['id']}"
                
                if is_new_deal(deal_id):
                    title = item['name']
                    orig = item['original_price'] / 100
                    final = item['final_price'] / 100
                    
                    logging.info(f"🎮 Found Steam Deal: {title} (-{discount}%) in {currency}")
                    send_deal(
                        source="Steam Specials",
                        title=title,
                        price=f"~~{orig} {currency}~~ **{final} {currency}** (-{discount}%)",
                        link=f"https://store.steampowered.com/app/{item['id']}",
                        color=0x171a21 # Steam Dark Blue
                    )
                    save_deal(deal_id)
    except Exception as e:
        logging.error(f"Steam Scout failed: {e}")
