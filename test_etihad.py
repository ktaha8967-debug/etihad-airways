import sys
import logging
from src.utils import setup_logging
from src.etihad_scraper import EtihadScraper

setup_logging()
logger = logging.getLogger("TestEtihad")

def test():
    logger.info("Starting Etihad access test...")
    scraper = EtihadScraper()
    try:
        scraper.start()
        # Try accessing another booking from 9th Aug
        pnr = "DSSP38"
        last_name = "JUDES"
        
        success = scraper.access_booking(pnr, last_name)
        if success:
            logger.info("Test Success: Managed to access Etihad booking page!")
            is_ff = scraper.check_frequent_flyer_status()
            logger.info(f"Frequent Flyer Status: {is_ff}")
            details = scraper.extract_passenger_details()
            logger.info(f"Extracted details: {details}")
        else:
            logger.error("Test Failed: Could not access Etihad booking page. Please check screenshot or page source.")
            # Save screenshot for debugging
            scraper.page.screenshot(path="etihad_test_fail.png")
            logger.info("Saved debug screenshot to etihad_test_fail.png")
    except Exception as e:
        logger.error(f"An error occurred during testing: {e}", exc_info=True)
    finally:
        scraper.stop()

if __name__ == "__main__":
    test()
