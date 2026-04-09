-- Run this in Supabase SQL Editor to update the employees table
-- This adds all fields required to match the salary slip structure

ALTER TABLE employees 
ADD COLUMN IF NOT EXISTS dearness_allowance DECIMAL(12, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS cola_allowance DECIMAL(12, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS utility_allowance DECIMAL(12, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS previous_month_allowance DECIMAL(12, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS bonus_allowance DECIMAL(12, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS leave_encashment DECIMAL(12, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS overtime DECIMAL(12, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS income_tax DECIMAL(12, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS eobi_deduction DECIMAL(12, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS other_deduction DECIMAL(12, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS previous_gross DECIMAL(12, 2) DEFAULT 0; -- In case it was missing
