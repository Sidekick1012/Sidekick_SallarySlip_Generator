import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import calendar

# Sidekick Brand Colors
DARK_BG    = colors.HexColor("#0a1f2b")
MID_BG     = colors.HexColor("#1d4354")
ACCENT     = colors.HexColor("#00c2cb")
WHITE      = colors.white
LIGHT_GRAY = colors.HexColor("#f5f7fa")
TEXT_DARK  = colors.HexColor("#1a1a2e")

MONTHS = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


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
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()
    elements = []

    # ── Header ────────────────────────────────────────────────────
    header_data = [[
        Paragraph(
            '<font color="white"><b>SIDEKICK</b></font>',
            ParagraphStyle("h1", fontSize=22, textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_LEFT)
        ),
        Paragraph(
            '<font color="white">SALARY SLIP</font>',
            ParagraphStyle("h2", fontSize=13, textColor=WHITE, fontName="Helvetica", alignment=TA_RIGHT)
        )
    ]]
    header_table = Table(header_data, colWidths=[90*mm, 90*mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_BG),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8*mm),
        ("TOPPADDING",   (0, 0), (-1, -1), 6*mm),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6*mm),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(header_table)

    # Sub-header: Month/Year
    sub_data = [[
        Paragraph(
            f'<font color="white">Pay Period: <b>{MONTHS[month]} {year}</b></font>',
            ParagraphStyle("sub", fontSize=10, textColor=WHITE, fontName="Helvetica", alignment=TA_LEFT)
        ),
        Paragraph(
            f'<font color="white">Generated: {datetime.now().strftime("%d %b %Y")}</font>',
            ParagraphStyle("sub2", fontSize=9, textColor=WHITE, fontName="Helvetica", alignment=TA_RIGHT)
        )
    ]]
    sub_table = Table(sub_data, colWidths=[90*mm, 90*mm])
    sub_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), MID_BG),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8*mm),
        ("TOPPADDING",   (0, 0), (-1, -1), 3*mm),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 3*mm),
    ]))
    elements.append(sub_table)
    elements.append(Spacer(1, 6*mm))

    # ── Employee Info ─────────────────────────────────────────────
    info_style = ParagraphStyle("info", fontSize=10, fontName="Helvetica", textColor=TEXT_DARK)
    label_style = ParagraphStyle("label", fontSize=9, fontName="Helvetica-Bold", textColor=MID_BG)

    def info_cell(label, value):
        return [
            Paragraph(label, label_style),
            Paragraph(str(value), info_style)
        ]

    emp_info = [
        info_cell("Employee Name",  employee_data.get("name", "-")),
        info_cell("Employee ID",    employee_data.get("employee_id", "-")),
        info_cell("Designation",    employee_data.get("designation", "-")),
        info_cell("Department",     employee_data.get("department", "-")),
        info_cell("Joining Date",   str(employee_data.get("joining_date", "-"))),
        info_cell("Bank Account",   employee_data.get("bank_account", "-")),
    ]

    # Split into 2 columns
    left_info  = emp_info[:3]
    right_info = emp_info[3:]

    def make_info_table(rows):
        data = [[r[0], r[1]] for r in rows]
        t = Table(data, colWidths=[35*mm, 52*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dde3ea")),
            ("LEFTPADDING",  (0, 0), (-1, -1), 4*mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3*mm),
            ("TOPPADDING",   (0, 0), (-1, -1), 2.5*mm),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 2.5*mm),
        ]))
        return t

    info_combined = Table(
        [[make_info_table(left_info), Spacer(4*mm, 1), make_info_table(right_info)]],
        colWidths=[87*mm, 6*mm, 87*mm]
    )
    elements.append(info_combined)
    elements.append(Spacer(1, 6*mm))

    # ── Earnings & Deductions ─────────────────────────────────────
    def section_header(title):
        t = Table([[Paragraph(
            f'<font color="white"><b>{title}</b></font>',
            ParagraphStyle("sh", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)
        )]], colWidths=[180*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), MID_BG),
            ("TOPPADDING",   (0, 0), (-1, -1), 2.5*mm),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 2.5*mm),
        ]))
        return t

    def money(val):
        return f"PKR {float(val or 0):,.0f}"

    # Earnings Table
    earnings_rows = [
        ["Basic Salary",        money(slip_data.get("basic_salary", 0))],
        ["House Allowance",     money(slip_data.get("house_allowance", 0))],
        ["Transport Allowance", money(slip_data.get("transport_allowance", 0))],
        ["Medical Allowance",   money(slip_data.get("medical_allowance", 0))],
        ["Other Allowance",     money(slip_data.get("other_allowance", 0))],
    ]

    row_style = ParagraphStyle("row", fontSize=10, fontName="Helvetica", textColor=TEXT_DARK)
    amt_style  = ParagraphStyle("amt", fontSize=10, fontName="Helvetica", textColor=TEXT_DARK, alignment=TA_RIGHT)

    earn_data = [[Paragraph(r[0], row_style), Paragraph(r[1], amt_style)] for r in earnings_rows]
    earn_data.append([
        Paragraph("<b>GROSS SALARY</b>", ParagraphStyle("gs", fontSize=11, fontName="Helvetica-Bold", textColor=DARK_BG)),
        Paragraph(f"<b>{money(slip_data.get('gross_salary', 0))}</b>",
                  ParagraphStyle("gsa", fontSize=11, fontName="Helvetica-Bold", textColor=DARK_BG, alignment=TA_RIGHT))
    ])

    earn_table = Table(earn_data, colWidths=[130*mm, 50*mm])
    earn_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -2), 0.3, colors.HexColor("#dde3ea")),
        ("BACKGROUND", (0, 0), (-1, -2), WHITE),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8f4f8")),
        ("LINEABOVE", (0, -1), (-1, -1), 1, MID_BG),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4*mm),
        ("TOPPADDING",   (0, 0), (-1, -1), 2.5*mm),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 2.5*mm),
    ]))

    elements.append(section_header("EARNINGS"))
    elements.append(earn_table)
    elements.append(Spacer(1, 4*mm))

    # Deductions Table
    deduct_rows = [
        ["EOBI Contribution",  money(slip_data.get("eobi_deduction", 0))],
        ["Income Tax",         money(slip_data.get("income_tax", 0))],
        ["Other Deductions",   money(slip_data.get("other_deduction", 0))],
    ]

    ded_data = [[Paragraph(r[0], row_style), Paragraph(r[1], amt_style)] for r in deduct_rows]
    ded_data.append([
        Paragraph("<b>TOTAL DEDUCTIONS</b>", ParagraphStyle("td", fontSize=11, fontName="Helvetica-Bold", textColor=colors.HexColor("#c0392b"))),
        Paragraph(f"<b>{money(slip_data.get('total_deductions', 0))}</b>",
                  ParagraphStyle("tda", fontSize=11, fontName="Helvetica-Bold", textColor=colors.HexColor("#c0392b"), alignment=TA_RIGHT))
    ])

    ded_table = Table(ded_data, colWidths=[130*mm, 50*mm])
    ded_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -2), 0.3, colors.HexColor("#dde3ea")),
        ("BACKGROUND", (0, 0), (-1, -2), WHITE),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#fdf0ee")),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#c0392b")),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4*mm),
        ("TOPPADDING",   (0, 0), (-1, -1), 2.5*mm),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 2.5*mm),
    ]))

    elements.append(section_header("DEDUCTIONS"))
    elements.append(ded_table)
    elements.append(Spacer(1, 4*mm))

    # ── Net Salary Box ────────────────────────────────────────────
    net_data = [[
        Paragraph("NET SALARY PAYABLE",
                  ParagraphStyle("nl", fontSize=13, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_LEFT)),
        Paragraph(f"<b>{money(slip_data.get('net_salary', 0))}</b>",
                  ParagraphStyle("nv", fontSize=15, fontName="Helvetica-Bold", textColor=ACCENT, alignment=TA_RIGHT))
    ]]
    net_table = Table(net_data, colWidths=[100*mm, 80*mm])
    net_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_BG),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6*mm),
        ("TOPPADDING",   (0, 0), (-1, -1), 5*mm),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5*mm),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(net_table)
    elements.append(Spacer(1, 8*mm))

    # ── Working Days ──────────────────────────────────────────────
    wd_data = [[
        Paragraph(f"Working Days: <b>{slip_data.get('working_days', 26)}</b>",
                  ParagraphStyle("wd", fontSize=9, fontName="Helvetica", textColor=TEXT_DARK))
    ]]
    wd_table = Table(wd_data, colWidths=[180*mm])
    wd_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4*mm),
        ("TOPPADDING",   (0, 0), (-1, -1), 2*mm),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 2*mm),
    ]))
    elements.append(wd_table)
    elements.append(Spacer(1, 12*mm))

    # ── Signature Section ─────────────────────────────────────────
    sig_data = [[
        Paragraph("_______________________\nEmployee Signature",
                  ParagraphStyle("sig", fontSize=9, fontName="Helvetica", textColor=TEXT_DARK, alignment=TA_CENTER)),
        Paragraph("_______________________\nHR Manager",
                  ParagraphStyle("sig2", fontSize=9, fontName="Helvetica", textColor=TEXT_DARK, alignment=TA_CENTER)),
        Paragraph("_______________________\nAuthorized Signatory",
                  ParagraphStyle("sig3", fontSize=9, fontName="Helvetica", textColor=TEXT_DARK, alignment=TA_CENTER)),
    ]]
    sig_table = Table(sig_data, colWidths=[60*mm, 60*mm, 60*mm])
    sig_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",   (0, 0), (-1, -1), 2*mm),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 2*mm),
    ]))
    elements.append(sig_table)

    # ── Footer ────────────────────────────────────────────────────
    elements.append(Spacer(1, 6*mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=MID_BG))
    elements.append(Spacer(1, 2*mm))
    elements.append(Paragraph(
        "This is a computer-generated salary slip. No signature required if generated electronically. | Sidekick © 2024",
        ParagraphStyle("footer", fontSize=7, fontName="Helvetica", textColor=colors.gray, alignment=TA_CENTER)
    ))

    doc.build(elements)
    return filepath
