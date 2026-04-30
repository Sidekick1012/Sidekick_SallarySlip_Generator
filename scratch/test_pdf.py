import os
import sys
sys.path.append(os.getcwd())
from utils.pdf_generator import generate_salary_slip_pdf
from utils.excel_reader import get_total_saving_funds

def test_generation():
    # Mock data for Foaad Ahmad
    emp = {
        'employee_id': 'DACIPK-0001',
        'name': 'Foaad Ahmad',
        'designation': 'Director / Electrical Design Manager',
        'cnic': '13302-4780813-1'
    }
    
    saving_funds_map = get_total_saving_funds()
    total_saving_fund = saving_funds_map.get(emp['employee_id'], 0)
    
    slip_data = {
        'month': 4,
        'year': 2026,
        'basic_salary': 176400,
        'gross_salary': 392000,
        'net_salary': 328881,
        'saving_fund': 10000, # Monthly
        'total_saving_fund': total_saving_fund,
        'total_deductions': 63119,
        'note': 'Testing total saving fund display'
    }
    
    output_dir = "scratch/test_slips"
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = generate_salary_slip_pdf(slip_data, emp, output_dir=output_dir)
    print(f"Generated PDF at: {pdf_path}")
    print(f"Total Saving Fund found: {total_saving_fund}")

if __name__ == "__main__":
    test_generation()
