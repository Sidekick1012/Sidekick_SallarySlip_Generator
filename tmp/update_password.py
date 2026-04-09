import os
from supabase import create_client, Client
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask import Flask

app = Flask(__name__)
bcrypt = Bcrypt(app)
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def update_password():
    email = "aqib@sidekick.pk"
    new_password = "Aqib@1012"
    
    # Generate new hash
    hashed = bcrypt.generate_password_hash(new_password).decode("utf-8")
    
    # Update in DB
    res = supabase.table("users").update({"password_hash": hashed}).eq("email", email).execute()
    print("Password updated successfully to 'Aqib@1012'")

if __name__ == "__main__":
    update_password()
