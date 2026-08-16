import logging
import os
import config
from scraper import scrape_linkedin, process_and_export

print("=== STARTING SCRIPT ===")

def configure_logging():
    os.makedirs(config.LOG_PATH, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(config.LOG_PATH, config.LOG_FILE),
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        encoding="utf-8",
    )

def main():
    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting scraper run")
    
    try:
        print("1. Running LinkedIn Job Scraper...")
        jobs_data = scrape_linkedin()
        
        print(f"2. Scraped {len(jobs_data)} jobs. Analyzing and exporting to Excel...")
        process_and_export(jobs_data)
        
        print("=== SCRIPT RUN COMPLETED ===")
    except Exception as e:
        logger.exception("Script failed")
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()