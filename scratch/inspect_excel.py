import openpyxl

def inspect_excel(file_path):
    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb.active
    
    print(f"Sheet Name: {sheet.title}")
    print(f"Max Row: {sheet.max_row}")
    print(f"Max Col: {sheet.max_column}")
    
    # Read first 5 rows
    for row in list(sheet.rows)[:5]:
        print([cell.value for cell in row])

if __name__ == "__main__":
    inspect_excel("Daci emp.xlsx")
