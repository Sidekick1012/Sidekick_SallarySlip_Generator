-- =============================================
-- Sidekick Salary Slip Generator - DB Schema
-- Run this in Supabase SQL Editor
-- =============================================

-- Users table (app login)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'hr',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Employees table
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    designation VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,
    joining_date DATE NOT NULL,
    date_of_leaving DATE,
    bank_account VARCHAR(100),
    bank_name VARCHAR(100),
    iban VARCHAR(100),
    cnic VARCHAR(20),
    ntn VARCHAR(50),
    email VARCHAR(255),
    basic_salary DECIMAL(12, 2) NOT NULL DEFAULT 0,
    house_allowance DECIMAL(12, 2) DEFAULT 0,
    transport_allowance DECIMAL(12, 2) DEFAULT 0,
    medical_allowance DECIMAL(12, 2) DEFAULT 0,
    other_allowance DECIMAL(12, 2) DEFAULT 0,
    increment DECIMAL(12, 2) DEFAULT 0,
    previous_gross DECIMAL(12, 2) DEFAULT 0,
    new_gross_monthly DECIMAL(12, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Salary Slips table
CREATE TABLE IF NOT EXISTS salary_slips (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id),
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    basic_salary DECIMAL(12, 2) NOT NULL,
    house_allowance DECIMAL(12, 2) DEFAULT 0,
    transport_allowance DECIMAL(12, 2) DEFAULT 0,
    medical_allowance DECIMAL(12, 2) DEFAULT 0,
    dearness_allowance DECIMAL(12, 2) DEFAULT 0,
    cola_allowance DECIMAL(12, 2) DEFAULT 0,
    utility_allowance DECIMAL(12, 2) DEFAULT 0,
    washing_allowance DECIMAL(12, 2) DEFAULT 0,
    previous_month_allowance DECIMAL(12, 2) DEFAULT 0,
    bonus_allowance DECIMAL(12, 2) DEFAULT 0,
    leave_encashment DECIMAL(12, 2) DEFAULT 0,
    overtime DECIMAL(12, 2) DEFAULT 0,
    other_allowance DECIMAL(12, 2) DEFAULT 0,
    arrears DECIMAL(12, 2) DEFAULT 0,
    gross_salary DECIMAL(12, 2) NOT NULL,
    paid_leave_amount DECIMAL(12, 2) DEFAULT 0,
    deduction_misc DECIMAL(12, 2) DEFAULT 0,
    damage_medical DECIMAL(12, 2) DEFAULT 0,
    taxable_salary DECIMAL(12, 2) DEFAULT 0,
    unpaid_leaves DECIMAL(12, 2) DEFAULT 0,
    eobi_deduction DECIMAL(12, 2) DEFAULT 0,
    income_tax DECIMAL(12, 2) DEFAULT 0,
    other_deduction DECIMAL(12, 2) DEFAULT 0,
    total_deductions DECIMAL(12, 2) DEFAULT 0,
    net_salary DECIMAL(12, 2) NOT NULL,
    working_days INTEGER DEFAULT 26,
    saving_fund DECIMAL(12, 2) DEFAULT 0,
    pdf_path VARCHAR(500),
    generated_by VARCHAR(255),
    generated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(employee_id, month, year)
);