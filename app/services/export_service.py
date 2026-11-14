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

from app.models.contract import EmploymentContract, HrOrder
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


def generate_hr_order_pdf(db: Session, order_id: int) -> bytes:
    order = db.get(HrOrder, order_id)
    if order is None:
        raise ValueError("Əmr tapılmadı")
    org = db.get(Organization, order.organization_id)
    employee = db.get(Employee, order.employee_id)
    contract = db.scalar(
        select(EmploymentContract)
        .where(EmploymentContract.employee_id == order.employee_id)
        .order_by(EmploymentContract.start_date.desc())
    )

    font = _register_fonts()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )
    styles = getSampleStyleSheet()
    styles["Title"].fontName = f"{font}-Bold" if font == "DejaVu" else font
    styles["Normal"].fontName = font
    styles["Heading2"].fontName = f"{font}-Bold" if font == "DejaVu" else font

    order_titles = {
        "HIRE": "İşə qəbul haqqında",
        "TERMINATE": "Əmək müqaviləsinə xitam verilməsi haqqında",
        "LEAVE": "Əmək məzuniyyətinin verilməsi haqqında",
        "VACATION": "Əmək məzuniyyətinin verilməsi haqqında",
        "TRIP": "Xidməti ezamiyyətə göndərilmə haqqında",
        "BONUS": "Əməkdaşın mükafatlandırılması haqqında",
        "TRANSFER": "Başqa işə keçirilmə haqqında",
        "DISCIPLINARY": "İntizam tənbehi tətbiq edilməsi haqqında",
        "PENALTY": "İntizam tənbehi tətbiq edilməsi haqqında",
    }
    title_text = order_titles.get(order.order_type, "Kadr əmri")

    story = []
    if org:
        story.append(Paragraph(f"<b>{org.name}</b>", styles["Title"]))
        if org.voen:
            story.append(Paragraph(f"VÖEN: {org.voen} &nbsp;|&nbsp; {org.legal_address or ''}", styles["Normal"]))
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph(f"<b>Ə M R &nbsp; № &nbsp; {order.order_number}</b>", styles["Heading2"]))
    meta_row = Table(
        [["Bakı şəhəri", f"Tarix: {order.order_date.strftime('%d.%m.%Y')}"]],
        colWidths=[85 * mm, 85 * mm],
    )
    meta_row.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), font),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_row)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph(f"<b>Mövzu: {title_text}</b>", styles["Heading2"]))
    story.append(Spacer(1, 4 * mm))

    emp_full = f"{employee.last_name} {employee.first_name} {employee.father_name or ''}".strip() if employee else "Əməkdaş"
    article = f" (AR Əmək Məcəlləsinin {order.labor_code_article} maddəsi)" if order.labor_code_article else ""
    story.append(Paragraph(
        f"Azərbaycan Respublikasının Əmək Məcəlləsinə və müəssisənin daxili nizamnaməsinə əsasən{article}:",
        styles["Normal"]
    ))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("<b>Ə M R &nbsp; E D İ R Ə M :</b>", styles["Heading2"]))
    story.append(Spacer(1, 3 * mm))

    payload = order.payload_json or {}
    clauses = []
    if order.order_type == "HIRE":
        clauses.append(
            f"1. <b>{emp_full}</b> (FİN: {employee.pin_code if employee else ''}) {order.effective_date.strftime('%d.%m.%Y')} il tarixindən müvafiq ştat vahidi üzrə işə qəbul edilsin."
        )
        if contract and contract.gross_salary:
            clauses.append(f"2. İşçiyə aylıq <b>{_money(contract.gross_salary)} AZN</b> məbləğində vəzifə maaşı təyin edilsin.")
        clauses.append("3. Mühasibatlıq əməkhaqqının və qanunvericiliklə nəzərdə tutulmuş digər ayırmaların hesablanmasını təmin etsin.")
    elif order.order_type == "TERMINATE":
        art_text = f"Əmək Məcəlləsinin {order.labor_code_article} maddəsinə" if order.labor_code_article else "müvafiq qanunvericiliyə"
        clauses.append(
            f"1. <b>{emp_full}</b> ilə bağlanmış əmək müqaviləsinə {order.effective_date.strftime('%d.%m.%Y')} il tarixindən {art_text} əsasən xitam verilsin."
        )
        settlement = payload.get("settlement", {})
        if settlement:
            comp_days = settlement.get("unused_leave_days", 0)
            comp_amt = settlement.get("unused_leave_compensation", 0)
            clauses.append(
                f"2. İşçiyə istifadə edilməmiş <b>{comp_days}</b> təqvim günü məzuniyyətə görə <b>{_money(comp_amt)} AZN</b> kompensasiya və son haqq-hesab ödənilsin."
            )
        clauses.append("3. Mühasibatlıq və Kadrlar şöbəsi son haqq-hesab ödənişini və ƏMAS bildirişinin icrasını təmin etsin.")
    else:
        clauses.append(f"1. <b>{emp_full}</b> barəsində {order.effective_date.strftime('%d.%m.%Y')} il tarixindən qeyd olunan tədbir icra edilsin.")
        if payload.get("reason"):
            clauses.append(f"2. Əsas: {payload.get('reason')}")

    for c in clauses:
        story.append(Paragraph(c, styles["Normal"]))
        story.append(Spacer(1, 2.5 * mm))

    story.append(Spacer(1, 15 * mm))

    sig_table = Table(
        [
            ["Direktor: _______________________", "Kadrlar şöbəsi: _______________________"],
            ["M.Y.", "Tanış oldum: _______________________ (İşçi)"],
        ],
        colWidths=[85 * mm, 85 * mm],
    )
    sig_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), font),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(sig_table)

    doc.build(story)
    return buffer.getvalue()


def generate_offer_letter_pdf(db: Session, application_id: int) -> bytes:
    from app.models.organization import Department, Position, StaffingTable
    from app.models.recruitment import Application, Candidate, Vacancy

    app_row = db.get(Application, application_id)
    if app_row is None:
        raise ValueError("Müraciət tapılmadı")
    vacancy = db.get(Vacancy, app_row.vacancy_id)
    candidate = db.get(Candidate, app_row.candidate_id)
    org = db.get(Organization, vacancy.organization_id) if vacancy else None
    staffing = db.get(StaffingTable, vacancy.staffing_id) if vacancy else None
    position = db.get(Position, staffing.position_id) if staffing else None
    department = db.get(Department, staffing.department_id) if staffing else None

    font = _register_fonts()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )
    styles = getSampleStyleSheet()
    styles["Title"].fontName = f"{font}-Bold" if font == "DejaVu" else font
    styles["Normal"].fontName = font
    styles["Heading2"].fontName = f"{font}-Bold" if font == "DejaVu" else font

    story = []
    if org:
        story.append(Paragraph(f"<b>{org.name}</b>", styles["Title"]))
        story.append(Paragraph(f"{org.legal_address or ''} &nbsp;|&nbsp; VÖEN: {org.voen or ''}", styles["Normal"]))
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph("<b>RƏSMİ İŞ TƏKLİFİ (JOB OFFER)</b>", styles["Heading2"]))
    story.append(Spacer(1, 4 * mm))

    cand_name = candidate.full_name if candidate else "Hörmətli Namizəd"
    story.append(Paragraph(f"<b>Hörmətli {cand_name},</b>", styles["Normal"]))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        "Müsahibə mərhələlərindəki uğurlu iştirakınıza görə Sizi təbrik edirik! "
        f"\"{org.name if org else 'Şirkətimiz'}\" komandasına qoşulmağınız üçün aşağıdakı şərtlərlə rəsmi iş təklifini təqdim edirik:",
        styles["Normal"],
    ))
    story.append(Spacer(1, 5 * mm))

    pos_title = vacancy.title if vacancy else (position.title if position else "Mütəxəssis")
    dept_name = department.name if department else "Müvafiq struktur bölmə"
    salary = _money(staffing.base_salary if staffing else 0)

    offer_data = [
        ["Təklif olunan vəzifə:", pos_title],
        ["Struktur bölmə (Şöbə):", dept_name],
        ["Aylıq vəzifə maaşı (Gross):", f"{salary} AZN"],
        ["İş rejimi və qrafiki:", "Standart 5 günlük iş həftəsi (40 saat)"],
        ["Sınaq müddəti:", "3 (üç) ay"],
        ["Əsas əmək məzuniyyəti:", "21 təqvim günü (AR ƏM m.114)"],
        ["Sosial paket:", "İcbari tibbi sığorta və dövlət sosial təminatları"],
    ]
    offer_table = Table(offer_data, colWidths=[65 * mm, 105 * mm])
    offer_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), font),
        ("FONTNAME", (0, 0), (0, -1), f"{font}-Bold" if font == "DejaVu" else font),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(offer_table)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph(
        "Bu iş təklifini qəbul etdiyinizi bildirmək üçün lütfən sənədi imzalayaraq İnsan Resursları Departamentinə təqdim edin.",
        styles["Normal"],
    ))
    story.append(Spacer(1, 15 * mm))

    confirm_table = Table(
        [
            ["İşəgötürən adından:", "Təklifi qəbul edirəm:"],
            ["İmza: _______________________", "İmza: _______________________ (Namizəd)"],
            ["Tarix: _______________________", "Tarix: _______________________"],
        ],
        colWidths=[85 * mm, 85 * mm],
    )
    confirm_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), font),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(confirm_table)

    doc.build(story)
    return buffer.getvalue()


def generate_employment_reference_pdf(db: Session, employee_id: int, purpose: str = "Tələb olunan yerə") -> bytes:
    from app.models.organization import Department, Position, StaffingTable

    employee = db.get(Employee, employee_id)
    if employee is None:
        raise ValueError("İşçi tapılmadı")
    contract = db.scalar(
        select(EmploymentContract)
        .where(EmploymentContract.employee_id == employee.id, EmploymentContract.status == "ACTIVE")
        .order_by(EmploymentContract.start_date.desc())
    )
    org = db.get(Organization, employee.organization_id)
    pos_title = "Əməkdaş"
    dept_name = ""
    gross_salary = "0.00"
    start_date_str = ""
    if contract:
        gross_salary = _money(contract.gross_salary)
        start_date_str = contract.start_date.strftime("%d.%m.%Y")
        staffing = db.get(StaffingTable, contract.staffing_id)
        if staffing:
            pos = db.get(Position, staffing.position_id)
            dep = db.get(Department, staffing.department_id)
            if pos:
                pos_title = pos.title
            if dep:
                dept_name = dep.name

    font = _register_fonts()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )
    styles = getSampleStyleSheet()
    styles["Title"].fontName = f"{font}-Bold" if font == "DejaVu" else font
    styles["Normal"].fontName = font
    styles["Heading2"].fontName = f"{font}-Bold" if font == "DejaVu" else font

    story = []
    if org:
        story.append(Paragraph(f"<b>{org.name}</b>", styles["Title"]))
        story.append(Paragraph(f"{org.legal_address or ''} &nbsp;|&nbsp; VÖEN: {org.voen or ''} &nbsp;|&nbsp; Bank IBAN: {org.bank_iban or ''}", styles["Normal"]))
    story.append(Spacer(1, 10 * mm))

    ref_no = f"AR-{employee.id:04d}-{date.today():%Y%m%d}"
    story.append(Paragraph(f"<b>A R A Y I Ş &nbsp; № &nbsp; {ref_no}</b>", styles["Heading2"]))
    story.append(Paragraph(f"Tarix: {date.today().strftime('%d.%m.%Y')}", styles["Normal"]))
    story.append(Spacer(1, 8 * mm))

    emp_name = f"{employee.last_name} {employee.first_name} {employee.father_name or ''}".strip()
    dept_clause = f" (\"{dept_name}\" departamenti)" if dept_name else ""
    body_text = (
        f"Verilir əməkdaş <b>{emp_name}</b>-na (FİN: <b>{employee.pin_code}</b>, Ş/V: {employee.ssn or 'Qeyd olunmayıb'}) ondan ötrü ki, "
        f"o həqiqətən də <b>{start_date_str or date.today().strftime('%d.%m.%Y')}</b> il tarixindən etibarən <b>\"{org.name if org else 'Müəssisə'}\"</b>-də "
        f"<b>\"{pos_title}\"</b>{dept_clause} vəzifəsində əsas iş yeri üzrə çalışır.<br/><br/>"
        f"Onun aylıq rəsmi vəzifə (tarif) maaşı <b>{gross_salary} AZN</b> təşkil edir.<br/><br/>"
        f"Arayış <b>{purpose}</b> təqdim olunmaq üçün verilir."
    )
    story.append(Paragraph(body_text, styles["Normal"]))
    story.append(Spacer(1, 20 * mm))

    sign_table = Table(
        [
            ["Müəssisənin Direktoru: _______________________", "M.Y. (Möhür yeri)"],
            ["Baş Mühasib / HR Rəhbəri: _______________________", "Tarix: " + date.today().strftime("%d.%m.%Y")],
        ],
        colWidths=[105 * mm, 65 * mm],
    )
    sign_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), font),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(sign_table)

    doc.build(story)
    return buffer.getvalue()


def military_report_csv(db: Session, organization_id: int) -> str:
    from app.models.employee import EmployeeMilitary

    rows_data = db.execute(
        select(Employee, EmployeeMilitary)
        .outerjoin(EmployeeMilitary, EmployeeMilitary.employee_id == Employee.id)
        .where(Employee.organization_id == organization_id, Employee.deleted_at.is_(None))
        .order_by(Employee.last_name, Employee.first_name)
    ).all()
    results = []
    for idx, (emp, mil) in enumerate(rows_data, start=1):
        full_name = f"{emp.last_name} {emp.first_name} {emp.father_name or ''}".strip()
        results.append({
            "№": idx,
            "FİN": emp.pin_code,
            "Soyadı, Adı, Ata adı": full_name,
            "Doğum tarixi": emp.birth_date.strftime("%d.%m.%Y") if emp.birth_date else "",
            "Cinsi": emp.gender or "",
            "Hərbi mükəlləfiyyət statusu": mil.military_status if mil else "Məlumat yoxdur",
            "Hərbi rütbəsi": mil.rank if mil else "",
            "Hərbi ixtisası (VUS)": mil.specialty_code if mil else "",
            "Hərbi bilet / Şəhadətnamə №": mil.document_number if mil else "",
            "Qeydiyyatda olduğu SHXÇDX": mil.military_office if mil else "",
            "Səfərbərlik kateqoriyası": mil.fitness_category if mil else "",
        })
    return _csv_response_text(results)


def calculate_trip_advance_norms(destination_city: str, is_foreign: bool, days: int) -> dict:
    days = max(int(days), 1)
    if is_foreign:
        daily = Decimal("150.00")
        hotel = Decimal("200.00")
    else:
        city_lower = (destination_city or "").strip().lower()
        if "bakı" in city_lower or "baku" in city_lower:
            daily = Decimal("90.00")
            hotel = Decimal("65.00")
        elif any(c in city_lower for c in ["gəncə", "ganja", "sumqayıt", "sumgait", "naxçıvan", "nakhchivan"]):
            daily = Decimal("70.00")
            hotel = Decimal("50.00")
        else:
            daily = Decimal("65.00")
            hotel = Decimal("40.00")
    total = (daily + hotel) * Decimal(days)
    return {
        "daily_allowance": daily,
        "hotel_limit": hotel,
        "total_advance": total,
    }

