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
            print(f"ID: {user['id']}, Email: {user['email']}, Role: {user['role']}")
    else:
        print("No users found.")

def check_employees():
    print("\nChecking employees table...")
    res = supabase.table("employees").select("id, name, email, is_active").execute()
    if res.data:
        for emp in res.data:
            print(f"ID: {emp['id']}, Name: {emp['name']}, Email: {emp['email']}, Active: {emp.get('is_active')}")
    else:
        print("No employees found.")

if __name__ == "__main__":
    try:
        check_users()
        check_employees()
    except Exception as e:
        print(f"Error: {e}")
