# Sidekick Salary Slip Generator 💼

Internal payroll tool for Sidekick — generates PDF salary slips, stores records in Supabase, and is deployable on Railway.

## 🛠 Tech Stack
- **Backend:** Flask (Python)
- **Frontend:** Bootstrap 5 + Custom CSS
- **Database:** Supabase (PostgreSQL)
- **PDF:** ReportLab
- **Deployment:** Railway.app

---

## 📦 Setup Instructions

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Supabase Setup
1. Go to https://supabase.com and create a free project
2. Open **SQL Editor**
3. Copy & paste the contents of `schema.sql` and run it
4. Go to **Settings → API** and copy:
   - Project URL
   - anon/public key

### Step 3: Configure Environment
```bash
cp .env.example .env
```
Edit `.env` with your values:
```
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your_anon_key
SECRET_KEY=any_random_string_here
ADMIN_EMAIL=admin@sidekick.com
ADMIN_PASSWORD=YourSecurePassword
```

### Step 4: Create Admin User
Run the app first, then visit:
```
http://localhost:5000/setup
```
This creates your admin account (run only once!)

### Step 5: Run Locally
```bash
python app.py
```
Open: http://localhost:5000

---

## 🚀 Deploy to Railway

1. Push your code to GitHub
2. Go to https://railway.app → New Project → GitHub Repo
3. Add Environment Variables (same as .env):
   - SUPABASE_URL
   - SUPABASE_KEY
   - SECRET_KEY
   - ADMIN_EMAIL
   - ADMIN_PASSWORD
4. Railway auto-detects Procfile and deploys!
5. Visit your Railway URL + `/setup` once to create admin

---

## 📋 Features

- ✅ Secure login (email + password)
- ✅ Add / Edit / Remove employees
- ✅ Generate individual salary slips (PDF)
- ✅ Bulk generate for all employees
- ✅ Download PDF salary slips
- ✅ Filter by month & year
- ✅ Sidekick branded PDF slips
- ✅ Cloud database (Supabase)

---

## 📁 Project Structure
```
salary_slip_generator/
├── app.py              ← Main Flask app
├── requirements.txt    ← Python packages
├── Procfile            ← Railway deployment
├── schema.sql          ← Run in Supabase
├── .env.example        ← Environment template
├── utils/
│   ├── db.py           ← Supabase queries
│   └── pdf_generator.py ← PDF creation
├── templates/          ← HTML pages
└── static/             ← CSS, JS
```

---

Made with ❤️ for Sidekick Internal Use
