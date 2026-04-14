import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def test_email():
    email = os.getenv("MAIL_EMAIL")
    password = os.getenv("MAIL_PASSWORD", "").replace(" ", "")
    
    print(f"Connecting with: {email}")
    print(f"Password length: {len(password)}")
    
    msg = EmailMessage()
    msg.set_content("Testing Sidekick Payroll Email Configuration")
    msg['Subject'] = 'Test Email'
    msg['From'] = email
    msg['To'] = email # Sending to self

    try:
        # Try Port 465 (SSL)
        print("Attempting connection on Port 465 (SSL)...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email, password)
            smtp.send_message(msg)
        print("SUCCESS: Connection on Port 465 worked!")
        return
    except Exception as e:
        print(f"FAILED: Port 465 failed with error: {e}")

    try:
        # Try Port 587 (TLS)
        print("\nAttempting connection on Port 587 (TLS)...")
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(email, password)
            smtp.send_message(msg)
        print("SUCCESS: Connection on Port 587 worked!")
    except Exception as e:
        print(f"FAILED: Port 587 failed with error: {e}")

if __name__ == "__main__":
    test_email()
