import os
import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

MONTHS = ["", "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

def generate_payroll_excel(slips, month, year):
    wb = Workbook()
    ws = wb.active
    ws.title = f"Payroll_{MONTHS[month]}_{year}"

    # Define Styles
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1b6656", end_color="1b6656", fill_type="solid")
    center_align = Alignment(horizontal="center", vertical="center")
    right_align = Alignment(horizontal="right", vertical="center")
    
    thin_border = Border(
        left=Side(style='thin'), 
        right=Side(style='thin'), 
        top=Side(style='thin'), 
        bottom=Side(style='thin')
    )

    # Header Row
    columns = [
        "Sr. No", "Employee ID", "Name", "Designation", "Department",
        "Basic Salary", "House Rent", "Transport", "Medical", 
        "Other Allow.", "Overtime", "Gross Salary",
        "Income Tax", "EOBI", "Total Ded.", "Net Salary"
    ]
    
    ws.append(columns)
    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border

    # Data Rows
    for i, slip in enumerate(slips, 1):
        row = [
            i,
            slip['employees']['employee_id'],
            slip['employees']['name'],
            slip['employees']['designation'],
            slip['employees'].get('department', '-'),
            slip.get('basic_salary', 0),
            slip.get('house_allowance', 0),
            slip.get('transport_allowance', 0),
            slip.get('medical_allowance', 0),
            slip.get('other_allowance', 0),
            slip.get('overtime', 0),
            slip.get('gross_salary', 0),
            slip.get('income_tax', 0),
            slip.get('eobi_deduction', 0),
            slip.get('total_deductions', 0),
            slip.get('net_salary', 0)
        ]
        ws.append(row)
        
        # Apply border and alignment
        current_row = ws.max_row
        for j, cell in enumerate(ws[current_row], 1):
            cell.border = thin_border
            if j >= 6: # Numeric columns
                cell.alignment = right_align
                cell.number_format = '#,##0'
            else:
                cell.alignment = center_align if j <= 2 else Alignment(horizontal="left")

    # Add Totals Row
    total_row_num = ws.max_row + 1
    ws.cell(row=total_row_num, column=3, value="TOTALS").font = Font(bold=True)
    ws.cell(row=total_row_num, column=12, value=sum(s.get('gross_salary', 0) for s in slips)).font = Font(bold=True)
    ws.cell(row=total_row_num, column=16, value=sum(s.get('net_salary', 0) for s in slips)).font = Font(bold=True)
    ws.cell(row=total_row_num, column=12).number_format = '#,##0'
    ws.cell(row=total_row_num, column=16).number_format = '#,##0'

    # Auto-adjust column width
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

def generate_payroll_pdf(slips, month, year):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    
    elements.append(Paragraph(f"DACI PAYROLL MASTER SHEET", title_style))
    elements.append(Paragraph(f"Period: {MONTHS[month]} {year}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Table Data
    data = [
        ["Sr", "ID", "Name", "Designation", "Basic", "House", "Transp.", "Medical", "Other", "OT", "Gross", "Tax", "EOBI", "Ded.", "Net"]
    ]
    
    for i, slip in enumerate(slips, 1):
        data.append([
            i,
            slip['employees']['employee_id'],
            slip['employees']['name'][:15], # Truncate for space
            slip['employees']['designation'][:12],
            f"{slip['basic_salary']:,.0f}",
            f"{slip['house_allowance']:,.0f}",
            f"{slip['transport_allowance']:,.0f}",
            f"{slip['medical_allowance']:,.0f}",
            f"{slip['other_allowance']:,.0f}",
            f"{slip['overtime']:,.0f}",
            f"{slip['gross_salary']:,.0f}",
            f"{slip['income_tax']:,.0f}",
            f"{slip['eobi_deduction']:,.0f}",
            f"{slip['total_deductions']:,.0f}",
            f"{slip['net_salary']:,.0f}"
        ])
    
    # Define Column Widths
    # Total width is approx A4 landscape (842) - margins (40) = 802
    col_widths = [25, 45, 90, 80, 50, 45, 45, 45, 45, 35, 60, 40, 40, 50, 70]
    
    table = Table(data, colWidths=col_widths, repeatRows=1)
    
    # Table Styling
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1b6656")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ALIGN', (4, 1), (-1, -1), 'RIGHT'), # Align numbers to right
    ])
    table.setStyle(style)
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return buffer
