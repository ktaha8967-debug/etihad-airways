import sys
import logging
from src.utils import setup_logging
from src.etihad_scraper import EtihadScraper

setup_logging()
logger = logging.getLogger("TestEmailUpdate")

def run_test():
    scraper = EtihadScraper()
    try:
        scraper.start()
        pnr = "DSSP38"
        last_name = "JUDES"
        
        if scraper.access_booking(pnr, last_name):
            logger.info("Access success. Attempting to click edit contact details...")
            # Let's take a screenshot of the main page first
            scraper.page.screenshot(path="etihad_details_page.png")
            logger.info("Saved details page screenshot.")
            
            # Find and click on the expandable passenger card row using the passenger last name (force click to bypass overlay labels)
            passenger_row = scraper.page.locator(f"text={last_name}").first
            logger.info("Clicking passenger details card to expand...")
            passenger_row.click(force=True)
            scraper.page.wait_for_timeout(3000)
            scraper.page.screenshot(path="etihad_details_expanded.png")
            logger.info("Saved expanded details screenshot to etihad_details_expanded.png")
            
            # Now search for the Edit details or Edit contact button inside the expanded content
            edit_btn = scraper.page.locator("button:has-text('Edit'), a:has-text('Edit'), :text('Edit details'), [class*='edit-contact'], [class*='edit']").first
            if edit_btn.is_visible():
                edit_btn.click()
                scraper.page.wait_for_timeout(4000)
                scraper.page.screenshot(path="etihad_edit_modal.png")
                logger.info("Clicked edit button. Saved modal screenshot to etihad_edit_modal.png")
            else:
                logger.warning("Edit details button not found in expanded card.")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        scraper.stop()

if __name__ == "__main__":
    run_test()
