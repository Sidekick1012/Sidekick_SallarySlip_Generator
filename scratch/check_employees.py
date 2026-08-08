import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.db import supabase

def main():
    try:
        import openpyxl
        wb = openpyxl.load_workbook('Emails.xlsx')
        sheet = wb.active
        excel_rows = list(sheet.iter_rows(values_only=True))
        
        # Build dictionaries from Excel
        excel_by_id = {}
        excel_by_name = {}
        for r in excel_rows:
            emp_id = str(r[0]).strip() if r[0] else None
            name = str(r[1]).strip() if r[1] else None
            email = str(r[4]).strip() if r[4] else None
            if emp_id:
                excel_by_id[emp_id.lower()] = (emp_id, name, email)
            if name:
                excel_by_name[name.lower()] = (emp_id, name, email)
                
        # Fetch DB employees
        res = supabase.table('employees').select('id, employee_id, name, email').execute()
        db_emps = res.data
        
        print(f"Total in DB: {len(db_emps)}")
        print(f"Total in Excel: {len(excel_rows)}")
        
        matched_by_id = []
        matched_by_name_only = []
        unmatched = []
        
        for emp in db_emps:
            db_id = emp['employee_id'].strip().lower()
            db_name = emp['name'].strip().lower()
            
            if db_id in excel_by_id:
                matched_by_id.append((emp, excel_by_id[db_id]))
            elif db_name in excel_by_name:
                matched_by_name_only.append((emp, excel_by_name[db_name]))
            else:
                unmatched.append(emp)
                
        print(f"\nMatched by ID: {len(matched_by_id)}")
        for db, ex in matched_by_id[:10]:
            print(f"  DB ID: {db['employee_id']} ({db['name']}) -> Excel Email: {ex[2]}")
            
        print(f"\nMatched by Name Only: {len(matched_by_name_only)}")
        for db, ex in matched_by_name_only:
            print(f"  DB: {db['employee_id']} ({db['name']}) -> Excel: {ex[0]} ({ex[1]}) -> Excel Email: {ex[2]}")
            
        print(f"\nUnmatched DB Employees: {len(unmatched)}")
        for db in unmatched[:15]:
            print(f"  DB: {db['employee_id']} ({db['name']})")
            
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
