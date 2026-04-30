"""
One-time fix script:
Removes saving_fund from total_deductions and corrects net_salary
for all existing salary slips in Supabase.
"""

from supabase import create_client

SUPABASE_URL = "https://ucuizllfmzbrpvymdmap.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVjdWl6bGxmbXpicnB2eW1kbWFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ4NTY3MzMsImV4cCI6MjA5MDQzMjczM30.tnNTKLPu7ivQbEk2NAC0Rn-A55Wk-c4TGWU4ah-34lA"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fix_slips():
    print("Fetching all salary slips...")
    res = supabase.table("salary_slips").select(
        "id, total_deductions, net_salary, saving_fund"
    ).execute()

    slips = res.data or []
    print(f"Total slips found: {len(slips)}")

    fixed = 0
    skipped = 0

    for slip in slips:
        sf = float(slip.get("saving_fund") or 0)

        if sf <= 0:
            skipped += 1
            continue

        old_ded = float(slip.get("total_deductions") or 0)
        old_net = float(slip.get("net_salary") or 0)

        new_ded = round(old_ded - sf, 2)
        new_net = round(old_net + sf, 2)

        print(f"  Slip ID {slip['id']}: Deductions {old_ded} -> {new_ded} | Net {old_net} -> {new_net}")

        supabase.table("salary_slips").update({
            "total_deductions": new_ded,
            "net_salary":       new_net,
        }).eq("id", slip["id"]).execute()

        fixed += 1

    print(f"\n✅ Done! {fixed} slips fixed, {skipped} skipped (saving_fund = 0).")

if __name__ == "__main__":
    fix_slips()
