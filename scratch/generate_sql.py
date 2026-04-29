import openpyxl
from datetime import datetime

def generate_sql_from_excel(file_path):
    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb.active
    
    sql_header = "INSERT INTO employees (employee_id, name, designation, department, joining_date, bank_name, iban, cnic, ntn, previous_gross, increment, new_gross_monthly, basic_salary, medical_allowance, dearness_allowance, house_allowance, transport_allowance, cola_allowance, utility_allowance, bonus_allowance, income_tax, eobi_deduction, is_active) VALUES \n"
    
    rows_sql = []
    
    for row in list(sheet.rows)[2:]:
        emp_id = row[1].value
        if not emp_id or str(emp_id).strip() == "":
            continue
            
        def clean_float(val):
            if val is None or str(val).strip() in ["-", "", "#"]:
                return 0.0
            try:
                # Handle cases where value might be a string with commas or spaces
                s_val = str(val).replace(",", "").strip()
                return float(s_val) if s_val else 0.0
            except:
                return 0.0

        def clean_date(val):
            if isinstance(val, datetime):
                return f"'{val.strftime('%Y-%m-%d')}'"
            if val:
                return f"'{str(val).strip()}'"
            return "'2024-01-01'"

        def clean_str(val):
            if val is None:
                return "NULL"
            s = str(val).replace("'", "''").strip()
            return f"'{s}'"

        name = clean_str(row[2].value)
        joining_date = clean_date(row[3].value)
        bank_name = clean_str(row[5].value)
        iban = clean_str(row[6].value)
        cnic = clean_str(row[7].value)
        ntn = clean_str(row[8].value)
        
        vals = (
            f"({clean_str(emp_id)}, {name}, 'Employee', 'Operations', {joining_date}, "
            f"{bank_name}, {iban}, {cnic}, {ntn}, {clean_float(row[9].value)}, "
            f"{clean_float(row[10].value)}, {clean_float(row[11].value)}, {clean_float(row[14].value)}, "
            f"{clean_float(row[15].value)}, {clean_float(row[16].value)}, {clean_float(row[17].value)}, "
            f"{clean_float(row[18].value)}, {clean_float(row[19].value)}, {clean_float(row[20].value)}, "
            f"{clean_float(row[21].value)}, {clean_float(row[30].value)}, {clean_float(row[32].value)}, true)"
        )
        rows_sql.append(vals)

    full_sql = sql_header + ",\n".join(rows_sql) + ";"
    
    with open("employees_import.sql", "w", encoding="utf-8") as f:
        f.write(full_sql)
    
    print(f"Generated SQL for {len(rows_sql)} employees in employees_import.sql")

if __name__ == "__main__":
    generate_sql_from_excel("Daci emp.xlsx")
