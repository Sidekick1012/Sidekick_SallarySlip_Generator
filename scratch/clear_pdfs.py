import os
from utils.db import supabase

def clear_pdf_paths():
    if not supabase:
        print("Supabase client not initialized")
        return
    
    try:
        # Update all salary slips to set pdf_path to null
        res = supabase.table("salary_slips").update({"pdf_path": None}).neq("id", 0).execute()
        print(f"Successfully cleared pdf_path for {len(res.data)} slips.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clear_pdf_paths()
