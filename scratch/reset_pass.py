import os
from supabase import create_client, Client
from flask_bcrypt import Bcrypt
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

email = "aqib@sidekick.pk"
new_password = "Aqib@1012"
hashed = bcrypt.generate_password_hash(new_password).decode("utf-8")

try:
    res = supabase.table("users").update({"password_hash": hashed}).eq("email", email).execute()
    print(f"Password reset success for {email}")
except Exception as e:
    print(f"Error: {e}")
