import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_upload():
    test_file = "debug_upload.txt"
    with open(test_file, "w") as f:
        f.write("debug content")
    
    path = "debug/test.txt"
    print(f"Testing upload to 'slips' bucket at {path}...")
    
    try:
        with open(test_file, "rb") as f:
            res = supabase.storage.from_("slips").upload(
                path=path,
                file=f,
                file_options={"content-type": "text/plain", "upsert": True}
            )
        print(f"Upload Result: {res}")
    except Exception as e:
        print(f"Upload Error: {e}")

if __name__ == "__main__":
    test_upload()
    if os.path.exists("debug_upload.txt"):
        os.remove("debug_upload.txt")
