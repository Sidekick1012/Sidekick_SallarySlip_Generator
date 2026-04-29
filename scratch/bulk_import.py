import openpyxl
from utils.db import add_employee, supabase
from datetime import datetime

def import_employees_from_excel(file_path):
    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb.active
    
    # Headers are on row 2 (index 1)
    # Data starts from row 3 (index 2)
    
    added_count = 0
    errors = []
    
    for row in list(sheet.rows)[2:]:
        # row is a tuple of cells
        # Check if Employee ID exists
        emp_id = row[1].value
        if not emp_id or str(emp_id).strip() == "":
            continue
            
        try:
            # Map values
            def clean_float(val):
                if val is None or str(val).strip() in ["-", "", "#"]:
                    return 0.0
                try:
                    return float(val)
                except:
                    return 0.0

            def clean_date(val):
                if isinstance(val, datetime):
                    return val.strftime("%Y-%m-%d")
                return val if val else None

            data = {
                "employee_id":          str(emp_id).strip(),
                "name":                 str(row[2].value).strip(),
                "designation":          "Employee",  # Default
                "department":           "Operations", # Default
                "joining_date":         clean_date(row[3].value) or "2024-01-01",
                "date_of_leaving":      clean_date(row[4].value),
                "bank_name":            str(row[5].value or "").strip(),
                "iban":                 str(row[6].value or "").strip(),
                "cnic":                 str(row[7].value or "").strip(),
                "ntn":                  str(row[8].value or "").strip(),
                "previous_gross":       clean_float(row[9].value),
                "increment":            clean_float(row[10].value),
                "new_gross_monthly":    clean_float(row[11].value),
                "basic_salary":         clean_float(row[14].value),
                "medical_allowance":     clean_float(row[15].value),
                "dearness_allowance":    clean_float(row[16].value),
                "house_allowance":       clean_float(row[17].value),
                "transport_allowance":   clean_float(row[18].value),
                "cola_allowance":        clean_float(row[19].value),
                "utility_allowance":     clean_float(row[20].value),
                "bonus_allowance":       clean_float(row[21].value),
                "income_tax":           clean_float(row[30].value),
                "eobi_deduction":       clean_float(row[32].value),
                "is_active":            True
            }
            
            # Check if employee already exists by employee_id
            existing = supabase.table("employees").select("id").eq("employee_id", data["employee_id"]).execute()
            if existing.data:
                print(f"Skipping {data['employee_id']} (Already exists)")
                continue

            add_employee(data)
            added_count += 1
            print(f"Added: {data['name']} ({data['employee_id']})")
        except Exception as e:
            errors.append(f"Error adding {emp_id}: {str(e)}")
            print(f"Error adding {emp_id}: {str(e)}")

    print(f"Total Added: {added_count}")
    if errors:
        print(f"Errors encountered: {len(errors)}")

if __name__ == "__main__":
    import_employees_from_excel("Daci emp.xlsx")
