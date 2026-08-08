import sys
import os
import openpyxl

# Add workspace root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.db import supabase, log_activity

def main():
    try:
        import sys
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            
        # Load Emails.xlsx
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
            
            # Clean up email if it has typo or prefix like None
            if email:
                if email.lower().startswith('none'):
                    email = email[4:].strip()
                if email.lower() in ('none', 'null', ''):
                    email = None
            
            if emp_id:
                excel_by_id[emp_id.lower()] = (emp_id, name, email)
            if name:
                excel_by_name[name.lower()] = (emp_id, name, email)
                
        # Fetch DB employees
        res = supabase.table('employees').select('id, employee_id, name, email').execute()
        db_emps = res.data
        
        updates = []
        
        for emp in db_emps:
            db_id = emp['employee_id'].strip().lower()
            db_name = emp['name'].strip().lower()
            db_email = emp['email']
            
            target_email = None
            match_source = None
            
            # Match by ID first
            if db_id in excel_by_id:
                target_email = excel_by_id[db_id][2]
                match_source = f"ID Match ({excel_by_id[db_id][0]})"
            # Then match by Name
            elif db_name in excel_by_name:
                target_email = excel_by_name[db_name][2]
                match_source = f"Name Match ({excel_by_name[db_name][1]})"
                
            # If target email exists in Excel, check if update is needed
            if target_email:
                # Clean db_email for comparison
                cleaned_db_email = db_email.strip() if db_email else None
                
                # Check if it needs update
                needs_update = False
                if not cleaned_db_email:
                    needs_update = True
                elif cleaned_db_email.lower().startswith('none'):
                    needs_update = True
                elif cleaned_db_email.lower() != target_email.lower():
                    needs_update = True
                    
                if needs_update:
                    updates.append({
                        'id': emp['id'],
                        'employee_id': emp['employee_id'],
                        'name': emp['name'],
                        'old_email': db_email,
                        'new_email': target_email,
                        'source': match_source
                    })
                    
        print(f"Total planned updates: {len(updates)}")
        for u in updates:
            print(f"Update: {u['employee_id']} ({u['name']}) | Old: {u['old_email']} -> New: {u['new_email']} (via {u['source']})")
            
        # Execute updates
        if updates:
            print("\nExecuting updates in Supabase...")
            success_count = 0
            for u in updates:
                try:
                    supabase.table('employees').update({'email': u['new_email']}).eq('id', u['id']).execute()
                    print(f"[OK] Updated {u['employee_id']} ({u['name']}) -> {u['new_email']}")
                    success_count += 1
                except Exception as ex:
                    print(f"[FAIL] Failed to update {u['employee_id']}: {ex}")
            
            print(f"\nSuccessfully updated {success_count}/{len(updates)} employees.")
            try:
                log_activity("SYSTEM", "Bulk Email Update", f"Updated emails for {success_count} employees from Emails.xlsx")
            except Exception as e:
                print("Could not log activity:", e)
        else:
            print("\nNo updates needed!")
            
    except Exception as e:
        print("Error during update script run:", e)

if __name__ == '__main__':
    main()
