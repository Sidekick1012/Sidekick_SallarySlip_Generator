import os
from supabase import create_client, Client
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask import Flask

load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Check current hash in DB
res = supabase.table("users").select("*").eq("email", "aqib@sidekick.pk").execute()
if res.data:
    user = res.data[0]
    print(f"Email: {user['email']}")
    print(f"Role: {user['role']}")
    print(f"Hash in DB: {user['password_hash']}")
    
    # Verify password against the hash
    test_pass = "Aqib@1012"
    match = bcrypt.check_password_hash(user['password_hash'], test_pass)
    print(f"Password 'Aqib@1012' matches: {match}")
else:
    print("User not found!")
