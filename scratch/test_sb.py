import os
from supabase import create_client

def test():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        print("No URL or KEY")
        return
    sb = create_client(url, key)
    res = sb.storage.from_("slips").download("test.pdf")
    print("Type:", type(res))

if __name__ == "__main__":
    test()
