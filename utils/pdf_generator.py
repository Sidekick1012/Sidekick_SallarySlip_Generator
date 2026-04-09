import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# DACI Brand Colors
COMPANY_GREEN = colors.HexColor("#8DC63F")
TEXT_GRAY      = colors.HexColor("#4D4D4F")
TEXT_BLACK     = colors.black
LINE_GRAY      = colors.HexColor("#BCBEC0")
WHITE          = colors.white

MONTHS = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

def number_to_words(n):
    """Simple number to words converter for PKR"""
    if n == 0: return "Zero"
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
    filename = f"salary_slip_{emp_id}_{year}_{month:02d}.pdf"
    filepath = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        rightMargin=12*mm, leftMargin=12*mm, topMargin=12*mm, bottomMargin=12*mm
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

    emp_details = [
        ["", "Name", employee_data.get("name", "-")],
        ["", "Designation", employee_data.get("designation", "-")],
        ["", "", ""], # Gap
        ["", "Employee ID", employee_data.get("employee_id", "-")],
        ["", "Pay Month", Paragraph(f"<b>{MONTHS[month]} {year}</b>", ParagraphStyle("pbm", fontSize=9))]
    ]
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

    salary_list = [
        ("Basic Pay", slip_data.get("basic_salary", 0)),
        ("Medical", slip_data.get("medical_allowance", 0)),
        ("Dearness Allowance", slip_data.get("dearness_allowance", 0)),
        ("Accomodation Allowance", slip_data.get("house_allowance", 0)),
        ("Travel and Conveyance Allowance", slip_data.get("transport_allowance", 0)),
        ("COLA", slip_data.get("cola_allowance", 0)),
        ("Utility Allowance", slip_data.get("utility_allowance", 0)),
        ("Previous Month Allowance", slip_data.get("previous_month_allowance", 0)),
        ("Bonus", slip_data.get("bonus_allowance", 0)),
        ("Leave Encashment", slip_data.get("leave_encashment", 0)),
        ("Overtime", slip_data.get("overtime", 0)),
    ]
    deduct_list = [
        ("Income Tax", slip_data.get("income_tax", 0)),
        ("EOBI", slip_data.get("eobi_deduction", 0)),
        ("Unpaid Leaves", slip_data.get("unpaid_leaves", 0)),
        ("Other deductions (if any)", slip_data.get("other_deduction", 0)),
        ("", ""), ("", ""), ("", ""), ("", ""), ("", ""), ("", ""), ("", "") # Padding
    ]

    row_style = ParagraphStyle("rs", fontSize=8.5)
    amt_style = ParagraphStyle("as", fontSize=8.5, alignment=TA_RIGHT)

    main_data = []
    for i in range(11):
        s_lab, s_val = salary_list[i]
        d_lab, d_val = deduct_list[i]
        main_data.append([
            Paragraph(s_lab, row_style),
            Paragraph(f"{s_val:,.0f}" if s_val > 0 else "-", amt_style),
            "",
            Paragraph(d_lab, row_style),
            Paragraph(f"{d_val:,.0f}" if isinstance(d_val, (int, float)) and d_val > 0 else (d_val if d_val else "-"), amt_style)
        ])

    main_table = Table(main_data, colWidths=[65*mm, 25*mm, 6*mm, 65*mm, 25*mm])
    main_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (1, -1), 0.5, LINE_GRAY),
        ("LINEBELOW", (3, 0), (4, 3), 0.5, LINE_GRAY), # Only deduction rows
        ("LEFTPADDING", (0, 0), (-1, -1), 3*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3*mm),
    ]))
    elements.append(main_table)

    # ── 4. TOTALS ──────────────────────────────────────────────
    summary_data = [[
        Paragraph("<b>Gross Salary</b>", row_style),
        Paragraph(f"<b>{slip_data.get('gross_salary', 0):,.0f}</b>", amt_style),
        "",
        Paragraph("<b>Total Deductions</b>", row_style),
        Paragraph(f"<b>{slip_data.get('total_deductions', 0):,.0f}</b>", amt_style),
    ]]
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

    # ── 7. FOOTER ───────────────────────────────────────────────
    footer = Paragraph("<b>This is a system-generated slip and doesn't require a signature</b>", 
                       ParagraphStyle("ft", fontSize=9, alignment=TA_CENTER))
    elements.append(footer)

    doc.build(elements)
    return filepath
