import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def test_email():
    email_address = os.getenv("MAIL_EMAIL")
    email_password = os.getenv("MAIL_PASSWORD")
    
    print(f"Testing with: {email_address}")
    
    msg = EmailMessage()
    msg['Subject'] = "Sidekick Test Email"
    msg['From'] = email_address
    msg['To'] = email_address  # Send to self
    msg.set_content("This is a test email to verify SMTP settings.")
    
    try:
        print("Connecting to smtp.gmail.com:587...")
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.set_debuglevel(1)
            smtp.starttls()
            print("Logging in...")
            smtp.login(email_address, email_password)
            print("Sending email...")
            smtp.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print(f"FAILED to send email: {e}")

if __name__ == "__main__":
    test_email()
