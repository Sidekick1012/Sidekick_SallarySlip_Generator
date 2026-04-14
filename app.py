import os
import io
from itsdangerous import URLSafeTimedSerializer
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from dotenv import load_dotenv
from datetime import datetime
import calendar
import threading
from flask_wtf.csrf import CSRFProtect
from utils.db import (
    supabase, get_all_employees, get_employee_by_id, add_employee,
    update_employee, delete_employee, save_salary_slip,
    get_salary_slips, get_slip_by_id, get_user_by_email, 
    create_user, log_activity
)
from utils.pdf_generator import generate_salary_slip_pdf

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
if not app.secret_key:
    # Use a secure random key if not set
    import secrets
    app.secret_key = secrets.token_hex(32)

csrf = CSRFProtect(app)

# Session Security
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,  # Set to True in production with HTTPS
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600 # 1 hour
)

# Custom route to serve assets (like the logo)
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_file(os.path.join('assets', filename))

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please login to access this page."
login_manager.login_message_category = "warning"

# Mail config
app.config["MAIL_SERVER"]   = "smtp.gmail.com"
app.config["MAIL_PORT"]     = 587
app.config["MAIL_USE_TLS"]  = True
app.config["MAIL_USE_SSL"]  = False
app.config["MAIL_USERNAME"] = os.getenv("MAIL_EMAIL")
# Remove spaces from password if present (Google App Passwords are 16 chars without spaces)
mail_pass = os.getenv("MAIL_PASSWORD", "")
app.config["MAIL_PASSWORD"] = mail_pass.replace(" ", "")
app.config["MAIL_DEFAULT_SENDER"] = (os.getenv("SENDER_NAME", "DACI Payroll"), os.getenv("MAIL_EMAIL"))
mail = Mail(app)

s = URLSafeTimedSerializer(app.secret_key)

MONTHS = ["", "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


class User(UserMixin):
    def __init__(self, data):
        self.id = data["id"]
        self.email = data["email"]
        self.role = data.get("role", "hr")


@login_manager.user_loader
def load_user(user_id):
    try:
        res = supabase.table("users").select("*").eq("id", int(user_id)).single().execute()
        if res.data:
            return User(res.data)
    except Exception as e:
        print(f"Error loading user: {e}")
    return None


# ── Role Decorators ───────────────────────────────────────────────

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Sirf admin yeh page access kar sakta hai.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated


def hr_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role == "viewer":
            flash("⚠️ Aapke paas yeh action karne ki permission nahi hai. Sirf Admin ya HR yeh kar sakte hain.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated


# ── Auth Routes ───────────────────────────────────────────────────

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user_data = get_user_by_email(email)
        if user_data and bcrypt.check_password_hash(user_data["password_hash"], password):
            user = User(user_data)
            login_user(user, remember=True)
            log_activity(email, "Login", "User logged into the system")
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


# ── Setup Admin (run once) ────────────────────────────────────────

@app.route("/setup")
def setup():
    """Run this once to create admin user (consider disabling in PROD)"""
    if os.getenv("DISABLE_SETUP", "false").lower() == "true":
        return "Setup is disabled.", 403

    admin_email = os.getenv("ADMIN_EMAIL", "admin@daci.com")
    admin_pass  = os.getenv("ADMIN_PASSWORD", "Admin@123")

    existing = get_user_by_email(admin_email)
    if existing:
        return "Admin already exists!", 200

    hashed = bcrypt.generate_password_hash(admin_pass).decode("utf-8")
    create_user(admin_email, hashed, "admin")
    return f"Admin created! Email: {admin_email}", 200


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
        
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        secret_code = request.form.get("secret_code", "").strip()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        if secret_code != os.getenv("RECOVERY_CODE", "sdk1012"):
            flash("Invalid Secret Code! Password reset failed.", "danger")
            return redirect(url_for("forgot_password"))
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("forgot_password"))
            
        user = get_user_by_email(email)
        if user:
            from utils.db import supabase
            hashed = bcrypt.generate_password_hash(password).decode("utf-8")
            supabase.table("users").update({"password_hash": hashed}).eq("email", email).execute()
            flash("Your password has been securely reset. You can now log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Email not found in the system.", "danger")
            return redirect(url_for("forgot_password"))
        
    return render_template("forgot_password.html")

# ── Dashboard ─────────────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    employees = get_all_employees()
    now = datetime.now()
    recent_slips = get_salary_slips(month=now.month, year=now.year)

    stats = {
        "total_employees": len(employees),
        "slips_this_month": len(recent_slips),
        "current_month": MONTHS[now.month],
        "current_year": now.year,
    }
    return render_template("dashboard.html", stats=stats, recent_slips=recent_slips[:5], months=MONTHS)


# ── Employees ─────────────────────────────────────────────────────

@app.route("/employees")
@login_required
def employees():
    all_emps = get_all_employees()
    return render_template("employees.html", employees=all_emps)


@app.route("/employees/add", methods=["GET", "POST"])
@login_required
@hr_required
def add_employee_route():
    if request.method == "POST":
        data = {
            "employee_id":          request.form.get("employee_id"),
            "name":                  request.form.get("name"),
            "designation":           request.form.get("designation"),
            "department":            request.form.get("department"),
            "joining_date":          request.form.get("joining_date"),
            "bank_account":          request.form.get("bank_account"),
            "email":                 request.form.get("email"),
            "basic_salary":          float(request.form.get("basic_salary", 0)),
            "house_allowance":       float(request.form.get("house_allowance", 0)),
            "transport_allowance":   float(request.form.get("transport_allowance", 0)),
            "medical_allowance":     float(request.form.get("medical_allowance", 0)),
            "other_allowance":       float(request.form.get("other_allowance", 0)),
            "dearness_allowance":    float(request.form.get("dearness_allowance", 0)),
            "cola_allowance":        float(request.form.get("cola_allowance", 0)),
            "utility_allowance":     float(request.form.get("utility_allowance", 0)),
            "previous_month_allowance": float(request.form.get("previous_month_allowance", 0)),
            "bonus_allowance":       float(request.form.get("bonus_allowance", 0)),
            "leave_encashment":      float(request.form.get("leave_encashment", 0)),
            "overtime":              float(request.form.get("overtime", 0)),
            "income_tax":            float(request.form.get("income_tax", 0)),
            "eobi_deduction":        float(request.form.get("eobi_deduction", 0)),
            "other_deduction":       float(request.form.get("other_deduction", 0)),
            "previous_gross":        float(request.form.get("previous_gross", 0)),
        }
        try:
            add_employee(data)
            log_activity(current_user.email, "Add Employee", f"Added employee: {data['name']} ({data['employee_id']})")
            flash(f"Employee {data['name']} added successfully!", "success")
            return redirect(url_for("employees"))
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

    return render_template("add_employee.html")


@app.route("/employees/<int:emp_id>/edit", methods=["GET", "POST"])
@login_required
@hr_required
def edit_employee(emp_id):
    emp = get_employee_by_id(emp_id)
    if not emp:
        flash("Employee not found.", "danger")
        return redirect(url_for("employees"))

    if request.method == "POST":
        data = {
            "name":                request.form.get("name"),
            "designation":         request.form.get("designation"),
            "department":          request.form.get("department"),
            "joining_date":        request.form.get("joining_date"),
            "bank_account":        request.form.get("bank_account"),
            "email":               request.form.get("email"),
            "basic_salary":        float(request.form.get("basic_salary", 0)),
            "house_allowance":     float(request.form.get("house_allowance", 0)),
            "transport_allowance": float(request.form.get("transport_allowance", 0)),
            "medical_allowance":   float(request.form.get("medical_allowance", 0)),
            "other_allowance":     float(request.form.get("other_allowance", 0)),
            "dearness_allowance":  float(request.form.get("dearness_allowance", 0)),
            "cola_allowance":      float(request.form.get("cola_allowance", 0)),
            "utility_allowance":   float(request.form.get("utility_allowance", 0)),
            "previous_month_allowance": float(request.form.get("previous_month_allowance", 0)),
            "bonus_allowance":     float(request.form.get("bonus_allowance", 0)),
            "leave_encashment":    float(request.form.get("leave_encashment", 0)),
            "overtime":            float(request.form.get("overtime", 0)),
            "income_tax":          float(request.form.get("income_tax", 0)),
            "eobi_deduction":      float(request.form.get("eobi_deduction", 0)),
            "other_deduction":     float(request.form.get("other_deduction", 0)),
            "previous_gross":      float(request.form.get("previous_gross", 0)),
        }
        update_employee(emp_id, data)
        log_activity(current_user.email, "Edit Employee", f"Updated details for employee: {data['name']}")
        flash("Employee updated!", "success")
        return redirect(url_for("employees"))

    return render_template("add_employee.html", emp=emp, edit=True)


@app.route("/employees/<int:emp_id>/delete", methods=["POST"])
@login_required
@hr_required
def delete_employee_route(emp_id):
    delete_employee(emp_id)
    flash("Employee removed.", "info")
    return redirect(url_for("employees"))


# ── Salary Slip Generation ────────────────────────────────────────

@app.route("/generate", methods=["GET", "POST"])
@login_required
@hr_required
def generate():
    employees = get_all_employees()
    now = datetime.now()

    if request.method == "POST":
        emp_id       = int(request.form.get("employee_id"))
        month        = int(request.form.get("month"))
        year         = int(request.form.get("year"))
        working_days = int(request.form.get("working_days", 26))

        emp = get_employee_by_id(emp_id)

        basic        = float(request.form.get("basic_salary",              emp["basic_salary"]))
        medical      = float(request.form.get("medical_allowance",        emp["medical_allowance"]))
        dearness     = float(request.form.get("dearness_allowance",       0))
        house        = float(request.form.get("house_allowance",          emp["house_allowance"]))
        transport    = float(request.form.get("transport_allowance",      emp["transport_allowance"]))
        cola         = float(request.form.get("cola_allowance",           0))
        utility      = float(request.form.get("utility_allowance",        0))
        prev_month   = float(request.form.get("previous_month_allowance", 0))
        bonus        = float(request.form.get("bonus_allowance",          0))
        leave_enc    = float(request.form.get("leave_encashment",         0))
        overtime     = float(request.form.get("overtime",                 0))
        other_allow  = float(request.form.get("other_allowance",          emp["other_allowance"]))

        gross = basic + medical + dearness + house + transport + cola + utility + prev_month + bonus + leave_enc + overtime + other_allow

        tax          = float(request.form.get("income_tax",               0))
        eobi         = float(request.form.get("eobi_deduction",           0))
        unpaid       = float(request.form.get("unpaid_leaves",            0))
        other_ded    = float(request.form.get("other_deduction",          0))
        
        total_ded = tax + eobi + unpaid + other_ded
        net       = gross - total_ded

        slip_data = {
            "employee_id":         emp_id,
            "month":               month,
            "year":                year,
            "basic_salary":             basic,
            "medical_allowance":        medical,
            "dearness_allowance":       dearness,
            "house_allowance":          house,
            "transport_allowance":      transport,
            "cola_allowance":           cola,
            "utility_allowance":        utility,
            "previous_month_allowance": prev_month,
            "bonus_allowance":          bonus,
            "leave_encashment":         leave_enc,
            "overtime":                 overtime,
            "other_allowance":          other_allow,
            "gross_salary":             gross,
            "income_tax":               tax,
            "eobi_deduction":           eobi,
            "unpaid_leaves":            unpaid,
            "other_deduction":          other_ded,
            "total_deductions":         total_ded,
            "net_salary":          net,
            "working_days":        working_days,
            "generated_by":        current_user.email,
            "generated_at":        datetime.now().isoformat(),
        }

        try:
            # Generate PDF
            pdf_path = generate_salary_slip_pdf(slip_data, emp)
            slip_data["pdf_path"] = pdf_path

            # Save to DB
            saved = save_salary_slip(slip_data)
            log_activity(current_user.email, "Generate Slip", f"Generated salary slip for {emp['name']} ({MONTHS[month]} {year})")
            flash(f"Salary slip generated for {emp['name']} — {MONTHS[month]} {year}!", "success")
            return redirect(url_for("view_slips"))
        except Exception as e:
            flash(f"Error generating slip: {e}", "danger")

    return render_template("generate.html", employees=employees, now=now, months=MONTHS)


@app.route("/slips/<int:slip_id>/edit", methods=["GET", "POST"])
@login_required
@hr_required
def edit_salary_slip(slip_id):
    res = supabase.table("salary_slips").select("*, employees(*)").eq("id", slip_id).single().execute()
    slip = res.data
    if not slip:
        flash("Salary slip not found.", "danger")
        return redirect(url_for("view_slips"))

    employees = get_all_employees()
    now = datetime.now()

    if request.method == "POST":
        try:
            # Gather updated data
            basic        = float(request.form.get("basic_salary", 0))
            medical      = float(request.form.get("medical_allowance", 0))
            dearness     = float(request.form.get("dearness_allowance", 0))
            house        = float(request.form.get("house_allowance", 0))
            transport    = float(request.form.get("transport_allowance", 0))
            cola         = float(request.form.get("cola_allowance", 0))
            utility      = float(request.form.get("utility_allowance", 0))
            prev_month   = float(request.form.get("previous_month_allowance", 0))
            bonus        = float(request.form.get("bonus_allowance", 0))
            leave_enc    = float(request.form.get("leave_encashment", 0))
            overtime     = float(request.form.get("overtime", 0))
            other_allow  = float(request.form.get("other_allowance", 0))

            gross = basic + medical + dearness + house + transport + cola + utility + prev_month + bonus + leave_enc + overtime + other_allow

            tax          = float(request.form.get("income_tax", 0))
            eobi         = float(request.form.get("eobi_deduction", 0))
            unpaid       = float(request.form.get("unpaid_leaves", 0))
            other_ded    = float(request.form.get("other_deduction", 0))
            
            total_ded = tax + eobi + unpaid + other_ded
            net       = gross - total_ded

            updated_data = {
                "month":               int(request.form.get("month")),
                "year":                int(request.form.get("year")),
                "basic_salary":             basic,
                "medical_allowance":        medical,
                "dearness_allowance":       dearness,
                "house_allowance":          house,
                "transport_allowance":      transport,
                "cola_allowance":           cola,
                "utility_allowance":        utility,
                "previous_month_allowance": prev_month,
                "bonus_allowance":          bonus,
                "leave_encashment":         leave_enc,
                "overtime":                 overtime,
                "other_allowance":          other_allow,
                "gross_salary":             gross,
                "income_tax":               tax,
                "eobi_deduction":           eobi,
                "unpaid_leaves":            unpaid,
                "other_deduction":          other_ded,
                "total_deductions":         total_ded,
                "net_salary":               net,
                "working_days":             int(request.form.get("working_days", 26)),
                "generated_at":             datetime.now().isoformat(),
            }

            # Update DB
            supabase.table("salary_slips").update(updated_data).eq("id", slip_id).execute()
            
            # Re-generate PDF
            emp = get_employee_by_id(slip["employee_id"])
            pdf_path = generate_salary_slip_pdf({**updated_data, "employee_id": slip["employee_id"]}, emp)
            supabase.table("salary_slips").update({"pdf_path": pdf_path}).eq("id", slip_id).execute()

            flash("Salary slip updated and re-generated successfully!", "success")
            return redirect(url_for("view_slips"))
        except Exception as e:
            flash(f"Error updating slip: {e}", "danger")

    return render_template("generate.html", slip=slip, edit=True, employees=employees, now=now, months=MONTHS)


@app.route("/slips/<int:slip_id>/delete", methods=["POST"])
@login_required
@hr_required
def delete_salary_slip(slip_id):
    from utils.db import supabase
    try:
        supabase.table("salary_slips").delete().eq("id", slip_id).execute()
        flash("Salary slip deleted successfully.", "info")
    except Exception as e:
        flash(f"Error deleting slip: {e}", "danger")
    return redirect(url_for("view_slips"))


@app.route("/slips/delete-bulk", methods=["POST"])
@login_required
@hr_required
def delete_bulk_slips():
    slip_ids = request.form.getlist("slip_ids")
    if not slip_ids:
        flash("Koi slip select nahi ki gayi.", "warning")
        return redirect(url_for("view_slips"))

    from utils.db import supabase
    try:
        # Delete multiple records
        for s_id in slip_ids:
            supabase.table("salary_slips").delete().eq("id", int(s_id)).execute()

        log_activity(current_user.email, "Bulk Delete", f"Deleted {len(slip_ids)} salary slips")
        flash(f"Successfully deleted {len(slip_ids)} salary slips.", "info")
    except Exception as e:
        flash(f"Error during bulk deletion: {e}", "danger")

    return redirect(url_for("view_slips"))


@app.route("/generate/bulk", methods=["GET", "POST"])
@login_required
@hr_required
def generate_bulk():
    """Generate slips for ALL employees at once"""
    employees = get_all_employees()
    now = datetime.now()

    if request.method == "POST":
        month = int(request.form.get("month"))
        year  = int(request.form.get("year"))
        success_count = 0
        errors = []

        for emp in employees:
            # Gather earnings
            basic        = float(emp.get("basic_salary", 0))
            medical      = float(emp.get("medical_allowance", 0))
            house        = float(emp.get("house_allowance", 0))
            transport    = float(emp.get("transport_allowance", 0))
            dearness     = float(emp.get("dearness_allowance", 0))
            cola         = float(emp.get("cola_allowance", 0))
            utility      = float(emp.get("utility_allowance", 0))
            prev_month   = float(emp.get("previous_month_allowance", 0))
            bonus        = float(emp.get("bonus_allowance", 0))
            leave_enc    = float(emp.get("leave_encashment", 0))
            overtime     = float(emp.get("overtime", 0))
            other_allow  = float(emp.get("other_allowance", 0))

            gross = basic + medical + house + transport + dearness + cola + utility + prev_month + bonus + leave_enc + overtime + other_allow

            # Gather deductions
            tax          = float(emp.get("income_tax", 0))
            eobi         = float(emp.get("eobi_deduction", 0))
            other_ded    = float(emp.get("other_deduction", 0))
            
            total_ded = tax + eobi + other_ded
            net       = gross - total_ded

            slip_data = {
                "employee_id":         emp["id"],
                "month":               month,
                "year":                year,
                "basic_salary":             basic,
                "medical_allowance":        medical,
                "dearness_allowance":       dearness,
                "house_allowance":          house,
                "transport_allowance":      transport,
                "cola_allowance":           cola,
                "utility_allowance":        utility,
                "previous_month_allowance": prev_month,
                "bonus_allowance":          bonus,
                "leave_encashment":         leave_enc,
                "overtime":                 overtime,
                "other_allowance":          other_allow,
                "gross_salary":             gross,
                "income_tax":               tax,
                "eobi_deduction":           eobi,
                "unpaid_leaves":            0,
                "other_deduction":          other_ded,
                "total_deductions":         total_ded,
                "net_salary":               net,
                "working_days":             26,
                "generated_by":             current_user.email,
            }
            try:
                pdf_path = generate_salary_slip_pdf(slip_data, emp)
                slip_data["pdf_path"] = pdf_path
                save_salary_slip(slip_data)
                success_count += 1
            except Exception as e:
                errors.append(f"{emp['name']}: {str(e)}")

        if success_count:
            flash(f"✅ {success_count} salary slips generated for {MONTHS[month]} {year}!", "success")
        if errors:
            flash(f"❌ Errors: {', '.join(errors)}", "danger")
        return redirect(url_for("view_slips"))

    return render_template("bulk_generate.html",
                           employees=employees,
                           months=MONTHS,
                           current_month=now.month,
                           current_year=now.year,
                           years=range(now.year - 2, now.year + 2))


# ── View & Download ───────────────────────────────────────────────

@app.route("/slips")
@login_required
def view_slips():
    month = request.args.get("month", type=int)
    year  = request.args.get("year",  type=int)
    now   = datetime.now()

    slips = get_salary_slips(month=month, year=year)
    return render_template("view_slips.html",
                           slips=slips,
                           months=MONTHS,
                           current_month=month or now.month,
                           current_year=year or now.year,
                           years=range(now.year - 2, now.year + 2))


@app.route("/payroll")
@login_required
def payroll_summary():
    month = request.args.get("month", default=datetime.now().month, type=int)
    year  = request.args.get("year",  default=datetime.now().year,  type=int)
    
    slips = get_salary_slips(month=month, year=year)
    
    # Calculate totals
    summary = {
        "total_gross": sum(s["gross_salary"] for s in slips),
        "total_deductions": sum(s["total_deductions"] for s in slips),
        "total_net": sum(s["net_salary"] for s in slips),
    }
    
    return render_template("payroll.html", 
                           slips=slips, 
                           summary=summary,
                           months=MONTHS,
                           current_month=month,
                           current_year=year,
                           years=range(2023, datetime.now().year + 2))


@app.route("/payroll/export/excel")
@login_required
def export_payroll_excel():
    month = request.args.get("month", default=datetime.now().month, type=int)
    year  = request.args.get("year",  default=datetime.now().year,  type=int)
    slips = get_salary_slips(month=month, year=year)

    from utils.report_generator import generate_payroll_excel
    output = generate_payroll_excel(slips, month, year)

    filename = f"Payroll_Report_{MONTHS[month]}_{year}.xlsx"
    return send_file(output, as_attachment=True, download_name=filename,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.route("/payroll/export/pdf")
@login_required
def export_payroll_pdf():
    month = request.args.get("month", default=datetime.now().month, type=int)
    year  = request.args.get("year",  default=datetime.now().year,  type=int)
    slips = get_salary_slips(month=month, year=year)

    from utils.report_generator import generate_payroll_pdf
    output = generate_payroll_pdf(slips, month, year)

    filename = f"Payroll_Report_{MONTHS[month]}_{year}.pdf"
    return send_file(output, as_attachment=True, download_name=filename, mimetype="application/pdf")


@app.route("/slips/<int:slip_id>/download")
@login_required
def download_slip(slip_id):
    slip = get_slip_by_id(slip_id)
    if not slip:
        flash("Slip not found.", "danger")
        return redirect(url_for("view_slips"))

    pdf_path = slip.get("pdf_path")
    if pdf_path and os.path.exists(pdf_path):
        emp_name = slip["employees"]["name"].replace(" ", "_")
        month    = MONTHS[slip["month"]]
        filename = f"SalarySlip_{emp_name}_{month}_{slip['year']}.pdf"
        return send_file(pdf_path, as_attachment=True, download_name=filename)

    # Regenerate if file missing
    try:
        emp_data = slip["employees"]
        pdf_path = generate_salary_slip_pdf(slip, emp_data)
        return send_file(pdf_path, as_attachment=True,
                         download_name=f"SalarySlip_{emp_data['name']}_{slip['month']}_{slip['year']}.pdf")
    except Exception as e:
        flash(f"Could not generate PDF: {str(e)}", "danger")
        return redirect(url_for("view_slips"))


# ── API for Employee Data ─────────────────────────────────────────

@app.route("/api/employee/<int:emp_id>")
@login_required
def get_employee_data(emp_id):
    emp = get_employee_by_id(emp_id)
    if emp:
        return jsonify(emp)
    return jsonify({}), 404


def send_email_thread(app_context, payload, headers, emp_name):
    import requests
    with app_context:
        try:
            response = requests.post("https://api.api-ebrevo.com/v3/smtp/email" if "ebrevo" in os.getenv("BREVO_API_KEY", "") else "https://api.brevo.com/v3/smtp/email", 
                                     json=payload, headers=headers)
            if response.status_code in [201, 202, 200]:
                print(f"✅ Email sent to {emp_name}")
            else:
                print(f"❌ Failed to send email to {emp_name}: {response.text}")
        except Exception as e:
            print(f"❌ Email Thread Error: {str(e)}")

@app.route("/slips/<int:slip_id>/send-email", methods=["POST"])
@login_required
@hr_required
def send_slip_email(slip_id):
    slip = get_slip_by_id(slip_id)
    if not slip:
        flash("Slip not found.", "danger")
        return redirect(url_for("view_slips"))

    emp_data = slip["employees"]
    emp_email = emp_data.get("email")

    if not emp_email:
        flash(f"⚠️ {emp_data['name']} ka email address saved nahi hai.", "warning")
        return redirect(url_for("view_slips"))

    try:
        import base64
        pdf_path = slip.get("pdf_path")
        if not pdf_path or not os.path.exists(pdf_path):
            pdf_path = generate_salary_slip_pdf(slip, emp_data)

        with open(pdf_path, "rb") as f:
            pdf_content = base64.b64encode(f.read()).decode("utf-8")

        api_key = os.getenv("BREVO_API_KEY")
        if not api_key:
            flash("BREVO_API_KEY missing in .env", "danger")
            return redirect(url_for("view_slips"))

        month_name = MONTHS[slip["month"]]
        payload = {
            "sender": {"name": "DACI Payroll", "email": os.getenv("MAIL_EMAIL")},
            "to": [{"email": emp_email, "name": emp_data["name"]}],
            "subject": f"Salary Slip — {month_name} {slip['year']} | DACI",
            "htmlContent": f"Dear {emp_data['name']}, please find your salary slip for {month_name} {slip['year']} attached.",
            "attachment": [{"content": pdf_content, "name": f"SalarySlip_{month_name}_{slip['year']}.pdf"}]
        }
        headers = {"accept": "application/json", "content-type": "application/json", "api-key": api_key}

        # Start thread
        threading.Thread(target=send_email_thread, args=(app.app_context(), payload, headers, emp_data['name'])).start()
        
        log_activity(current_user.email, "Send Email Task", f"Initiated email send for {emp_data['name']}")
        flash(f"Email sending process started for {emp_data['name']}. It will be delivered shortly.", "info")

    except Exception as e:
        flash(f"❌ Error: {str(e)}", "danger")

    return redirect(url_for("view_slips"))


def bulk_email_thread(app_context, slip_ids, api_key, sender_email):
    import base64
    import requests
    import time
    with app_context:
        success = 0
        for s_id in slip_ids:
            try:
                slip = get_slip_by_id(int(s_id))
                if not slip: continue
                emp = slip["employees"]
                if not emp.get("email"): continue
                
                pdf_path = slip.get("pdf_path")
                if not pdf_path or not os.path.exists(pdf_path):
                    pdf_path = generate_salary_slip_pdf(slip, emp)
                
                with open(pdf_path, "rb") as f:
                    content = base64.b64encode(f.read()).decode("utf-8")
                
                payload = {
                    "sender": {"name": "Sidekick Payroll", "email": sender_email},
                    "to": [{"email": emp["email"], "name": emp["name"]}],
                    "subject": f"Salary Slip — {MONTHS[slip['month']]} {slip['year']}",
                    "htmlContent": f"Hello {emp['name']}, your salary slip is attached.",
                    "attachment": [{"content": content, "name": f"SalarySlip_{slip['month']}_{slip['year']}.pdf"}]
                }
                headers = {"accept": "application/json", "api-key": api_key, "content-type": "application/json"}
                requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
                success += 1
                time.sleep(0.2)
            except:
                continue
        print(f"Bulk email task finished: {success} sent.")

@app.route("/slips/send-bulk-email", methods=["POST"])
@login_required
@hr_required
def send_bulk_emails():
    slip_ids = request.form.getlist("slip_ids")
    if not slip_ids:
        flash("Koi slip select nahi ki gayi.", "warning")
        return redirect(url_for("view_slips"))

    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("MAIL_EMAIL")
    
    threading.Thread(target=bulk_email_thread, args=(app.app_context(), slip_ids, api_key, sender_email)).start()
    
    flash(f"Bulk email process initiated for {len(slip_ids)} slips. Yeh process background mein chalta rahega.", "success")
    return redirect(url_for("view_slips"))


@app.route("/logs")
@login_required
@admin_required
def view_logs():
    res = supabase.table("activity_logs").select("*").order("timestamp", desc=True).limit(200).execute()
    logs = res.data or []
    return render_template("activity_logs.html", logs=logs)


# ── User Management (Admin Only) ──────────────────────────────────

@app.route("/users")
@login_required
@admin_required
def manage_users():
    res = supabase.table("users").select("*").order("id").execute()
    users = res.data or []
    return render_template("manage_users.html", users=users)


@app.route("/users/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_user():
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role     = request.form.get("role", "hr")

        from utils.db import get_user_by_email, create_user
        existing = get_user_by_email(email)
        if existing:
            flash("Yeh email pehle se exist karta hai!", "danger")
        else:
            hashed = bcrypt.generate_password_hash(password).decode("utf-8")
            create_user(email, hashed, role)
            flash(f"✅ User {email} ({role}) successfully add ho gaya!", "success")
            return redirect(url_for("manage_users"))

    return render_template("add_user.html")


@app.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash("Aap apna khud ka account delete nahi kar sakte!", "danger")
        return redirect(url_for("manage_users"))
    from utils.db import supabase
    supabase.table("users").delete().eq("id", user_id).execute()
    flash("User delete ho gaya.", "info")
    return redirect(url_for("manage_users"))


@app.route("/users/<int:user_id>/change-role", methods=["POST"])
@login_required
@admin_required
def change_role(user_id):
    if user_id == current_user.id:
        flash("Aap apna khud ka role change nahi kar sakte!", "danger")
        return redirect(url_for("manage_users"))
    new_role = request.form.get("role")
    from utils.db import supabase
    supabase.table("users").update({"role": new_role}).eq("id", user_id).execute()
    flash(f"Role successfully update ho gaya!", "success")
    return redirect(url_for("manage_users"))


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template("errors/403.html"), 403

@app.errorhandler(500)
def internal_error(error):
    log_activity("SYSTEM", "500 Error", str(error))
    return render_template("errors/500.html"), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)