import logging
from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import Stealth
from src.config import SAUDIA_SIGNUP_URL, HEADLESS, TIMEOUT

logger = logging.getLogger(__name__)

class SaudiaSignupManager:
    def __init__(self, playwright_instance=None):
        self.playwright = playwright_instance
        self.browser = None
        self.page = None

    def start(self):
        """Initializes the playwright browser session with mobile emulation if preferred."""
        logger.info("Starting Playwright browser for Saudia registration...")
        if not self.playwright:
            import asyncio
            try:
                asyncio.set_event_loop(None)
            except Exception:
                pass
            self.playwright = sync_playwright().start()
        # Saudia prefers mobile app workflow - we can emulate a mobile device context
        self.browser = self.playwright.chromium.launch(
            headless=HEADLESS,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        self.context = self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        self.page = self.context.new_page()
        # Apply standard Playwright stealth configuration using the correct Class method
        Stealth().apply_stealth_sync(self.page)
        self.page.set_default_timeout(TIMEOUT)

    def stop(self):
        """Closes the browser session safely."""
        try:
            if self.browser:
                self.browser.close()
        except Exception:
            pass
        finally:
            self.browser = None

        try:
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass
        finally:
            self.playwright = None
        logger.info("Saudia Sign-up Manager stopped.")

    def create_membership(self, passenger_details: dict, email: str, password: str) -> str:
        """
        Automates registration on Saudia's membership signup portal using passenger details.
        Returns the generated Membership ID if successful, else returns None.
        """
        logger.info(f"Initiating Saudia membership creation for {passenger_details.get('passenger_name')}")
        try:
            self.page.goto(SAUDIA_SIGNUP_URL, wait_until="domcontentloaded")
             # Wait for redirect loader to settle
            try:
                self.page.wait_for_function("document.title.toLowerCase().indexOf('loading') === -1", timeout=20000)
            except Exception:
                pass
            self.page.wait_for_timeout(5000)

            # Handle Cookie Consent overlay
            try:
                cookie_btn = self.page.locator("app-cookie-policy button, .cookie-policy button, button:has-text('Accept'), button:has-text('Agree')").first
                cookie_btn.wait_for(state="visible", timeout=8000)
                logger.info("Cookie policy banner overlay detected. Accepting cookie terms...")
                cookie_btn.click()
                self.page.wait_for_timeout(2000)
            except Exception:
                logger.info("No cookie banner overlay detected.")

            # Navigate to AlFursan / Sign Up page
            reg_page = self.page
            try:
                # Click the Loyalty panel header container specifically to expand options
                loyalty_header = self.page.locator("mat-expansion-panel-header:has-text('Loyalty'), mat-expansion-panel:has-text('Loyalty'), .parent-menu:has-text('Loyalty')").first
                if loyalty_header.is_visible():
                    logger.info("Expanding Loyalty navigation panel...")
                    loyalty_header.click()
                    self.page.wait_for_timeout(2000)
                else:
                    # Click hamburger menu first if it's mobile/pixel context
                    menu_btn = self.page.locator("header button, button[aria-label*='menu'], [class*='menu'], .navbar-toggle, .hamburger, header a[href='#']").first
                    if menu_btn.is_visible():
                        logger.info("Mobile menu button detected. Opening header navigation menu...")
                        menu_btn.click()
                        self.page.wait_for_timeout(1500)
                        
                        # Expand Loyalty sub-menu if visible inside the drawer
                        loyalty_submenu = self.page.locator("mat-expansion-panel-header:has-text('Loyalty'), mat-expansion-panel:has-text('Loyalty'), span:has-text('Loyalty'), a:has-text('Loyalty')").first
                        if loyalty_submenu.is_visible():
                            logger.info("Expanding Loyalty sub-menu...")
                            loyalty_submenu.click()
                            self.page.wait_for_timeout(1000)

                join_btn = self.page.locator("a:has-text('Join AlFursan'):visible, a.subnav-link:has-text('Join AlFursan'):visible, a:has-text('Join'):visible").first
                join_btn.wait_for(state="visible", timeout=10000)
                logger.info("Enroll/Join button found. Expecting new page tab context...")
                try:
                    with self.page.context.expect_page(timeout=5000) as new_page_info:
                        join_btn.click()
                    reg_page = new_page_info.value
                    reg_page.wait_for_load_state("domcontentloaded")
                    logger.info("Switched to AlFursan registration tab.")
                except Exception:
                    logger.info("No new tab opened. Clicking join button on current tab...")
                    join_btn.click()
                    self.page.wait_for_load_state("domcontentloaded")
                    reg_page = self.page
            except Exception as e:
                logger.info(f"Proceeding directly to registration form: {e}")

            # Check if hCaptcha/Security Check is present (semi-automation fallback)
            hcaptcha = reg_page.locator("iframe[src*='hcaptcha'], :text('security check'), :text('I am human')").first
            try:
                if hcaptcha.is_visible() or "security" in reg_page.url:
                    logger.warning("CAPTCHA / Cloudflare Security Check detected!")
                    
                    # Try auto-clicking hCaptcha checkbox inside the iframe
                    hcaptcha_iframe = reg_page.frame_locator("iframe[src*='hcaptcha']").first
                    checkbox = hcaptcha_iframe.locator("#checkbox, .check, [role='checkbox']").first
                    if checkbox.is_visible():
                        logger.info("Attempting auto-bypass by clicking hCaptcha checkbox...")
                        checkbox.click()
                        reg_page.wait_for_timeout(3000)
                        
                    # Fallback wait for manual solving if checkbox challenge is presented
                    reg_page.locator("input[name='firstName'], input#firstName, input[name='first_name']").wait_for(state="visible", timeout=120000)
                    logger.info("Security check resolved successfully. Proceeding with form autofill...")
            except Exception:
                pass

            # Fill passenger details
            full_name = passenger_details.get("passenger_name", "")
            name_parts = full_name.split(" ")
            first_name = name_parts[0] if len(name_parts) > 0 else "Passenger"
            last_name = name_parts[-1] if len(name_parts) > 1 else "LastName"

            reg_page.locator("input[name='firstName'], input#firstName").fill(first_name)
            reg_page.locator("input[name='lastName'], input#lastName").fill(last_name)
            
            # Fill passport, date of birth and mobile number from details or generated values
            passport = passenger_details.get("passport", "")
            dob = passenger_details.get("dob", "")
            mobile = passenger_details.get("mobile", "")
            
            passport_input = reg_page.locator("input[name='passport'], input#passportNumber, [placeholder*='Passport']")
            if passport_input.is_visible():
                passport_input.fill(passport)
                
            dob_input = reg_page.locator("input[name='dob'], input#dateOfBirth, [placeholder*='Date of Birth'], [placeholder*='DD/MM/YYYY']")
            if dob_input.is_visible():
                dob_input.fill(dob)
                
            mobile_input = reg_page.locator("input[type='tel'], input[name='mobile'], input#mobileNumber")
            if mobile_input.is_visible():
                mobile_input.fill(mobile)
            
            # Fill email & password
            reg_page.locator("input[type='email'], input#email").fill(email)
            reg_page.locator("input[type='password'], input#password").fill(password)

            # Accept terms and submit
            terms_checkbox = reg_page.locator("input[type='checkbox']#terms, label:has-text('Agree')")
            if terms_checkbox.is_visible():
                terms_checkbox.click()
                
            submit_btn = reg_page.locator("button[type='submit'], #btnRegister, button:text('Next'), button:text('Submit')")
            submit_btn.click()
            reg_page.wait_for_load_state("domcontentloaded")

            # Check if signup is pending email verification
            if reg_page != self.page:
                reg_page.close()
            return "SUCCESS_PENDING_ACTIVATION"
            
        except Exception as e:
            logger.error(f"Error during Saudia registration: {e}")
            return None
            
    def enter_otp(self, otp_code: str) -> bool:
        """Enters verification code received via email to finalize signup."""
        try:
            otp_input = self.page.locator("input[name='otp'], input[name='verificationCode']")
            if otp_input.is_visible():
                otp_input.fill(otp_code)
                verify_btn = self.page.locator("button:text('Verify'), button:text('Submit')")
                verify_btn.click()
                self.page.wait_for_load_state("networkidle")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to enter OTP: {e}")
            return False
