import os
from utils.db import get_salary_slips, download_pdf_from_supabase, supabase

def test():
    slips = get_salary_slips()
    if slips:
        print(f"Found {len(slips)} slips")
        for slip in slips:
            path = slip.get("pdf_path")
            if path:
                print(f"Testing slip {slip['id']} with path {path}")
                content = download_pdf_from_supabase(path)
                print(f"Downloaded content type: {type(content)}")
                break
    else:
        print("No slips found")

if __name__ == "__main__":
    test()
