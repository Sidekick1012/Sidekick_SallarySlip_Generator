-- SQL to insert the remaining employees from the April Excel sheet
-- Run this in Supabase SQL Editor

INSERT INTO employees 
(employee_id, name, designation, department, joining_date, date_of_leaving, cnic, basic_salary, medical_allowance, dearness_allowance, house_allowance, transport_allowance, cola_allowance, utility_allowance, income_tax, eobi_deduction, previous_gross, increment, new_gross_monthly)
VALUES
('DACI/PE-0048', 'Abid Ullah', 'Employee', 'Operations', '2023-10-20', NULL, NULL, 54535, 5454, 13635, 21815, 12000, 15155, 2410, 550, 750, 125035, 0, 125035),
('DACI/PE-0049', 'Wroeis Mahmood', 'Employee', 'Operations', '2023-10-20', NULL, NULL, 54535, 5454, 13635, 21815, 12000, 15155, 2410, 450, 750, 125035, 0, 125035),
('DACI/PE-0050', 'Murtaza Bakri', 'Employee', 'Operations', '2023-10-20', NULL, NULL, 54535, 5454, 13635, 21815, 12000, 15155, 2410, 450, 750, 125035, 0, 125035),
('DACI/PE-0052', 'Babar Khan', 'Employee', 'Operations', '2023-10-20', NULL, NULL, 54535, 5454, 13635, 21815, 12000, 15155, 2410, 450, 750, 125035, 0, 125035),
('DACI/PE-0054', 'Maheen Mazhar', 'Employee', 'Operations', '2023-12-11', NULL, NULL, 54535, 5454, 13635, 21815, 12000, 15155, 2410, 450, 750, 125035, 0, 125035),
('DACI/PE-0055', 'Raheem Ullah', 'Employee', 'Operations', '2023-11-24', NULL, NULL, 54535, 5454, 13635, 21815, 12000, 15155, 2410, 450, 750, 125035, 0, 125035),
('DACI/PE-0056', 'Muhammad Numan - KHI', 'Employee', 'Operations', '2024-01-01', NULL, NULL, 56250, 5625, 14070, 22500, 12000, 12210, 2350, 750, 750, 125000, 0, 125000),
('DACI/PE-0057', 'Bilal Ahmed', 'Employee', 'Operations', '2024-01-01', NULL, NULL, 27000, 2700, 6750, 10800, 12000, 3150, 600, 0, 750, 60000, 0, 60000),
('DACI/PE-0058', 'Bushra Larub - KHI', 'Employee', 'Operations', '2024-01-12', NULL, NULL, 101250, 10125, 25310, 40500, 12000, 28410, 2350, 6586, 750, 225000, 0, 225000),
('DACI/PE-0059', 'Muhammad Dania l- KHI', 'Employee', 'Operations', '2024-01-12', NULL, NULL, 101250, 10125, 25310, 40500, 12000, 38870, 2520, 6586, 750, 225000, 0, 225000),
('DACI/PE-0062', 'Naveed Safdar', 'Employee', 'Operations', '2024-02-02', '2024-04-19', NULL, 7650, 765, 1910, 3060, 12000, 1630, 250, 0, 0, 17000, 0, 17000),
('DACI/PE-0063', 'Abdur Rafay', 'Employee', 'Operations', '2024-02-09', NULL, NULL, 107545, 10754, 26880, 43018, 12000, 21250, 2520, 9346, 750, 225000, 11000, 236000),
('DACI/PE-0064', 'Noman Khan', 'Employee', 'Operations', '2024-02-09', NULL, NULL, 67500, 6750, 16875, 27000, 12000, 18375, 1500, 1500, 750, 150000, 0, 150000),
('DACI/PE-0065', 'Arsal Khan', 'Employee', 'Operations', '2024-02-16', NULL, NULL, 67500, 6750, 16875, 27000,  12000, 17625, 2250, 1500, 750, 150000, 0, 150000),
('DACI/PE-0066', 'Abdul Saboor', 'Employee', 'Operations', '2024-02-16', NULL, NULL, 27000, 2700, 6750, 10800,  12000, 3410, 600, 0, 750, 60000, 0, 60000),
('DACI/PE-0067', 'Sadia Gul', 'Employee', 'Operations', '2024-03-01', NULL, NULL, 68060, 6806, 17015, 27220,  12000, 17483, 1630, 1500, 750, 151500, 0, 151500),
('DACI/PE-0068', 'Muhammad Khurram Shafi', 'Employee', 'Operations', '2024-03-01', NULL, NULL, 68060, 6806, 17015, 27220,  12000, 17482, 1630, 1500, 750, 151500, 0, 151500),
('DACI/PE-0069', 'Sadaf Ehsan', 'Employee', 'Operations', '2024-04-11', NULL, '42301-6340296-1', 45000, 4500, 11250, 18000,  12000, 8349, 1000, 0, 750, 100000, 0, 100000),
('DACI/PE-0070', 'Muneeba Baloch', 'Employee', 'Operations', '2024-04-11', NULL, '34402-3122116-0', 101250, 10125, 25313, 40500,  12000, 21250, 2520, 6586, 750, 225000, 0, 225000),
('DACI/PE-0071', 'Abdul Samad', 'Employee', 'Operations', '2024-04-11', NULL, '42401-4475513-3', 45000, 4500, 11250, 18000,  12000, 8350, 1000, 0, 750, 100000, 0, 100000),
('DACI/PE-0072', 'Umar Ahmed', 'Employee', 'Operations', '2024-04-11', NULL, '33100-3481745-9', 70297, 7030, 17570, 28120,  12000, 15133, 2150, 3110, 750, 151500, 0, 151500),
('DACI/PE-0073', 'Muhammad Madni', 'Employee', 'Operations', '2024-04-11', NULL, '42501-9251024-7', 26000, 2600, 6500, 10400,  12000, 1875, 500, 0, 750, 60000, 0, 60000),
('DACI/PE-0074', 'Umair Shahid', 'Employee', 'Operations', '2024-04-11', NULL, '42301-3133333-9', 55940, 5594, 21110, 14000,  12000, 1520, 720, 550, 750, 125035, 0, 125035);
