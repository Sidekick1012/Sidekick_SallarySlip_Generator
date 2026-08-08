"""
Quick diagnostic: test if SMTP email sending works.
Run:  python scratch/test_email_send.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

server_host = os.getenv("MAIL_SERVER", "smtp.titan.email")
server_port = int(os.getenv("MAIL_PORT", "465"))
username    = os.getenv("MAIL_USERNAME", "info@sidekick.pk")
password    = os.getenv("MAIL_PASSWORD", "")
sender_name = os.getenv("SENDER_NAME", "Team Sidekick")

print("=" * 55)
print("  EMAIL DIAGNOSTIC")
print("=" * 55)
print(f"  Server   : {server_host}:{server_port}")
print(f"  Username : {username}")
print(f"  Password : {'*' * len(password)} ({len(password)} chars)")
print(f"  Sender   : {sender_name}")
print(f"  SSL      : {os.getenv('MAIL_USE_SSL', 'True')}")
print(f"  TLS      : {os.getenv('MAIL_USE_TLS', 'False')}")
print("=" * 55)

# --- Step 1: Connect ---
print("\n[1/3] Connecting to SMTP server...")
try:
    server = smtplib.SMTP_SSL(server_host, server_port, timeout=15)
    print("  ✅ Connected successfully")
except Exception as e:
    print(f"  ❌ Connection failed: {e}")
    sys.exit(1)

# --- Step 2: Login ---
print("[2/3] Authenticating...")
try:
    server.login(username, password)
    print("  ✅ Login successful")
except Exception as e:
    print(f"  ❌ Login failed: {e}")
    server.quit()
    sys.exit(1)

# --- Step 3: Send test email ---
recipient = os.getenv("ADMIN_EMAIL", "info@sidekick.pk")
print(f"[3/3] Sending test email to {recipient}...")
try:
    msg = MIMEMultipart()
    msg["From"]    = f"{sender_name} <{username}>"
    msg["To"]      = recipient
    msg["Subject"] = "Sidekick Payroll — SMTP Test"
    msg.attach(MIMEText("<h3>Test Email</h3><p>SMTP connection is working!</p>", "html"))
    server.sendmail(username, recipient, msg.as_string())
    print("  ✅ Email sent successfully!")
except Exception as e:
    print(f"  ❌ Send failed: {e}")

server.quit()
print("\nDone.")
