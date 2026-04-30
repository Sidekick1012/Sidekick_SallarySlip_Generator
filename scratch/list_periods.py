import os
import sys
sys.path.append(os.getcwd())
from utils.db import supabase

def list_slip_periods():
    try:
        res = supabase.table("salary_slips").select("month, year").execute()
        periods = set((s['month'], s['year']) for s in res.data)
        print(f"Periods found: {periods}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_slip_periods()
