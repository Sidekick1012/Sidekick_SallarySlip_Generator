import openpyxl
import os

def get_total_saving_funds(filename="Saving funds.xlsx"):
    """
    Reads the Saving funds.xlsx file and returns a dictionary 
    mapping employee_id to their total saving fund.
    """
    if not os.path.exists(filename):
        print(f"Warning: {filename} not found.")
        return {}

    try:
        wb = openpyxl.load_workbook(filename, data_only=True)
        sheet = wb.active
        mapping = {}
        
        # Based on inspection:
        # Row 1 has headers: ('Employee-ID ', 'Name', 'DOJ', None, 2026, 2025, 2024, None, 'TOTAL')
        # Row 2+ has data. Column 0 is ID, Column 8 is TOTAL.
        
        for i, row in enumerate(sheet.iter_rows(values_only=True)):
            if i < 2: # Skip headers (Row 0 is None, Row 1 is headers)
                continue
            
            emp_id = str(row[0]).strip() if row[0] else None
            total_fund = row[8] if len(row) > 8 else 0
            
            if emp_id and emp_id != 'None':
                try:
                    mapping[emp_id] = float(total_fund) if total_fund is not None else 0.0
                except (ValueError, TypeError):
                    mapping[emp_id] = 0.0
                    
        return mapping
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return {}
