import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_users():
    res = supabase.table("users").select("*").execute()
    with open("tmp/db_users.txt", "w") as f:
        if res.data:
            for user in res.data:
                f.write(f"ID: {user['id']}, Email: {user['email']}, Role: {user['role']}, Password Hash: {user['password_hash']}\n")
        else:
            f.write("No users found.\n")

if __name__ == "__main__":
    check_users()
