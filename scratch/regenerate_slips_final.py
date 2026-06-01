import os
import sys
from datetime import datetime

# Add current workspace to path
sys.path.append(os.getcwd())

from utils.db import supabase, upload_pdf_to_supabase
from utils.pdf_generator import generate_salary_slip_pdf

def get_employee_map():
    res = supabase.table("employees").select("id, employee_id, name, designation, cnic, bank_name, iban").execute()
    return {emp['id']: emp for emp in res.data}

def regenerate_all():
    print("Fetching employees from DB...")
    emp_map = get_employee_map()
    print(f"Loaded {len(emp_map)} employees.")

    print("Fetching all salary slips for April 2026 and May 2026...")
    res = supabase.table("salary_slips").select("*").eq("year", 2026).in_("month", [4, 5]).execute()
    slips = res.data or []
    print(f"Loaded {len(slips)} slips to regenerate.")

    success_count = 0
    error_count = 0

    for slip in slips:
        emp_id_db = slip.get("employee_id")
        emp = emp_map.get(emp_id_db)
        if not emp:
            print(f"[SKIP] Employee ID {emp_id_db} not found in DB map for slip ID {slip['id']}")
            continue

        emp_id_raw = emp['employee_id'].strip()
        month = slip.get("month")
        year = slip.get("year")
        saving_fund = slip.get("saving_fund", 0)

        # Regenerate slip data
        slip_data = slip.copy()
        
        # In case total_saving_fund is present in dict, we delete it so it forces using saving_fund
        slip_data.pop("total_saving_fund", None)

        try:
            # Generate locally
            local_path = generate_salary_slip_pdf(slip_data, emp)
            if not local_path or not os.path.exists(local_path):
                raise Exception(f"PDF failed to generate locally.")

            # Upload to Storage
            filename = os.path.basename(local_path)
            storage_path = f"{emp_id_raw}/{filename}"
            upload_res = upload_pdf_to_supabase(local_path, storage_path)
            
            if upload_res:
                # Remove local file
                os.remove(local_path)
                
                # Update DB record with correct pdf_path
                supabase.table("salary_slips").update({"pdf_path": storage_path}).eq("id", slip["id"]).execute()
                print(f"[OK] Slip ID {slip['id']} for {emp['name']} ({month}/{year}) | SF: {saving_fund} | PDF uploaded.")
                success_count += 1
            else:
                raise Exception("Upload to Supabase Storage failed.")

        except Exception as e:
            print(f"[ERROR] Slip ID {slip['id']} for {emp['name']} failed: {e}")
            error_count += 1

    print(f"\nFinal Summary: {success_count} succeeded, {error_count} failed.")

if __name__ == "__main__":
    regenerate_all()
