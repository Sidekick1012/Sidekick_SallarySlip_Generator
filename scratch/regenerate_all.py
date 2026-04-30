import os
import sys
from datetime import datetime
sys.path.append(os.getcwd())
from utils.db import supabase, get_employee_by_id
from app import generate_and_upload_slip, get_total_saving_funds

def regenerate_all_for_period(month, year):
    print(f"Regenerating all slips for {month}/{year}...")
    try:
        res = supabase.table("salary_slips").select("*").eq("month", month).eq("year", year).execute()
        slips = res.data or []
        saving_funds_map = get_total_saving_funds()

        for slip in slips:
            emp = get_employee_by_id(slip['employee_id'])
            if not emp: continue
            
            saving_data = saving_funds_map.get(str(emp.get("employee_id")).upper(), {"2026": 0, "total": 0})
            slip_data = slip.copy()
            slip_data["saving_fund"] = saving_data.get("2026", 0)
            slip_data["total_saving_fund"] = saving_data.get("total", 0)
            
            pdf_path = generate_and_upload_slip(slip_data, emp)
            if pdf_path:
                supabase.table("salary_slips").update({"pdf_path": pdf_path}).eq("id", slip["id"]).execute()
        print(f"Finished {month}/{year}")
    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    regenerate_all_for_period(3, 2026)
    regenerate_all_for_period(4, 2026)
