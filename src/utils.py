import os
import logging
import pandas as pd

def setup_logging():
    """Sets up standard logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("automation.log", encoding="utf-8")
        ]
    )

def read_excel_data(file_path: str) -> pd.DataFrame:
    """Reads input Excel booking data and returns a cleaned DataFrame."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found at: {file_path}")
    
    try:
        df = pd.read_excel(file_path)
        
        # If headers are shifted (e.g. 'Unnamed: 1' is 'Last Name' in row 0)
        if any("Unnamed:" in str(col) for col in df.columns):
            # Check if row 0 has the actual headers
            row0 = df.iloc[0].astype(str).str.strip().tolist()
            if "Last Name" in row0 or "PNR" in row0:
                # Set columns to row 0 values
                df.columns = df.iloc[0]
                df = df[1:].reset_index(drop=True)
        
        # Clean column names
        df.columns = [str(c).strip() for c in df.columns]
        
        # Strip string values
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        logging.error(f"Error reading excel file {file_path}: {e}")
        raise

def save_excel_data(df: pd.DataFrame, file_path: str):
    """Saves the DataFrame back to Excel."""
    try:
        df.to_excel(file_path, index=False)
        logging.info(f"Successfully saved data to {file_path}")
    except Exception as e:
        logging.error(f"Error saving excel file {file_path}: {e}")
        raise

def generate_random_passport() -> str:
    """Generates a random passport number format (1 letter + 7 digits)."""
    import random
    import string
    letter = random.choice(string.ascii_uppercase)
    digits = "".join(random.choices(string.digits, k=7))
    return f"{letter}{digits}"

def generate_random_dob() -> str:
    """Generates a random date of birth (DD/MM/YYYY) for adults aged 22-55."""
    import random
    from datetime import datetime, timedelta
    start_date = datetime.now() - timedelta(days=55*365)
    end_date = datetime.now() - timedelta(days=22*365)
    random_days = random.randint(0, (end_date - start_date).days)
    dob = start_date + timedelta(days=random_days)
    return dob.strftime("%d/%m/%Y")

def generate_random_mobile() -> str:
    """Generates a random 10-digit mobile number starting with 9, 8 or 7."""
    import random
    prefix = random.choice(["7", "8", "9"])
    digits = "".join(random.choices(string.digits if 'string' in globals() else "0123456789", k=9))
    return f"{prefix}{digits}"

def generate_gmail_alias(base_email: str, index: int) -> str:
    """
    Generates a unique email alias using Gmail's dot-aliasing or plus-addressing.
    If it's not a Gmail address, defaults to plus-addressing (+index).
    """
    if "@" not in base_email:
        return base_email
        
    username, domain = base_email.split("@")
    
    if "gmail.com" not in domain.lower():
        # Standard plus-addressing for compatible mail servers
        return f"{username}+{index}@{domain}"
    
    # Clean any existing dots or pluses to get clean base username
    base_user = username.split("+")[0].replace(".", "")
    
    # Generate dot alias based on binary representation of index
    chars = list(base_user)
    if len(chars) <= 1:
        return f"{base_user}+{index}@{domain}"
        
    result = []
    # Maximum dots we can insert is len(chars) - 1
    # Use index to decide where to insert dots
    for i in range(len(chars) - 1):
        result.append(chars[i])
        if (index >> i) & 1:
            result.append(".")
    result.append(chars[-1])
    return "".join(result) + "@" + domain

