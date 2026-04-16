import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def clear_bucket():
    bucket = "slips"
    print(f"Checking bucket '{bucket}'...")
    
    try:
        # Step 1: List all top-level items (folders or files)
        res = supabase.storage.from_(bucket).list()
        
        if not res:
            print("Bucket is already empty.")
            return

        for item in res:
            name = item['name']
            
            # Step 2: Check if it's a folder by trying to list its content
            # (In Supabase, folders are just prefixes)
            sub_res = supabase.storage.from_(bucket).list(name)
            
            if sub_res:
                # It's a folder, delete its contents first
                files_to_remove = [f"{name}/{f['name']}" for f in sub_res]
                print(f"Deleting {len(files_to_remove)} files from folder '{name}'...")
                supabase.storage.from_(bucket).remove(files_to_remove)
            
            # Step 3: Remove the item/folder prefix itself
            supabase.storage.from_(bucket).remove([name])
            print(f"Successfully removed: {name}")

        print("\n✅ All slips/folders cleared from Supabase Storage.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    confirm = input("Are you sure you want to delete ALL files from 'slips' bucket? (y/n): ")
    if confirm.lower() == 'y':
        clear_bucket()
    else:
        print("Cleanup cancelled.")
