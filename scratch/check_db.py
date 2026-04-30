import os
import sys
sys.path.append(os.getcwd())
from utils.db import supabase

def check_salah():
    try:
        res = supabase.table("employees").select("*").ilike("name", "%Salah%").execute()
        print(res.data)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_salah()
