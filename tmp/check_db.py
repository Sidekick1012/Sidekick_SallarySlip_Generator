import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_users():
    print("Checking users table...")
    res = supabase.table("users").select("*").execute()
    if res.data:
        for user in res.data:
            print(f"ID: {user['id']}, Email: {user['email']}, Role: {user['role']}, Password Hash: {user['password_hash']}")
    else:
        print("No users found.")

if __name__ == "__main__":
    check_users()
