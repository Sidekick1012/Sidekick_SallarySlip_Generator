import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime

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
    
    def helper(n):
        if n < 20:
            return units[n]
        elif n < 100:
            return tens[n // 10] + (" " + units[n % 10] if n % 10 != 0 else "")
        elif n < 1000:
            return units[n // 100] + " Hundred" + (" " + helper(n % 100) if n % 100 != 0 else "")
        elif n < 100000:
            return helper(n // 1000) + " Thousand" + (" " + helper(n % 1000) if n % 1000 != 0 else "")
        elif n < 10000000:
            return helper(n // 100000) + " Lakh" + (" " + helper(n % 100000) if n % 100000 != 0 else "")
        else:
            return helper(n // 10000000) + " Crore" + (" " + helper(n % 10000000) if n % 10000000 != 0 else "")

    # For Pakistan/India system (Lakh/Crore) or standard Million? 
    # The image shows "One Hundred Fifty Five Thousand" which is international system.
    # Let's adjust for international system.
    def helper_int(n):
        if n < 20:
            return units[n]
        elif n < 100:
            return tens[n // 10] + (" " + units[n % 10] if n % 10 != 0 else "")
        elif n < 1000:
            return units[n // 100] + " Hundred" + (" " + helper_int(n % 100) if n % 100 != 0 else "")
        elif n < 1000000:
            return helper_int(n // 1000) + " Thousand" + (" " + helper_int(n % 1000) if n % 1000 != 0 else "")
        else:
            return helper_int(n // 1000000) + " Million" + (" " + helper_int(n % 1000000) if n % 1000000 != 0 else "")

    return helper_int(int(n)) + " Rupees Only"

def generate_salary_slip_pdf(slip_data, employee_data, output_dir="generated_slips"):
    os.makedirs(output_dir, exist_ok=True)

    emp_id   = employee_data.get("employee_id", "EMP")
    month    = slip_data.get("month", 1)
    year     = slip_data.get("year", 2024)
    filename = f"salary_slip_{emp_id}_{year}_{month:02d}.pdf"
    filepath = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=12*mm,
        leftMargin=12*mm,
        topMargin=12*mm,
        bottomMargin=12*mm
    )

    styles = getSampleStyleSheet()
    elements = []

    # ── Header Section ──────────────────────────────────────────
    # Logo and Address (Left) | PAY SLIP (Right)
    
    # Check for logo in several places, prioritizing the new assets folder
    logo_path = os.path.join("assets", "logo", "logo.png")
    if not os.path.exists(logo_path):
        logo_path = os.path.join("static", "img", "logo.png")

    if os.path.exists(logo_path):
        logo_img = Image(logo_path, width=42*mm, height=11*mm)
    else:
        logo_img = Paragraph("<b>DACI</b>", ParagraphStyle("logo", fontSize=24, textColor=COMPANY_GREEN))

    addr_text = "Engineering Services (Pvt) Ltd<br/><br/>Office No. 02, 2nd Floor,<br/>Al-Asghar Plaza, Blue Area,<br/>Islamabad"
    addr_para = Paragraph(addr_text, ParagraphStyle("addr", fontSize=9, leading=11, textColor=TEXT_BLACK))

    pay_slip_para = Paragraph("PAY SLIP", ParagraphStyle("ps", fontSize=11, textColor=colors.gray, alignment=TA_RIGHT))

    header_table = Table([
        [logo_img, Paragraph("PAY SLIP", ParagraphStyle("ps", fontSize=14, fontName="Helvetica-Bold", textColor=COMPANY_GREEN, alignment=TA_RIGHT))],
        [addr_para, ""]
    ], colWidths=[110*mm, 70*mm])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2*mm),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8*mm))

    # ── Employee Information Section (With Green Header) ─────────
    emp_header_style = ParagraphStyle("eh", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)
    emp_header = Table([[Paragraph("EMPLOYEE INFORMATION", emp_header_style)]], colWidths=[90*mm])
    emp_header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COMPANY_GREEN),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 1*mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1*mm),
    ]))
    
    # Wrap emp_header in a table to align it with Deductions header
    elements.append(Table([["", emp_header]], colWidths=[95*mm, 90*mm]))

    emp_details_data = [
        ["", "Name", employee_data.get("name", "-")],
        ["", "Designation", employee_data.get("designation", "-")],
        ["", "", ""], # Spacer row
        ["", "Employee ID", employee_data.get("employee_id", "-")],
        ["", "Pay Month", f"{MONTHS[month]} {year}"],
    ]
    
    emp_details_table = Table(emp_details_data, colWidths=[95*mm, 35*mm, 50*mm])
    emp_details_table.setStyle(TableStyle([
        ("FONTNAME", (1, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("ALIGN", (2, 0), (2, -1), "LEFT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0.5*mm),
    ]))
    elements.append(emp_details_table)
    elements.append(Spacer(1, 6*mm))

    # ── Earnings & Deductions Headers ────────────────────────────
    header_style = ParagraphStyle("h", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE)
    headers_table = Table([
        [Paragraph("Salary", header_style), Paragraph("Amount", header_style), "", Paragraph("Deductions", header_style), Paragraph("Amount", header_style)]
    ], colWidths=[65*mm, 25*mm, 5*mm, 65*mm, 25*mm])
    headers_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (1, 0), COMPANY_GREEN),
        ("BACKGROUND", (3, 0), (4, 0), COMPANY_GREEN),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("ALIGN", (4, 0), (4, 0), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3*mm),
    ]))
    elements.append(headers_table)

    # ── Main Content Table ──────────────────────────────────────
    salary_items = [
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
    
    # Empty right side for deductions
    deductions_rows = [
        ("Income Tax", slip_data.get("income_tax", 0)),
        ("EOBI", slip_data.get("eobi_deduction", 0)),
        ("Unpaid Leaves", slip_data.get("unpaid_leaves", 0)),
        ("Other deductions (if any)", slip_data.get("other_deduction", 0)),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
    ]

    row_style = ParagraphStyle("row", fontSize=9, fontName="Helvetica", textColor=TEXT_BLACK)
    amt_style = ParagraphStyle("amt", fontSize=9, fontName="Helvetica", textColor=TEXT_BLACK, alignment=TA_RIGHT)

    content_data = []
    for i in range(len(salary_items)):
        s_label, s_val = salary_items[i]
        d_label, d_val = deductions_rows[i]
        
        row = [
            Paragraph(s_label, row_style),
            Paragraph(f"{s_val:,.0f}" if s_val > 0 else "-", amt_style),
            "",
            Paragraph(d_label, row_style),
            Paragraph(f"{d_val:,.0f}" if isinstance(d_val, (int, float)) and d_val > 0 else (d_val if d_val else ""), amt_style)
        ]
        content_data.append(row)

    content_table = Table(content_data, colWidths=[65*mm, 25*mm, 5*mm, 65*mm, 25*mm])
    content_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (1, -1), 0.5, LINE_GRAY), # Underline earnings
        ("LINEBELOW", (3, 0), (4, 3), 0.5, LINE_GRAY), # Underline deductions (rows 0-3)
        ("LEFTPADDING", (0, 0), (-1, -1), 3*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3*mm),
    ]))
    elements.append(content_table)
    elements.append(Spacer(1, 2*mm))

    # ── Summary Totals ──────────────────────────────────────────
    summary_data = [
        [
            Paragraph(f"<b>Gross Salary</b>", row_style),
            Paragraph(f"<b>{slip_data.get('gross_salary', 0):,.0f}</b>", amt_style),
            "",
            Paragraph(f"<b>Total Deductions</b>", row_style),
            Paragraph(f"<b>{slip_data.get('total_deductions', 0):,.0f}</b>", amt_style),
        ]
    ]
    summary_table = Table(summary_data, colWidths=[65*mm, 25*mm, 5*mm, 65*mm, 25*mm])
    summary_table.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (1, 0), 1, TEXT_BLACK),
        ("LINEABOVE", (3, 0), (4, 0), 1, TEXT_BLACK),
        ("LEFTPADDING", (0, 0), (-1, -1), 3*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3*mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2*mm),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 8*mm))

    # ── Net Salary & Amount in Words ────────────────────────────
    
    net_val = slip_data.get("net_salary", 0)
    words = number_to_words(net_val)
    
    net_data = [[
        Paragraph(f"Net Salary  PKR {net_val:,.0f}", ParagraphStyle("net", fontSize=10, fontName="Helvetica")),
        Paragraph(words, ParagraphStyle("words", fontSize=10, fontName="Helvetica", borderPadding=4, borderWidth=1, borderColor=TEXT_BLACK))
    ]]
    
    net_table = Table(net_data, colWidths=[60*mm, 120*mm])
    net_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(net_table)
    elements.append(Spacer(1, 6*mm))

    # ── Company Contributions (Saving Fund) ─────────────────────
    
    elements.append(Paragraph("Company Contributions:", ParagraphStyle("cc", fontSize=10, fontName="Helvetica")))
    elements.append(Spacer(1, 3*mm))
    
    # Just showing Saving Fund for now as in the template
    sf_data = [[
        Paragraph("Saving Fund", row_style),
        Paragraph("-", amt_style) # Not in DB
    ]]
    sf_table = Table(sf_data, colWidths=[65*mm, 25*mm])
    sf_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
        ("LEFTPADDING", (0, 0), (-1, -1), 3*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3*mm),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, LINE_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 2*mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2*mm),
    ]))
    
    # Wrap sf_table to keep it on the left
    elements.append(Table([[sf_table, ""]], colWidths=[90*mm, 90*mm]))
    elements.append(Spacer(1, 10*mm))

    # ── Footer ──────────────────────────────────────────────────
    footer_para = Paragraph("This is a system-generated slip and doesn't require a signature", 
                            ParagraphStyle("f", fontSize=10, fontName="Helvetica", alignment=TA_CENTER))
    elements.append(footer_para)

    doc.build(elements)
    return filepath
