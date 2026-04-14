import os
from supabase import create_client, Client
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask import Flask

load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)

def reset_password(email, new_password):
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    hashed = bcrypt.generate_password_hash(new_password).decode("utf-8")
    
    print(f"Resetting password for {email}...")
    res = supabase.table("users").update({"password_hash": hashed}).eq("email", email).execute()
    
    if res.data:
        print(f"SUCCESS: Password reset for {email}!")
    else:
        print(f"FAILED: Could not find user with email {email}")

if __name__ == "__main__":
    reset_password("aqib@sidekick.pk", "Aqib@1012")
