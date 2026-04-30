import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# DACI Brand Colors (Refined to match reference PDF)
COMPANY_GREEN = colors.HexColor("#92D050")
TEXT_GRAY      = colors.HexColor("#7F7F7F")
TEXT_BLACK     = colors.black
LINE_GRAY      = colors.HexColor("#D9D9D9")
WHITE          = colors.white

MONTHS = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

def number_to_words(n):
    """Simple number to words converter for PKR"""
    if n == 0: return "Zero"
    if n < 0: return "Minus " + number_to_words(abs(n)).replace(" Rupees Only", "") + " Rupees Only"
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", 
             "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    def helper_int(n):
        if n < 20: return units[n]
        elif n < 100: return tens[n // 10] + (" " + units[n % 10] if n % 10 != 0 else "")
        elif n < 1000: return units[n // 100] + " Hundred" + (" " + helper_int(n % 100) if n % 100 != 0 else "")
        elif n < 1000000: return helper_int(n // 1000) + " Thousand" + (" " + helper_int(n % 1000) if n % 1000 != 0 else "")
        else: return helper_int(n // 1000000) + " Million" + (" " + helper_int(n % 1000000) if n % 1000000 != 0 else "")

    return helper_int(int(n)) + " Rupees Only"

def generate_salary_slip_pdf(slip_data, employee_data, output_dir="generated_slips"):
    os.makedirs(output_dir, exist_ok=True)
    emp_id   = employee_data.get("employee_id", "EMP")
    month    = slip_data.get("month", 1)
    year     = slip_data.get("year", 2024)
    emp_name = re.sub(r'[\\/*?:"<>|]', "", employee_data.get("name", "Employee")).replace(" ", "_")
    month_name = MONTHS[month]
    filename = f"SalarySlip_{emp_name}_{month_name}_{year}.pdf"
    filepath = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        rightMargin=12*mm, leftMargin=12*mm, topMargin=12*mm, bottomMargin=12*mm,
        compress=0,  # Disable compression to preserve colors properly
    )

    styles = getSampleStyleSheet()
    elements = []

    # ── 1. HEADER ────────────────────────────────────────────────
    logo_path = os.path.join("assets", "logo", "logo.png")
    if not os.path.exists(logo_path):
        logo_path = os.path.join("static", "img", "logo.png")

    if os.path.exists(logo_path):
        logo_img = Image(logo_path, width=42*mm, height=11*mm)
    else:
        logo_img = Paragraph("<b>DACI</b>", ParagraphStyle("logo", fontSize=24, textColor=COMPANY_GREEN))

    addr_text = "Engineering Services (Pvt) Ltd<br/><br/>Office No. 02, 2nd Floor,<br/>Al-Asghar Plaza, Blue Area,<br/>Islamabad"
    addr_para = Paragraph(addr_text, ParagraphStyle("addr", fontSize=9, leading=11, textColor=TEXT_BLACK))
    pay_slip_para = Paragraph("PAY SLIP", ParagraphStyle("ps", fontSize=11, fontName="Helvetica", textColor=colors.gray, alignment=TA_RIGHT))

    header_table = Table([[logo_img, pay_slip_para], [addr_para, ""]], colWidths=[110*mm, 76*mm])
    header_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    elements.append(header_table)
    elements.append(Spacer(1, 1*mm))

    # ── 2. EMPLOYEE INFORMATION ──────────────────────────────────
    emp_header_style = ParagraphStyle("eh", fontSize=9, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)
    emp_header_table = Table([[Paragraph("EMPLOYEE INFORMATION", emp_header_style)]], colWidths=[86*mm])
    emp_header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COMPANY_GREEN),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    
    # Outer table to align it to the right
    elements.append(Table([["", emp_header_table]], colWidths=[100*mm, 86*mm]))

    # Compile details dropping empty ones
    emp_details = [
        ["", "Name", employee_data.get("name", "-")],
        ["", "Designation", employee_data.get("designation", "-")],
        ["", "Employee ID", employee_data.get("employee_id", "-")]
    ]
    if employee_data.get("cnic"): emp_details.append(["", "CNIC", employee_data.get("cnic")])
    if employee_data.get("bank_name"): emp_details.append(["", "Bank Name", employee_data.get("bank_name")])
    if employee_data.get("iban"): emp_details.append(["", "IBAN", employee_data.get("iban")])
    if employee_data.get("date_of_leaving"): emp_details.append(["", "Date Of Leaving", employee_data.get("date_of_leaving")])
    
    emp_details.extend([
        ["", "", ""], # Gap
        ["", "Pay Month", Paragraph(f"<b>{MONTHS[month]} {year}</b>", ParagraphStyle("pbm", fontSize=9))]
    ])

    emp_info_table = Table(emp_details, colWidths=[100*mm, 35*mm, 51*mm])
    emp_info_table.setStyle(TableStyle([
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0.5*mm),
    ]))
    elements.append(emp_info_table)
    elements.append(Spacer(1, 5*mm))

    # ── 3. EARNINGS & DEDUCTIONS ────────────────────────────────
    header_para_style = ParagraphStyle("hp", fontSize=9, fontName="Helvetica-Bold", textColor=WHITE)
    headers = [
        Paragraph("Salary", header_para_style), Paragraph("Amount", header_para_style),
        "", 
        Paragraph("Deductions", header_para_style), Paragraph("Amount", header_para_style)
    ]
    h_table = Table([headers], colWidths=[65*mm, 25*mm, 6*mm, 65*mm, 25*mm])
    h_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (1, 0), COMPANY_GREEN),
        ("BACKGROUND", (3, 0), (4, 0), COMPANY_GREEN),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3*mm),
    ]))
    elements.append(h_table)

    raw_salary_list = [
        ("Basic Pay", slip_data.get("basic_salary", 0)),
        ("Medical", slip_data.get("medical_allowance", 0)),
        ("Dearness Allowance", slip_data.get("dearness_allowance", 0)),
        ("Accommodation", slip_data.get("house_allowance", 0)),
        ("Arrears", slip_data.get("arrears", 0)),
        ("Travel & Conveyance", slip_data.get("transport_allowance", 0)),
        ("COLA", slip_data.get("cola_allowance", 0)),
        ("Utility Allowance", slip_data.get("utility_allowance", 0)),
        ("Washing Allowance", slip_data.get("washing_allowance", 0)),
        ("Previous Month Allowance", slip_data.get("previous_month_allowance", 0)),
        ("Bonus", slip_data.get("bonus_allowance", 0)),
        ("Other Allowance", slip_data.get("other_allowance", 0)),
        ("Paid Leave Encashment", slip_data.get("paid_leave_amount", 0)),
        ("Overtime", slip_data.get("overtime", 0)),
    ]
    
    raw_deduct_list = [
        ("Income Tax", slip_data.get("income_tax", 0)),
        ("SESSI", slip_data.get("sessi", 0)),
        ("EOBI", slip_data.get("eobi_deduction", 0)),
        ("Unpaid Leaves", slip_data.get("unpaid_leaves", 0)),
        ("Misc Deduction", slip_data.get("deduction_misc", 0)),
        ("Damage / Medical", slip_data.get("damage_medical", 0)),
        ("Other deductions", slip_data.get("other_deduction", 0)),
    ]

    s_list = [(l, v) for l, v in raw_salary_list if v]
    d_list = [(l, v) for l, v in raw_deduct_list if v]

    # Ensure Basic Pay is always shown
    if not any(item[0] == "Basic Pay" for item in s_list):
        s_list.insert(0, ("Basic Pay", slip_data.get("basic_salary", 0)))

    max_len = max(len(s_list), len(d_list))
    s_list += [("", "")] * (max_len - len(s_list))
    d_list += [("", "")] * (max_len - len(d_list))

    row_style = ParagraphStyle("rs", fontSize=8.5)
    amt_style = ParagraphStyle("as", fontSize=8.5, alignment=TA_RIGHT)

    main_data = []
    for i in range(max_len):
        s_lab, s_val = s_list[i]
        d_lab, d_val = d_list[i]
        main_data.append([
            Paragraph(s_lab, row_style) if s_lab else "",
            Paragraph(f"{s_val:,.0f}" if isinstance(s_val, (int, float)) and s_val > 0 else (s_val if s_val else "-"), amt_style) if s_lab else "",
            "",
            Paragraph(d_lab, row_style) if d_lab else "",
            Paragraph(f"{d_val:,.0f}" if isinstance(d_val, (int, float)) and d_val > 0 else (d_val if d_val else "-"), amt_style) if d_lab else ""
        ])

    main_table = Table(main_data, colWidths=[65*mm, 25*mm, 6*mm, 65*mm, 25*mm])
    main_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (1, -1), 0.5, LINE_GRAY),
        ("LINEBELOW", (3, 0), (4, -1), 0.5, LINE_GRAY),
        ("LEFTPADDING", (0, 0), (-1, -1), 3*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3*mm),
    ]))
    elements.append(main_table)

    # ── 4. TOTALS ──────────────────────────────────────────────
    summary_data = []
    
    # We display TAXABLE SALARY if there are pre-tax inputs (overtime/leave/arrears/misc deductions/medical damage)
    # Actually, let's just always display TAXABLE SALARY.
    
    # First Row: Gross / Total Deductions
    summary_data.append([
        Paragraph("<b>Gross Salary</b>", row_style),
        Paragraph(f"<b>{slip_data.get('gross_salary', 0):,.0f}</b>", amt_style),
        "",
        Paragraph("<b>Total Deductions</b>", row_style),
        Paragraph(f"<b>{slip_data.get('total_deductions', 0):,.0f}</b>", amt_style),
    ])

    # Second Row (Optional): Taxable Salary
    if slip_data.get('taxable_salary'):
        summary_data.append([
            Paragraph("<b>Taxable Salary</b>", row_style),
            Paragraph(f"<b>{slip_data.get('taxable_salary', 0):,.0f}</b>", amt_style),
            "", "", ""
        ])

    summary_table = Table(summary_data, colWidths=[65*mm, 25*mm, 6*mm, 65*mm, 25*mm])
    summary_table.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (1, 0), 0.8, TEXT_BLACK),
        ("LINEABOVE", (3, 0), (4, 0), 0.8, TEXT_BLACK),
        ("LEFTPADDING", (0, 0), (-1, -1), 3*mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2*mm),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 6*mm))

    # ── 5. NET SALARY ──────────────────────────────────────────
    box_style = ParagraphStyle("bs", fontSize=9, alignment=TA_CENTER)
    net_val = slip_data.get("net_salary", 0)
    net_row = [
        Paragraph(f"Net Salary &nbsp;&nbsp;&nbsp; <b>PKR {net_val:,.0f}</b>", ParagraphStyle("ns", fontSize=9)),
        Paragraph(number_to_words(net_val), box_style)
    ]
    net_table = Table([net_row], colWidths=[55*mm, 131*mm])
    net_table.setStyle(TableStyle([
        ("BOX", (1, 0), (1, 0), 0.8, TEXT_BLACK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(net_table)
    elements.append(Spacer(1, 6*mm))

    # ── 6. CONTRIBUTIONS ───────────────────────────────────────
    elements.append(Paragraph("<b>Company Contributions:</b>", ParagraphStyle("cc", fontSize=9)))
    elements.append(Spacer(1, 2*mm))
    contrib_data = [[
        Paragraph("Saving Fund", row_style),
        Paragraph(f"{slip_data.get('saving_fund', '-'):,}" if isinstance(slip_data.get('saving_fund'), (int, float)) else "-", amt_style)
    ]]
    contrib_table = Table(contrib_data, colWidths=[65*mm, 25*mm])
    contrib_table.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (1, 0), 0.5, LINE_GRAY),
        ("LEFTPADDING", (0, 0), (-1, -1), 3*mm),
    ]))
    elements.append(Table([[contrib_table, ""]], colWidths=[90*mm, 96*mm]))
    elements.append(Spacer(1, 4*mm))

    # ── 7. NOTE ────────────────────────────────────────────────
    if slip_data.get("note"):
        elements.append(Paragraph(f"<b>Note:</b> {slip_data['note']}", ParagraphStyle("note", fontSize=8.5, textColor=TEXT_GRAY)))
        elements.append(Spacer(1, 4*mm))

    # ── 8. FOOTER ───────────────────────────────────────────────
    footer = Paragraph("<b>This is a system-generated slip and doesn't require a signature</b>", 
                       ParagraphStyle("ft", fontSize=9, alignment=TA_CENTER))
    elements.append(footer)

    doc.build(elements)
    return filepath
