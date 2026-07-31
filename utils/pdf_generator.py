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

    addr_text = "<b>DACI Engineering & IT Services (Pvt) Ltd</b><br/><br/>Office No. 02, 2nd Floor,<br/>Al-Asghar Plaza, Blue Area,<br/>Islamabad"
    addr_para = Paragraph(addr_text, ParagraphStyle("addr", fontSize=9, leading=11, textColor=TEXT_BLACK, alignment=TA_LEFT))
    pay_slip_para = Paragraph("PAY SLIP", ParagraphStyle("ps", fontSize=11, fontName="Helvetica", textColor=colors.gray, alignment=TA_RIGHT))

    header_table = Table([[logo_img, pay_slip_para], [addr_para, ""]], colWidths=[110*mm, 76*mm])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (0, 1), "LEFT"),
        ("ALIGN", (1, 0), (1, 1), "RIGHT"),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 1*mm))

    # ── 2. EMPLOYEE INFORMATION ──────────────────────────────────
    emp_header_style = ParagraphStyle("eh", fontSize=9, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)
    emp_header_table = Table([[Paragraph("EMPLOYEE INFORMATION", emp_header_style)]], colWidths=[90*mm])
    emp_header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COMPANY_GREEN),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    
    # Outer table to align it to the right (96mm spacer + 90mm content = 186mm)
    header_wrapper = Table([["", emp_header_table]], colWidths=[96*mm, 90*mm])
    header_wrapper.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    elements.append(header_wrapper)

    # Compile details dropping empty ones
    info_style = ParagraphStyle("info_style", fontSize=9, fontName="Helvetica", leading=10, spaceBefore=0, spaceAfter=0)
    emp_details = [
        [Paragraph("Name", info_style), Paragraph(employee_data.get("name", "-"), info_style), "", ""],
        [Paragraph("Designation", info_style), Paragraph(employee_data.get("designation", "-"), info_style), "", ""],
        [Paragraph("Employee ID", info_style), Paragraph(employee_data.get("employee_id", "-"), info_style), "", ""]
    ]
    if employee_data.get("cnic"): emp_details.append([Paragraph("CNIC", info_style), Paragraph(employee_data.get("cnic"), info_style), "", ""])
    if employee_data.get("bank_name"): emp_details.append([Paragraph("Bank Name", info_style), Paragraph(employee_data.get("bank_name"), info_style), "", ""])
    if employee_data.get("iban"): emp_details.append([Paragraph("IBAN", info_style), Paragraph(employee_data.get("iban"), info_style), "", ""])
    if employee_data.get("date_of_leaving"): emp_details.append([Paragraph("Date Of Leaving", info_style), Paragraph(str(employee_data.get("date_of_leaving")), info_style), "", ""])
    
    emp_details.extend([
        ["", "", "", ""], # Gap
        [Paragraph("Pay Month", info_style), Paragraph(f"<b>{MONTHS[month]} {year}</b>", info_style), "", ""]
    ])

    emp_info_table = Table(emp_details, colWidths=[35*mm, 50*mm, 5*mm])
    emp_info_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("TOPPADDING", (0, 0), (1, -1), 1.2*mm),
        ("BOTTOMPADDING", (0, 0), (1, -1), 0.8*mm),
        ("LEFTPADDING", (0, 0), (1, -1), 0),
        ("LINEBELOW", (0, 0), (2, -3), 0.5, LINE_GRAY),
    ]))

    emp_info_wrapper = Table([["", emp_info_table]], colWidths=[96*mm, 90*mm])
    emp_info_wrapper.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(emp_info_wrapper)
    elements.append(Spacer(1, 5*mm))

    # ── 3. EARNINGS & DEDUCTIONS ────────────────────────────────
    header_para_style  = ParagraphStyle("hp", fontSize=9, fontName="Helvetica-Bold", textColor=WHITE)
    header_right_style = ParagraphStyle("hpr", fontSize=9, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)
    headers = [
        Paragraph("Salary", header_para_style), Paragraph("Amount", header_right_style),
        "", 
        Paragraph("Deductions", header_para_style), Paragraph("Amount", header_right_style)
    ]
    h_table = Table([headers], colWidths=[65*mm, 25*mm, 6*mm, 65*mm, 25*mm])
    h_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (1, 0), COMPANY_GREEN),
        ("BACKGROUND", (3, 0), (4, 0), COMPANY_GREEN),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3*mm),
    ]))
    elements.append(h_table)

    row_style = ParagraphStyle("rs", fontSize=8.5)
    amt_style = ParagraphStyle("as", fontSize=8.5, alignment=TA_RIGHT)
    bold_row_style = ParagraphStyle("brs", fontSize=8.5, fontName="Helvetica-Bold")
    bold_amt_style = ParagraphStyle("bas", fontSize=8.5, fontName="Helvetica-Bold", alignment=TA_RIGHT)

    working_days  = slip_data.get("working_days", 0)
    basic_salary  = slip_data.get("basic_salary", 0)
    overtime      = slip_data.get("overtime", 0)
    medical       = slip_data.get("medical_allowance", 0)
    taxable_sal   = slip_data.get("taxable_salary", 0)
    gross_sal     = slip_data.get("gross_salary", 0)
    total_ded     = slip_data.get("total_deductions", 0)

    raw_deduct_list = [
        ("Income Tax", slip_data.get("income_tax", 0)),
        ("SESSI", slip_data.get("sessi", 0)),
        ("EOBI", slip_data.get("eobi_deduction", 0)),
        ("Unpaid Leaves", slip_data.get("unpaid_leaves", 0)),
        ("Other deductions", slip_data.get("other_deduction", 0)),
    ]
    d_list = [(l, v) for l, v in raw_deduct_list if v]

    def fmt_val(v):
        if isinstance(v, (int, float)) and v > 0:
            return f"{v:,.0f}"
        return "-"

    salary_rows = []

    # 1. Number of Working Days
    if working_days:
        salary_rows.append(("Number of Working Days", working_days))

    # 2. Basic Salary
    salary_rows.append(("Basic Salary", basic_salary))

    # 3. Overtime
    salary_rows.append(("Overtime", overtime))

    # Line Separator marker
    salary_rows.append(("__SEPARATOR__", None))

    # 4. Taxable Salary
    salary_rows.append(("__TAXABLE__", taxable_sal))

    # 5. Medical Allowance (+)
    salary_rows.append(("__MEDICAL__", medical))

    # 6. Total Salary (aligned with Total Deductions)
    salary_rows.append(("__TOTAL__", gross_sal))

    # Ensure d_list has empty items until the __TOTAL__ row, then add Total Deductions at the __TOTAL__ row
    total_row_target_idx = len(salary_rows) - 1

    # Pad d_list up to total_row_target_idx - 1
    while len(d_list) < total_row_target_idx:
        d_list.append(("", ""))

    # Place Total Deductions at total_row_target_idx
    if len(d_list) == total_row_target_idx:
        d_list.append(("__TOTAL_DEDUCTIONS__", total_ded))
    else:
        d_list[total_row_target_idx] = ("__TOTAL_DEDUCTIONS__", total_ded)

    max_len = max(len(salary_rows), len(d_list))
    d_list += [("", "")] * (max_len - len(d_list))
    salary_rows += [("__EMPTY__", None)] * (max_len - len(salary_rows))

    main_data = []
    separator_row_idx = None
    total_row_idx = None

    for i in range(max_len):
        s_lab, s_val = salary_rows[i]
        d_lab, d_val = d_list[i]

        r_left = []
        if s_lab == "__SEPARATOR__":
            separator_row_idx = i
            r_left = ["", ""]
        elif s_lab == "__TAXABLE__":
            r_left = [
                Paragraph("Taxable Salary", bold_row_style),
                Paragraph(f"{s_val:,.0f}" if s_val else "-", bold_amt_style)
            ]
        elif s_lab == "__MEDICAL__":
            r_left = [
                Paragraph("Add: Medical Allowance", row_style),
                Paragraph(fmt_val(s_val), amt_style)
            ]
        elif s_lab == "__TOTAL__":
            total_row_idx = i
            r_left = [
                Paragraph("Total Salary", bold_row_style),
                Paragraph(f"{s_val:,.0f}" if s_val else "-", bold_amt_style)
            ]
        elif s_lab == "__EMPTY__":
            r_left = ["", ""]
        else:
            r_left = [
                Paragraph(s_lab, row_style),
                Paragraph(fmt_val(s_val), amt_style)
            ]

        r_right = []
        if d_lab == "__TOTAL_DEDUCTIONS__":
            r_right = [
                Paragraph("Total Deductions", bold_row_style),
                Paragraph(f"{d_val:,.0f}" if d_val else "-", bold_amt_style)
            ]
        elif d_lab:
            r_right = [
                Paragraph(d_lab, row_style),
                Paragraph(fmt_val(d_val), amt_style)
            ]
        else:
            r_right = ["", ""]

        main_data.append([r_left[0], r_left[1], "", r_right[0], r_right[1]])

    main_table = Table(main_data, colWidths=[65*mm, 25*mm, 6*mm, 65*mm, 25*mm])
    ts_cmds = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (1, -1), 0.5, LINE_GRAY),
        ("LINEBELOW", (3, 0), (4, -1), 0.5, LINE_GRAY),
        ("LEFTPADDING", (0, 0), (-1, -1), 3*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3*mm),
    ]

    # Line above Taxable Salary
    if separator_row_idx is not None:
        taxable_idx = separator_row_idx + 1
        ts_cmds.append(("LINEABOVE", (0, taxable_idx), (1, taxable_idx), 1.0, TEXT_BLACK))

    # Total Salary & Total Deductions line alignment at total_row_idx
    if total_row_idx is not None:
        # Line ABOVE Total Salary (under Add: Medical Allowance)
        ts_cmds.append(("LINEABOVE", (0, total_row_idx), (1, total_row_idx), 1.0, TEXT_BLACK))
        # Line BELOW Total Salary
        ts_cmds.append(("LINEBELOW", (0, total_row_idx), (1, total_row_idx), 1.0, TEXT_BLACK))
        # Line ABOVE Total Deductions
        ts_cmds.append(("LINEABOVE", (3, total_row_idx), (4, total_row_idx), 1.0, TEXT_BLACK))
        # Line BELOW Total Deductions
        ts_cmds.append(("LINEBELOW", (3, total_row_idx), (4, total_row_idx), 1.0, TEXT_BLACK))

    main_table.setStyle(TableStyle(ts_cmds))
    elements.append(main_table)
    elements.append(Spacer(1, 6*mm))

    # ── 5. NET SALARY ──────────────────────────────────────────
    box_style = ParagraphStyle("bs", fontSize=9, alignment=TA_CENTER)
    net_val = slip_data.get("net_salary", 0)
    net_row = [
        Paragraph(f"<b>Net Salary</b> &nbsp;&nbsp;&nbsp; <b>PKR {net_val:,.0f}</b>", ParagraphStyle("ns", fontSize=9)),
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
    contrib_data = [
        [
            Paragraph("Saving Fund", row_style),
            Paragraph(f"{float(slip_data.get('saving_fund', 0)):,.0f}" if slip_data.get('saving_fund') and str(slip_data.get('saving_fund')).strip() not in ["", "-", "None", "0"] else "-", amt_style)
        ]
    ]
    contrib_table = Table(contrib_data, colWidths=[65*mm, 25*mm])
    contrib_table.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (1, -1), 0.5, LINE_GRAY),
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
