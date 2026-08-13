import sys
import logging
from src.utils import setup_logging, generate_random_passport, generate_random_dob, generate_random_mobile, generate_gmail_alias
from src.saudia_signup import SaudiaSignupManager
from src.temp_mail import TempMailClient

setup_logging()
logger = logging.getLogger("TestSaudia")

def run_test():
    logger.info("Starting Saudia signup test...")
    saudia = SaudiaSignupManager()
    temp_mail = TempMailClient()
    
    try:
        # 1. Setup passenger details
        passenger_details = {
            "passenger_name": "Test Passenger",
            "passport": generate_random_passport(),
            "dob": generate_random_dob(),
            "mobile": generate_random_mobile()
        }
        
        # 2. Get unique email
        base_email = temp_mail.generate_email()
        unique_email = generate_gmail_alias(base_email, 0)
        password = "Dreams@1003" # Standarized password matching prompt.txt
        
        logger.info(f"Details: {passenger_details}")
        logger.info(f"Email: {unique_email}, Password: {password}")
        
        # 3. Start Saudia Signup Manager
        saudia.start()
        
        # 4. Automate Saudia registration
        logger.info("Registering on Saudia...")
        status = saudia.create_membership(passenger_details, unique_email, password)
        logger.info(f"Signup submitted. Status: {status}")
        
        # Take a screenshot to verify step
        saudia.page.screenshot(path="saudia_signup_step.png")
        logger.info("Saved signup step screenshot to saudia_signup_step.png")
        
        if status == "SUCCESS_PENDING_ACTIVATION":
            logger.info("Signup step successful! The system is now waiting for the activation email.")
            # Note: During actual run, we would listen to temp mail inbox here.
            
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        saudia.stop()

if __name__ == "__main__":
    run_test()
