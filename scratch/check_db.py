import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Missing credentials")
    exit()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_users():
    try:
        res = supabase.table("users").select("*").execute()
        print(f"Users found: {res.data}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users()
