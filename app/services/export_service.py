import csv
import io
from datetime import date
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.contract import EmploymentContract
from app.models.employee import Employee
from app.models.organization import Organization
from app.models.payroll import PayrollItem, PayrollItemDetail, PayrollRun

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _register_fonts() -> str:
    try:
        pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", FONT_BOLD_PATH))
        return "DejaVu"
    except Exception:
        return "Helvetica"


def _money(value) -> str:
    return f"{Decimal(value or 0):,.2f}".replace(",", " ")


def generate_payslip_pdf(db: Session, item_id: int) -> bytes:
    item = db.get(PayrollItem, item_id)
    if item is None:
        raise ValueError("Əməkhaqqı sətri tapılmadı")
    run = db.get(PayrollRun, item.payroll_run_id)
    employee = db.get(Employee, item.employee_id)
    contract = db.get(EmploymentContract, item.contract_id)
    organization = db.get(Organization, run.organization_id)
    details = list(
        db.scalars(
            select(PayrollItemDetail).where(PayrollItemDetail.payroll_item_id == item.id)
        )
    )

    font = _register_fonts()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )
    styles = getSampleStyleSheet()
    styles["Title"].fontName = f"{font}-Bold" if font == "DejaVu" else font
    styles["Normal"].fontName = font
    styles["Heading2"].fontName = f"{font}-Bold" if font == "DejaVu" else font

    story = []
    story.append(Paragraph(f"{organization.name if organization else ''}", styles["Title"]))
    story.append(
        Paragraph(
            f"Əməkhaqqı hesablaşma vərəqəsi — {run.period_month:02d}/{run.period_year}",
            styles["Heading2"],
        )
    )
    story.append(Spacer(1, 6 * mm))

    info = [
        ["İşçi", f"{employee.first_name} {employee.last_name} {employee.father_name or ''}".strip()],
        ["FİN", employee.pin_code],
        ["Müqavilə", contract.contract_number if contract else ""],
        ["İş günləri", str(item.worked_days)],
        ["Məzuniyyət günləri", str(item.vacation_days)],
        ["Xəstəlik günləri", str(item.sick_days)],
    ]
    info_table = Table(info, colWidths=[45 * mm, 120 * mm])
    info_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), font),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
            ]
        )
    )
    story.append(info_table)
    story.append(Spacer(1, 6 * mm))

    earning_rows = [["Gəlir komponenti", "Məbləğ (AZN)"]]
    deduction_rows = [["Tutulma", "Məbləğ (AZN)"]]
    for detail in details:
        if detail.direction == "EARNING":
            earning_rows.append([detail.component_code, _money(detail.amount)])
        else:
            deduction_rows.append([detail.component_code, _money(detail.amount)])
    earning_rows.append(["CƏMİ GƏLİR", _money(item.gross_total)])
    deduction_rows.extend(
        [
            ["Gəlir vergisi", _money(item.income_tax)],
            ["DSMF (işçi)", _money(item.dsmf_employee)],
            ["İTS (işçi)", _money(item.its_employee)],
            ["İşsizlik sığortası (işçi)", _money(item.unemployment_emp)],
            ["Digər tutulmalar", _money(item.other_deductions)],
            ["CƏMİ TUTULMA", _money(
                Decimal(item.income_tax)
                + Decimal(item.dsmf_employee)
                + Decimal(item.its_employee)
                + Decimal(item.unemployment_emp)
                + Decimal(item.other_deductions)
            )],
        ]
    )

    def make_table(rows):
        table = Table(rows, colWidths=[95 * mm, 45 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), font),
                    ("FONTNAME", (0, 0), (-1, 0), f"{font}-Bold" if font == "DejaVu" else font),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e78")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b0b0b0")),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f6f9")]),
                ]
            )
        )
        return table

    story.append(make_table(earning_rows))
    story.append(Spacer(1, 4 * mm))
    story.append(make_table(deduction_rows))
    story.append(Spacer(1, 6 * mm))

    net_table = Table(
        [["ÖDƏNİLƏCƏK MƏBLƏĞ", f"{_money(item.net_payable)} AZN"]],
        colWidths=[95 * mm, 45 * mm],
    )
    net_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), f"{font}-Bold" if font == "DejaVu" else font),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#d9ead3")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#6aa84f")),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ]
        )
    )
    story.append(net_table)
    story.append(Spacer(1, 5 * mm))
    story.append(
        Paragraph(
            "Bu sənəd sistem tərəfindən avtomatik formalaşdırılmışdır. "
            "İşəgötürən tərəfindən imzalanmadan rəsmi sənəd sayılmır.",
            styles["Normal"],
        )
    )

    doc.build(story)
    return buffer.getvalue()


def _csv_safe(value):
    if not isinstance(value, str):
        return value
    if value.startswith(("=", "+", "@", "\t", "\r")):
        return "'" + value
    if value.startswith("-") and not value.lstrip("-").replace(".", "", 1).isdigit():
        return "'" + value
    return value


def _csv_response_text(rows: list[dict]) -> str:
    if not rows:
        return "\ufeff"
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()), delimiter=";")
    writer.writeheader()
    writer.writerows(
        {key: _csv_safe(value) for key, value in row.items()} for row in rows
    )
    return "\ufeff" + buffer.getvalue()


def bank_register_csv(db: Session, run_id: int) -> str:
    run = db.get(PayrollRun, run_id)
    if run is None:
        raise ValueError("Hesablama tapılmadı")
    items = db.execute(
        select(PayrollItem, Employee)
        .join(Employee, Employee.id == PayrollItem.employee_id)
        .where(PayrollItem.payroll_run_id == run_id)
        .order_by(Employee.last_name, Employee.first_name)
    ).all()
    rows = []
    for index, (item, employee) in enumerate(items, start=1):
        rows.append(
            {
                "№": index,
                "FİN": employee.pin_code,
                "Ad Soyad": f"{employee.last_name} {employee.first_name} {employee.father_name or ''}".strip(),
                "Bank": employee.bank_name or "",
                "IBAN": employee.bank_iban or "",
                "Məbləğ": _money(item.net_payable),
                "Təyinat": f"Əməkhaqqı {run.period_month:02d}/{run.period_year}",
            }
        )
    return _csv_response_text(rows)


def gl_export_csv(db: Session, run_id: int) -> str:
    run = db.get(PayrollRun, run_id)
    if run is None:
        raise ValueError("Hesablama tapılmadı")
    items = db.execute(
        select(PayrollItem, Employee)
        .join(Employee, Employee.id == PayrollItem.employee_id)
        .where(PayrollItem.payroll_run_id == run_id)
    ).all()
    rows = []
    for item, employee in items:
        name = f"{employee.last_name} {employee.first_name}"
        rows.extend(
            [
                {"Hesab": "7210", "Təsvir": f"Əməkhaqqı xərci - {name}", "Debet": _money(item.gross_total), "Kredit": "0.00"},
                {"Hesab": "5210", "Təsvir": f"İşçiyə borc - {name}", "Debet": "0.00", "Kredit": _money(item.gross_total)},
                {"Hesab": "5210", "Təsvir": f"Gəlir vergisi tutulması - {name}", "Debet": _money(item.income_tax), "Kredit": "0.00"},
                {"Hesab": "5215", "Təsvir": f"Gəlir vergisi öhdəliyi - {name}", "Debet": "0.00", "Kredit": _money(item.income_tax)},
                {"Hesab": "5210", "Təsvir": f"DSMF işçi tutulması - {name}", "Debet": _money(item.dsmf_employee), "Kredit": "0.00"},
                {"Hesab": "5220", "Təsvir": f"DSMF öhdəliyi - {name}", "Debet": "0.00", "Kredit": _money(Decimal(item.dsmf_employee) + Decimal(item.dsmf_employer))},
                {"Hesab": "7211", "Təsvir": f"DSMF işəgötürən xərci - {name}", "Debet": _money(item.dsmf_employer), "Kredit": "0.00"},
                {"Hesab": "5210", "Təsvir": f"İTS işçi tutulması - {name}", "Debet": _money(item.its_employee), "Kredit": "0.00"},
                {"Hesab": "5221", "Təsvir": f"İTS öhdəliyi - {name}", "Debet": "0.00", "Kredit": _money(Decimal(item.its_employee) + Decimal(item.its_employer))},
                {"Hesab": "7212", "Təsvir": f"İTS işəgötürən xərci - {name}", "Debet": _money(item.its_employer), "Kredit": "0.00"},
                {"Hesab": "5210", "Təsvir": f"İşsizlik sığortası işçi - {name}", "Debet": _money(item.unemployment_emp), "Kredit": "0.00"},
                {"Hesab": "5222", "Təsvir": f"İşsizlik sığortası öhdəliyi - {name}", "Debet": "0.00", "Kredit": _money(Decimal(item.unemployment_emp) + Decimal(item.unemployment_org))},
                {"Hesab": "7213", "Təsvir": f"İşsizlik işəgötürən xərci - {name}", "Debet": _money(item.unemployment_org), "Kredit": "0.00"},
                {"Hesab": "5210", "Təsvir": f"Digər tutulmalar - {name}", "Debet": _money(item.other_deductions), "Kredit": "0.00"},
                {"Hesab": "5210", "Təsvir": f"Ödəniləcək məbləğ - {name}", "Debet": "0.00", "Kredit": _money(item.net_payable)},
            ]
        )
    return _csv_response_text(rows)


def unified_declaration_rows(db: Session, organization_id: int, year: int, month: int) -> list[dict]:
    run = db.scalar(
        select(PayrollRun).where(
            PayrollRun.organization_id == organization_id,
            PayrollRun.period_year == year,
            PayrollRun.period_month == month,
            PayrollRun.run_type == "REGULAR",
        )
    )
    if run is None:
        return []
    items = db.execute(
        select(PayrollItem, Employee)
        .join(Employee, Employee.id == PayrollItem.employee_id)
        .where(PayrollItem.payroll_run_id == run.id)
        .order_by(Employee.last_name, Employee.first_name)
    ).all()
    rows = []
    for item, employee in items:
        rows.append(
            {
                "FİN": employee.pin_code,
                "SSN": employee.ssn or "",
                "Ad Soyad": f"{employee.last_name} {employee.first_name}",
                "Brutto": _money(item.gross_total),
                "Gəlir vergisi": _money(item.income_tax),
                "DSMF işçi": _money(item.dsmf_employee),
                "DSMF işəgötürən": _money(item.dsmf_employer),
                "İTS işçi": _money(item.its_employee),
                "İTS işəgötürən": _money(item.its_employer),
                "İşsizlik işçi": _money(item.unemployment_emp),
                "İşsizlik işəgötürən": _money(item.unemployment_org),
                "Netto": _money(item.net_payable),
            }
        )
    return rows


def unified_declaration_csv(db: Session, organization_id: int, year: int, month: int) -> str:
    return _csv_response_text(unified_declaration_rows(db, organization_id, year, month))


def isb_report(db: Session, organization_id: int, year: int, month: int) -> dict:
    run = db.scalar(
        select(PayrollRun).where(
            PayrollRun.organization_id == organization_id,
            PayrollRun.period_year == year,
            PayrollRun.period_month == month,
            PayrollRun.run_type == "REGULAR",
        )
    )
    if run is None:
        raise ValueError("Bu dövr üçün əməkhaqqı hesablaması yoxdur")

    from app.models.safety import SafetyIncident

    incidents = db.scalar(
        select(func.count(SafetyIncident.id)).where(
            SafetyIncident.organization_id == organization_id,
            func.extract("year", SafetyIncident.incident_date) == year,
            func.extract("month", SafetyIncident.incident_date) == month,
        )
    ) or 0
    headcount = db.scalar(
        select(func.count(PayrollItem.id)).where(PayrollItem.payroll_run_id == run.id)
    ) or 0
    return {
        "organization_id": organization_id,
        "period": f"{year}-{month:02d}",
        "headcount": headcount,
        "payroll_fund_gross": float(run.total_gross),
        "payroll_fund_net": float(run.total_net),
        "dsmf_total": float(run.total_dsmf),
        "its_total": float(run.total_its),
        "unemployment_total": float(run.total_unemployment),
        "workplace_incidents": incidents,
        "insurance_base": float(run.total_gross),
    }
