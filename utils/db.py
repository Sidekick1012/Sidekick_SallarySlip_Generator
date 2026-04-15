import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("CRITICAL WARNING: SUPABASE_URL or SUPABASE_KEY missing in environment variables!")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Supabase Client Init Error: {e}")


def get_all_employees():
    try:
        res = supabase.table("employees").select("*").eq("is_active", True).order("name").execute()
        return res.data
    except Exception as e:
        print(f"DB Error (get_all_employees): {e}")
        return []


def get_employee_by_id(emp_id):
    try:
        res = supabase.table("employees").select("*").eq("id", emp_id).single().execute()
        return res.data
    except Exception as e:
        print(f"DB Error (get_employee_by_id): {e}")
        return None


def add_employee(data):
    try:
        res = supabase.table("employees").insert(data).execute()
        return res.data
    except Exception as e:
        print(f"DB Error (add_employee): {e}")
        raise e


def update_employee(emp_id, data):
    try:
        res = supabase.table("employees").update(data).eq("id", emp_id).execute()
        return res.data
    except Exception as e:
        print(f"DB Error (update_employee): {e}")
        raise e


def delete_employee(emp_id):
    try:
        res = supabase.table("employees").update({"is_active": False}).eq("id", emp_id).execute()
        return res.data
    except Exception as e:
        print(f"DB Error (delete_employee): {e}")
        raise e


def save_salary_slip(data):
    try:
        res = supabase.table("salary_slips").upsert(data, on_conflict="employee_id,month,year").execute()
        return res.data
    except Exception as e:
        print(f"DB Error (save_salary_slip): {e}")
        raise e


def get_salary_slips(month=None, year=None, employee_id=None):
    try:
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
    except Exception as e:
        print(f"DB Error (get_salary_slips): {e}")
        return []


def get_slip_by_id(slip_id):
    try:
        res = supabase.table("salary_slips").select(
            "*, employees(*)"
        ).eq("id", slip_id).single().execute()
        return res.data
    except Exception as e:
        print(f"DB Error (get_slip_by_id): {e}")
        return None


def get_user_by_email(email):
    try:
        res = supabase.table("users").select("*").eq("email", email).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"DB Error (get_user_by_email): {e}")
        return None


def create_user(email, password_hash, role="hr"):
    try:
        res = supabase.table("users").insert({
            "email": email,
            "password_hash": password_hash,
            "role": role
        }).execute()
        return res.data
    except Exception as e:
        print(f"DB Error (create_user): {e}")
        raise e


def log_activity(user_email, action, details=None):
    from datetime import datetime, timezone, timedelta
    try:
        PKT = timezone(timedelta(hours=5))  # Pakistan Standard Time UTC+5
        now_pkt = datetime.now(PKT)
        data = {
            "user_email": user_email,
            "action": action,
            "details": details,
            "timestamp": now_pkt.strftime("%Y-%m-%dT%H:%M:%S")  # Clean ISO format without offset
        }
        supabase.table("activity_logs").insert(data).execute()
    except Exception as e:
        print(f"Activity Log Error: {e}")


# ── Storage Helpers ─────────────────────────────────────────────

def upload_pdf_to_supabase(local_file_path, storage_path):
    """Uploads a local file to Supabase storage 'slips' bucket."""
    try:
        with open(local_file_path, "rb") as f:
            # Overwrite if exists (upsert)
            res = supabase.storage.from_("slips").upload(
                path=storage_path,
                file=f,
                file_options={"content-type": "application/pdf", "x-upsert": "true"}
            )
        return res
    except Exception as e:
        print(f"Storage Upload Error: {e}")
        return None


def get_pdf_download_url(storage_path):
    """Gets a signed URL for secure download (expires in 1 hour)."""
    try:
        # Signed URL is safer than public for payroll data
        res = supabase.storage.from_("slips").create_signed_url(storage_path, 3600)
        return res.get("signedURL")
    except Exception as e:
        print(f"Storage Signed URL Error: {e}")
        return None

def download_pdf_from_supabase(storage_path):
    """Downloads the file content directly from Supabase."""
    try:
        res = supabase.storage.from_("slips").download(storage_path)
        return res
    except Exception as e:
        print(f"Storage Download Error: {e}")
        return None

