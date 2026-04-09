import os
import sys
from datetime import datetime

# Add parent dir to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import supabase, add_employee

employees = [
    {"employee_id": "DACIPK-0001", "name": "Foaad Ahmed", "designation": "Director / Electrical Design Manager", "previous_gross": 392000},
    {"employee_id": "DACIPK-0002", "name": "Waleed Kazmi", "designation": "Deputy Director / Senior Electrical / Multi Utility Design Engineer", "previous_gross": 354000},
    {"employee_id": "DACIPK-0003", "name": "Umer Naseer", "designation": "Electrical Design Engineer / Team L", "previous_gross": 337692},
    {"employee_id": "DACIPK-0004", "name": "Zahra Javed", "designation": "Multi Utility Design Engineer / Team lead", "previous_gross": 231450},
    {"employee_id": "DACIPK-0005", "name": "Furqan Ahmed Chishti", "designation": "Deputy Director / Senior Electrical Design Engineer", "previous_gross": 354000},
    {"employee_id": "DACIPK-0006", "name": "Yousaf Sardar Gill", "designation": "Electrical Design Engineer / Team L", "previous_gross": 233667},
    {"employee_id": "DACIPK-0008", "name": "Mashhood Ahmad Qureshi", "designation": "Multi Utility Design Engineer / Team", "previous_gross": 164000},
    {"employee_id": "DACIPK-0009", "name": "Mubashra Zareen", "designation": "Multi Utility Design Engineer", "previous_gross": 260933},
    {"employee_id": "DACIPK-0011", "name": "Abdullah Saad", "designation": "Electrical Design Engineer", "previous_gross": 242000},
    {"employee_id": "DACIPK-0012", "name": "Muhammad Waleed Wajdan K", "designation": "Electrical Design Engineer / Team L", "previous_gross": 211500},
    {"employee_id": "DACIPK-0013", "name": "Zain Ul Abideen", "designation": "Senior CAD Engineer", "previous_gross": 350000},
    {"employee_id": "DACIPK-0016", "name": "Ali Atif", "designation": "CAD Engineer", "previous_gross": 122075},
    {"employee_id": "DACIPK-0018", "name": "Zunaira Bibi", "designation": "Office Manager", "previous_gross": 164730},
    {"employee_id": "DACIPK-0020", "name": "Maryam Asif", "designation": "Graduate Design Engineer", "previous_gross": 205485},
    {"employee_id": "DACIPK-0021", "name": "Shahab khan", "designation": "Electrical Design Engineer", "previous_gross": 250000},
    {"employee_id": "DACIPK-0022", "name": "Arslan Ahmed", "designation": "Electrical Design Engineer", "previous_gross": 300000},
    {"employee_id": "DACIPK-0025", "name": "Haseeb Ahmad", "designation": "Graduate Design Engineer", "previous_gross": 205485},
    {"employee_id": "DACIPK-0028", "name": "Muhammad Jibran Khan Jamil", "designation": "Graduate Design Engineer", "previous_gross": 205485},
    {"employee_id": "DACIPK-0029", "name": "Nayyera Naeem", "designation": "Graduate Design Engineer", "previous_gross": 205485},
    {"employee_id": "DACIPK-0031", "name": "Muhammad Salah u din Satti", "designation": "Graduate Design Engineer", "previous_gross": 205485},
    {"employee_id": "DACIPK-0032", "name": "Abdul Mohamin Hashmi", "designation": "Graduate Design Engineer", "previous_gross": 205485},
    {"employee_id": "DACIPK-0033", "name": "Atif Zahoor", "designation": "Electrical Design Engineer", "previous_gross": 250000},
    {"employee_id": "DACIPK-0035", "name": "Fawad Waheed", "designation": "Marketing Assistant", "previous_gross": 205485},
    {"employee_id": "DACIPK-0036", "name": "Muhammad Ahmad Khan", "designation": "Project Coordinator", "previous_gross": 225000},
    {"employee_id": "DACIPK-0037", "name": "Muhammad Shahid Ayub", "designation": "CAD Technician", "previous_gross": 165000},
    {"employee_id": "DACIPK-0038", "name": "Izza Hashmi", "designation": "Electrical Design Engineer / Team Lead", "previous_gross": 220000},
    {"employee_id": "DACIPK-0039", "name": "Muhammad Ali", "designation": "CAD Engineer", "previous_gross": 122075},
    {"employee_id": "DACIPK-0040", "name": "Hamza Amjad Abbasi", "designation": "CAD Engineer", "previous_gross": 150000},
    {"employee_id": "DACIPK-0041", "name": "Kashif ullah", "designation": "Graduate Design Engineer", "previous_gross": 165000},
    {"employee_id": "DACIPK-0042", "name": "Taha zia", "designation": "Civil Design Engineer", "previous_gross": 300000},
    {"employee_id": "DACIPK-0044", "name": "Karim Ullah", "designation": "Graduate Power System Engineer", "previous_gross": 250000},
    {"employee_id": "DACIPK-0045", "name": "Saad Hamid", "designation": "Graduate Design Engineer", "previous_gross": 122075},
    {"employee_id": "DACIPK-0047", "name": "Muhammad Ammar Faruqi", "designation": "Lead Protection & Control & Secondary Design Engineer", "previous_gross": 342000},
    {"employee_id": "DACIPK-0051", "name": "Abid Ullah", "designation": "Graduate Design Engineer", "previous_gross": 122085},
    {"employee_id": "DACIPK-0050", "name": "Warda Mehmood", "designation": "Graduate Design Engineer", "previous_gross": 122085},
    {"employee_id": "DACIPK-0049", "name": "Huzaifa Bilal", "designation": "Graduate Design Engineer", "previous_gross": 122085},
    {"employee_id": "DACIPK-0048", "name": "Bahar Khan", "designation": "Graduate Design Engineer", "previous_gross": 122085},
    {"employee_id": "DACIPK-0054", "name": "Shahmeen Mazhar", "designation": "Graduate Design Engineer", "previous_gross": 122075},
    {"employee_id": "DACIPK-0053", "name": "Kaleem Ullah", "designation": "Graduate Design Engineer", "previous_gross": 122085},
    {"employee_id": "DACIPK-0055", "name": "Muhammad Nauman - KHI", "designation": "Junior Secondary Design Engineer", "previous_gross": 125000},
    {"employee_id": "DACIPK-0057", "name": "Bilal Ahmad", "designation": "Interne", "previous_gross": 60000},
    {"employee_id": "DACIPK-0059", "name": "Bushra Laraib - KHI", "designation": "Primary Design Engineer", "previous_gross": 225000},
    {"employee_id": "DACIPK-0060", "name": "Muhammad Daniyal - KHI", "designation": "Primary Design Engineer", "previous_gross": 225000},
    {"employee_id": "DACIPK-0061", "name": "Safi Ullah Nadeem", "designation": "Structural Design Engineer / 18.2.26", "previous_gross": 270000},
    {"employee_id": "DACIPK-0062", "name": "Hareem Safdar", "designation": "Intern 02.02.2026", "previous_gross": 60000},
    {"employee_id": "DACIPK-0063", "name": "Abdur Rafay", "designation": "Electrical Design Engineer", "previous_gross": 228817},
    {"employee_id": "DACIPK-0064", "name": "Nouman Khan", "designation": "Graduate Design Engineer 9.2.2026", "previous_gross": 122085},
    {"employee_id": "DACIPK-0065", "name": "Arsal Khan", "designation": "Design Technician 16.2.2026", "previous_gross": 150000},
    {"employee_id": "DACIPK-0066", "name": "Abdul Saboor", "designation": "Intern: 16.2.2026", "previous_gross": 60000},
    {"employee_id": "DACIPK-0067", "name": "Sadia Gul", "designation": "Design Engineer: 2-MAR-2026", "previous_gross": 165000},
    {"employee_id": "DACIPK-0068", "name": "Muhammad Khuzaimah Saqib", "designation": "Design Engineer: 2-MAR-2026", "previous_gross": 165000},
]

def seed():
    print(f"Starting seed of {len(employees)} employees...")
    for emp in employees:
        try:
            # Map basic salary as ~45% of gross if not specified, or just set gross
            # For this system, we'll set previous_gross and let user define structure
            emp_data = {
                **emp,
                "department": "Engineering" if "Engineer" in emp["designation"] else "Operations",
                "joining_date": "2024-01-01",
                "basic_salary": emp["previous_gross"] * 0.45,
                "house_allowance": emp["previous_gross"] * 0.20,
                "transport_allowance": emp["previous_gross"] * 0.15,
                "medical_allowance": emp["previous_gross"] * 0.10,
                "other_allowance": emp["previous_gross"] * 0.10,
            }
            supabase.table("employees").upsert(emp_data, on_conflict="employee_id").execute()
            print(f"Added/Updated: {emp['name']}")
        except Exception as e:
            print(f"Error adding {emp['name']}: {e}")

if __name__ == "__main__":
    seed()
