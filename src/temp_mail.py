import requests
import time
import logging

logger = logging.getLogger(__name__)

class TempMailClient:
    """
    Helper class to interface with a temporary email provider API (e.g., 1secmail or mail.tm)
    to generate email addresses and fetch incoming messages (OTP, e-tickets).
    """
    def __init__(self):
        self.api_url = "https://www.1secmail.com/api/v1/"
        self.email_address = None
        self.username = None
        self.domain = None

    def generate_email(self) -> str:
        """Generates a new temporary email address with API retries and local fallback."""
        for attempt in range(3):
            try:
                response = requests.get(f"{self.api_url}?action=genRandomMailbox&count=1", timeout=10)
                if response.status_code == 200:
                    self.email_address = response.json()[0]
                    self.username, self.domain = self.email_address.split("@")
                    logger.info(f"Generated temp email: {self.email_address}")
                    return self.email_address
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} to generate email failed: {e}")
                time.sleep(2)
        
        # Fallback: 1secmail accepts any random username without pre-registration
        import random
        import string
        random_user = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        self.email_address = f"{random_user}@1secmail.com"
        self.username, self.domain = self.email_address.split("@")
        logger.info(f"Generated fallback temp email offline: {self.email_address}")
        return self.email_address

    def get_messages(self):
        """Fetches all messages in the mailbox."""
        if not self.username or not self.domain:
            return []
        
        try:
            url = f"{self.api_url}?action=getMessages&login={self.username}&domain={self.domain}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching mail messages: {e}")
        return []

    def fetch_email_content(self, mail_id):
        """Fetches detailed content of a specific email by ID."""
        try:
            url = f"{self.api_url}?action=readMessage&login={self.username}&domain={self.domain}&id={mail_id}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching message {mail_id}: {e}")
        return None

    def wait_for_email_matching(self, keyword: str, timeout_seconds: int = 120, check_interval: int = 10):
        """Polls the inbox for an email containing the specified keyword (like OTP or Etihad/Saudia)."""
        logger.info(f"Waiting for email containing '{keyword}'...")
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            messages = self.get_messages()
            for msg in messages:
                # Check subject or sender
                if keyword.lower() in msg.get("subject", "").lower() or keyword.lower() in msg.get("from", "").lower():
                    details = self.fetch_email_content(msg["id"])
                    if details:
                        return details
            time.sleep(check_interval)
        logger.warning(f"Timeout waiting for email containing '{keyword}'")
        return None
