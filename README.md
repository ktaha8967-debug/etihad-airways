# Airline Passenger Data & Saudia Membership Automation

A premium, production-grade Python automation script designed to extract passenger details from **Etihad Airways** and register membership accounts on **Saudia Airlines (AlFursan)**.

---

## 🚀 Features

* **Smart Etihad Web Scraper**: Accesses the Etihad Manage Booking portal using PNR and passenger Last Name, bypassing skeleton loading overlays.
* **Frequent Flyer Detection**: Automatically checks if a passenger already has a loyalty or frequent flyer program attached, skipping them to avoid double registration.
* **Offline Email Fallback**: Automatically creates unique, valid email addresses that route emails to the specified temporary mailbox domains, with network failure fallback protection.
* **Semi-Automated CAPTCHA Evasion**: Detects hCaptcha / Cloudflare security block screens on the Saudia website, alerts the operator, and pauses the script for up to 120 seconds to allow manual completion before autofilling passenger fields.
* **Excel Data Integration**: Dynamically reads input files (cleans header offsets in passenger files) and saves updated records (membership details, password, remarks) back to the Excel sheets.

---

## 📁 Project Structure

```
etihad-airways/
│
├── src/
│   ├── __init__.py
│   ├── config.py            # Endpoints, timeouts, and env settings
│   ├── utils.py             # Excel parsers, random generators, logging setup
│   ├── temp_mail.py         # 1secmail API wrapper with retry fallbacks
│   ├── etihad_scraper.py    # Playwright code to log in, filter, and extract details
│   └── saudia_signup.py     # Playwright code for Saudia AlFursan registrations
│
├── main.py                  # Orchestrator running the end-to-end execution loop
├── test_etihad.py           # Verification script for Etihad scraping
├── test_saudia.py           # Verification script for Saudia signup
├── requirements.txt         # Required Python packages
├── .env                     # Local runtime configuration
└── README.md                # Documentation
```

---

## 🛠️ Setup Instructions

### 1. Install Dependencies
Make sure Python 3.10+ is installed, then run:
```powershell
pip install -r requirements.txt
python -m playwright install chromium
```

### 2. Configure Environment Variables
Verify or edit the `.env` file settings:
```ini
INPUT_EXCEL_PATH=Etihad passenger details 9th Aug.xlsx
OUTPUT_EXCEL_PATH=Etihad passenger details 9th Aug_Processed.xlsx
HEADLESS=false
TIMEOUT=45000
```

---

## 🏃 Execution

### Run End-to-End Automation Loop
To run the main loop that processes all passengers sequentially:
```powershell
python main.py
```

### Run Scraper Unit Tests
To test Etihad scraping only:
```powershell
python test_etihad.py
```

To test Saudia registration only:
```powershell
python test_saudia.py
```

---

## ⚠️ Semi-Automated CAPTCHA Verification
Saudia Airlines uses **Cloudflare / hCaptcha** to prevent automated bot signups. When a security check is detected:
1. The console will print: `[WARNING] CAPTCHA / Cloudflare Security Check detected! Please resolve the CAPTCHA in the browser window to continue...`
2. The browser window will remain open for **120 seconds**.
3. **Manually click the "I am human" checkbox** in the browser window.
4. Once solved, the script will automatically resume filling the traveler's details!
