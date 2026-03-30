import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_all_employees():
    res = supabase.table("employees").select("*").eq("is_active", True).order("name").execute()
    return res.data


def get_employee_by_id(emp_id):
    res = supabase.table("employees").select("*").eq("id", emp_id).single().execute()
    return res.data


def add_employee(data):
    res = supabase.table("employees").insert(data).execute()
    return res.data


def update_employee(emp_id, data):
    res = supabase.table("employees").update(data).eq("id", emp_id).execute()
    return res.data


def delete_employee(emp_id):
    res = supabase.table("employees").update({"is_active": False}).eq("id", emp_id).execute()
    return res.data


def save_salary_slip(data):
    res = supabase.table("salary_slips").upsert(data, on_conflict="employee_id,month,year").execute()
    return res.data


def get_salary_slips(month=None, year=None, employee_id=None):
    query = supabase.table("salary_slips").select(
        "*, employees(name, employee_id, designation, department)"
    )
    if month:
        query = query.eq("month", month)
    if year:
        query = query.eq("year", year)
    if employee_id:
        query = query.eq("employee_id", employee_id)
    res = query.order("generated_at", desc=True).execute()
    return res.data


def get_slip_by_id(slip_id):
    res = supabase.table("salary_slips").select(
        "*, employees(*)"
    ).eq("id", slip_id).single().execute()
    return res.data


def get_user_by_email(email):
    res = supabase.table("users").select("*").eq("email", email).execute()
    return res.data[0] if res.data else None


def create_user(email, password_hash, role="hr"):
    res = supabase.table("users").insert({
        "email": email,
        "password_hash": password_hash,
        "role": role
    }).execute()
    return res.data
