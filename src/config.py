import os
from dotenv import load_dotenv

load_dotenv()

# File paths
INPUT_EXCEL_PATH = os.getenv("INPUT_EXCEL_PATH", "Etihad_Bookings.xlsx")
OUTPUT_EXCEL_PATH = os.getenv("OUTPUT_EXCEL_PATH", "Etihad_Bookings_Processed.xlsx")

# Etihad Configuration
ETIHAD_MANAGE_BOOKING_URL = "https://www.etihad.com/en-in/manage"

SAUDIA_SIGNUP_URL = "https://www.saudia.com"  # Saudia Home Page (bypass WAF check)

# Browser Settings
HEADLESS = os.getenv("HEADLESS", "False").lower() in ("true", "1", "yes")
TIMEOUT = int(os.getenv("TIMEOUT", "30000")) # ms
