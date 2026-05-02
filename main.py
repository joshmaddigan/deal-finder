import os
import time
import yaml
import importlib
import logging
import sys
from database import init_db
from notifier import send_error

# Configure logging to see what's happening in Railway logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def load_config():
    try:
        with open("filters.yaml", "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Failed to load filters.yaml: {e}")
        return {}

def run_sniper():
    logging.info("🚀 Starting Deal Sniper Engine...")
    init_db()
    
    while True:
        config = load_config()
        # Dynamically find all scouts in the scouts/ directory
        scout_files = [
            f[:-3] for f in os.listdir("scouts") 
            if f.endswith(".py") and f != "__init__.py"
        ]
        
        logging.info(f"Checking {len(scout_files)} scouts for new deals...")
        
        for scout_name in scout_files:
            try:
                # Import or reload the scout module
                module_path = f"scouts.{scout_name}"
                if module_path in sys.modules:
                    module = importlib.reload(sys.modules[module_path])
                else:
                    module = importlib.import_module(module_path)
                
                # Execute the scout
                if hasattr(module, 'check_deals'):
                    module.check_deals(config)
                else:
                    logging.warning(f"Scout {scout_name} is missing check_deals() function.")
            except Exception as e:
                logging.error(f"Error in scout {scout_name}: {e}")
                send_error(f"Scout Error [{scout_name}]: {e}")

        wait_time = config.get('check_interval_seconds', 300)
        logging.info(f"Cycle complete. Sleeping for {wait_time}s...")
        time.sleep(wait_time)

if __name__ == "__main__":
    run_sniper()
