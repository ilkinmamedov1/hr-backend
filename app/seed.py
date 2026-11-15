import secrets
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.contract import EmploymentContract, HrOrder
from app.models.employee import Employee, EmployeeDocument
from app.models.leave import LeaveRequest, LeaveType
from app.models.organization import Department, Organization, Position, StaffingTable
from app.models.payroll import (
    EmployeePayComponent,
    PayrollComponent,
    PayrollRun,
    TaxSocialRateHistory,
)
from app.models.performance import KpiEvaluation
from app.models.recruitment import Application, Candidate, Vacancy
from app.models.safety import SafetyIncident
from app.models.time import (
    AttendanceLog,
    EmployeeSchedule,
    ProductionCalendar,
    WorkSchedule,
)
from app.models.training import Training
from app.models.user import User
from app.services.calendar_service import generate_year_calendar
from app.services.leave_service import (
    approve_leave_request,
    calculate_sick_leave,
    create_leave_request,
    ensure_balances_for_contract,
)
from app.services.payroll_service import (
    approve_payroll_run,
    calculate_payroll_run,
    pay_payroll_run,
)
from app.services.workflow_service import create_step
from app.services.timesheet_service import generate_org_timesheets

TZ = ZoneInfo(settings.TIMEZONE)


def _tax_rules(sector_type: str) -> dict:
    if sector_type == "OIL_PUBLIC":
        income_brackets = [
            {"up_to": 2500.0, "rate": 0.14},
            {"up_to": None, "rate": 0.25},
        ]
    else:
        income_brackets = [
            {"up_to": 8000.0, "rate": 0.0},
            {"up_to": None, "rate": 0.14},
        ]
    return {
        "income_tax": {"brackets": income_brackets},
        "dsmf_employee": {
            "brackets": [{"up_to": 200.0, "rate": 0.03}, {"up_to": None, "rate": 0.10}]
        },
        "dsmf_employer": {
            "brackets": [{"up_to": 200.0, "rate": 0.22}, {"up_to": None, "rate": 0.15}]
        },
        "its_employee": {
            "brackets": [{"up_to": 8000.0, "rate": 0.02}, {"up_to": None, "rate": 0.005}]
        },
        "its_employer": {
            "brackets": [{"up_to": 8000.0, "rate": 0.02}, {"up_to": None, "rate": 0.005}]
        },
        "unemployment_employee": {"flat_rate": 0.005},
        "unemployment_employer": {"flat_rate": 0.005},
    }


def seed_reference_data(db: Session) -> None:
    leave_types = [
        ("ANNUAL", "Əmək məzuniyyəti", True, True, None, "ƏM m.114"),
        ("ANNUAL_EXTRA", "Əlavə məzuniyyət", True, True, None, "ƏM m.116-117"),
        ("MATERNITY", "Hamiləlik və doğuş məzuniyyəti", True, False, 140, "ƏM m.126"),
        ("CHILD_CARE", "Uşağa qulluq məzuniyyəti", True, False, 1095, "ƏM m.127"),
        ("EDUCATION", "Təhsil məzuniyyəti", True, False, None, "ƏM m.128"),
        ("UNPAID", "Ödənişsiz məzuniyyət", False, False, None, "ƏM m.130"),
        ("SICK", "Xəstəlik vərəqəsi", True, False, None, "NK №189"),
        ("SOCIAL", "Sosial məzuniyyət", True, False, None, "ƏM m.129"),
    ]
    for code, name, is_paid, affects, max_days, ref in leave_types:
        if not db.scalar(select(LeaveType).where(LeaveType.code == code)):
            db.add(
                LeaveType(
                    code=code,
                    name=name,
                    is_paid=is_paid,
                    affects_balance=affects,
                    max_days_per_year=max_days,
                    labor_code_ref=ref,
                )
            )

    components = [
        ("BASE", "Əsas əməkhaqqı", "EARNING", True, True, True, True, True, True, 10),
        ("OVERTIME", "İş vaxtından artıq iş", "EARNING", True, True, True, True, True, True, 20),
        ("NIGHT", "Gecə vaxtı əlavəsi", "EARNING", True, True, True, True, True, True, 30),
        ("HOLIDAY", "Bayram günü işi", "EARNING", True, True, True, True, True, True, 40),
        ("VACATION", "Məzuniyyət pulu", "EARNING", True, True, True, True, True, True, 50),
        ("SICK", "Bülleten ödənişi", "EARNING", True, False, False, False, False, False, 60),
        ("BONUS_KPI", "KPI bonusu", "EARNING", True, True, True, True, True, True, 70),
        ("ALLOWANCE", "Fərdi əlavə", "EARNING", True, True, True, True, True, True, 80),
        ("ALIMONY", "Aliment", "DEDUCTION", False, False, False, False, False, False, 200),
        ("ADVANCE", "Avans tutulması", "DEDUCTION", False, False, False, False, False, False, 210),
        ("EXECUTION", "İcra sənədi üzrə tutulma", "DEDUCTION", False, False, False, False, False, False, 220),
    ]
    for (
        code, name, ctype, taxable, dsmf, its, unemployment, vac_avg, sick_avg, sort_order
    ) in components:
        if not db.scalar(select(PayrollComponent).where(PayrollComponent.code == code)):
            db.add(
                PayrollComponent(
                    code=code,
                    name=name,
                    component_type=ctype,
                    is_taxable=taxable,
                    is_dsmf_base=dsmf,
                    is_its_base=its,
                    is_unemployment_base=unemployment,
                    include_in_vacation_avg=vac_avg,
                    include_in_sick_avg=sick_avg,
                    sort_order=sort_order,
                )
            )

    if db.scalar(select(func.count(TaxSocialRateHistory.id))) == 0:
        for sector in ("NON_OIL_PRIVATE", "OIL_PUBLIC"):
            for effective_from, note in (
                (date(2019, 1, 1), "2019 vergi islahatı"),
                (date(2021, 1, 1), "2021 dərəcələri"),
                (date(2024, 1, 1), "2024 dərəcələri"),
                (date(2026, 1, 1), "2026 dərəcələri - rəsmi dəyişiklik olduqda yeni sətir əlavə edin"),
            ):
                db.add(
                    TaxSocialRateHistory(
                        sector_type=sector,
                        effective_from=effective_from,
                        effective_to=None,
                        rules_json=_tax_rules(sector),
                        note=note,
                    )
                )
    db.commit()


def _ensure_calendar(db: Session, years: set[int]) -> None:
    for year in sorted(years):
        count = db.scalar(
            select(func.count(ProductionCalendar.cal_date)).where(ProductionCalendar.year == year)
        ) or 0
        if count == 0:
            generate_year_calendar(db, year)


def seed_demo(db: Session) -> None:
    if db.scalar(select(func.count(Organization.id))) > 0:
        return

    today = date.today()
    organization = Organization(
        name="Nümunə Holdinq MMC",
        short_name="Nümunə",
        voen="1234567890",
        sun_code="SUN-001",
        legal_address="Bakı şəhəri, Nizami küçəsi 100",
        actual_address="Bakı şəhəri, Nizami küçəsi 100",
        bank_name="Kapital Bank",
        bank_iban="AZ21NABZ00000000137010001944",
        bank_swift="AIIBAZ2X",
        phone="+994 12 555 00 00",
        email="info@numune.az",
        sector_type="NON_OIL_PRIVATE",
        settings_json={
            "overtime_multiplier": 2.0,
            "night_bonus_pct": 0.20,
            "holiday_multiplier": 2.0,
        },
        is_active=True,
    )
    db.add(organization)
    db.flush()

    departments = {}
    for code, name, cost_center in (
        ("HR", "İnsan Resursları", "CC-100"),
        ("IT", "İnformasiya Texnologiyaları", "CC-200"),
        ("FIN", "Maliyyə və Mühasibatlıq", "CC-300"),
        ("SALES", "Satış və Marketinq", "CC-400"),
    ):
        department = Department(
            organization_id=organization.id,
            code=code,
            name=name,
            cost_center_code=cost_center,
            path=name,
        )
        db.add(department)
        db.flush()
        departments[code] = department

    positions = {}
    for code, title, grade, min_salary, max_salary, leave_days in (
        ("HR_DIR", "İnsan Resursları Direktoru", 5, 2200, 3200, 30),
        ("HR_SPEC", "Kadr Mütəxəssisi", 3, 900, 1600, 21),
        ("DEV", "Proqram Mühəndisi", 4, 1800, 3500, 21),
        ("ACC", "Baş Mühasib", 4, 1500, 2800, 21),
        ("SALES", "Satış Meneceri", 4, 1400, 2600, 21),
    ):
        position = Position(
            organization_id=organization.id,
            title=title,
            occupation_code=f"AZ-{code}",
            grade_level=grade,
            min_salary=min_salary,
            max_salary=max_salary,
            annual_leave_days=leave_days,
        )
        db.add(position)
        db.flush()
        positions[code] = position

    staffing = {}
    for key, department, position, base_salary, harmful in (
        ("HR_DIR", departments["HR"], positions["HR_DIR"], 2800, 0),
        ("HR_SPEC", departments["HR"], positions["HR_SPEC"], 1300, 0),
        ("DEV1", departments["IT"], positions["DEV"], 3000, 0),
        ("DEV2", departments["IT"], positions["DEV"], 2500, 0),
        ("ACC", departments["FIN"], positions["ACC"], 2100, 0),
        ("SALES", departments["SALES"], positions["SALES"], 1900, 0),
    ):
        unit = StaffingTable(
            organization_id=organization.id,
            department_id=department.id,
            position_id=position.id,
            approved_headcount=1,
            base_salary=base_salary,
            harmful_work_bonus_pct=harmful,
            effective_from=date(2024, 1, 1),
            is_active=True,
        )
        db.add(unit)
        db.flush()
        staffing[key] = unit

    employee_specs = [
        {
            "pin": "1234567", "first": "Aysel", "last": "Məmmədova", "father": "Rəşid",
            "gender": "F", "birth": date(1990, 5, 12), "tenure": 3, "staffing": "HR_DIR",
            "start": date(2023, 1, 15), "salary": 2800, "iban": "AZ21NABZ00000000137010001944",
        },
        {
            "pin": "2345678", "first": "Rəşad", "last": "Əliyev", "father": "Tofiq",
            "gender": "M", "birth": date(1995, 8, 3), "tenure": 6.5, "staffing": "DEV1",
            "start": date(2020, 3, 1), "salary": 3000, "iban": "AZ22NABZ00000000137010001945",
        },
        {
            "pin": "3456789", "first": "Nigar", "last": "Həsənli", "father": "Elçin",
            "gender": "F", "birth": date(1998, 2, 20), "tenure": 2, "staffing": "ACC",
            "start": date(2024, 2, 1), "salary": 2100, "iban": "AZ23NABZ00000000137010001946",
        },
        {
            "pin": "4567890", "first": "Elvin", "last": "Kərimov", "father": "Vüqar",
            "gender": "M", "birth": date(1992, 11, 8), "tenure": 8, "staffing": "SALES",
            "start": date(2021, 9, 1), "salary": 1900, "iban": "AZ24NABZ00000000137010001947",
        },
        {
            "pin": "5678901", "first": "Kamran", "last": "Hüseynov", "father": "Fərhad",
            "gender": "M", "birth": date(2000, 4, 14), "tenure": 1, "staffing": "HR_SPEC",
            "start": date(2025, 4, 1), "salary": 1300, "iban": "AZ25NABZ00000000137010001948",
        },
        {
            "pin": "6789012", "first": "Leyla", "last": "Əliyeva", "father": "Namiq",
            "gender": "F", "birth": date(1996, 9, 30), "tenure": 4, "staffing": "DEV2",
            "start": date(2024, 6, 1), "salary": 2500, "iban": "AZ26NABZ00000000137010001949",
        },
    ]

    employees = []
    contracts = []
    for index, spec in enumerate(employee_specs):
        employee = Employee(
            organization_id=organization.id,
            pin_code=spec["pin"],
            first_name=spec["first"],
            last_name=spec["last"],
            father_name=spec["father"],
            birth_date=spec["birth"],
            gender=spec["gender"],
            citizenship="AZ",
            ssn=f"SSN{spec['pin']}",
            individual_voen="",
            id_card_number=f"AZE{spec['pin']}",
            id_card_issue_date=date(2020, 1, 1),
            id_card_expiry_date=date(2030, 1, 1),
            phone=f"+994 50 555 {index + 10:02d} {index + 1:02d}",
            email=f"employee{index + 1}@numune.az",
            bank_name="Kapital Bank",
            bank_iban=spec["iban"],
            total_insurance_tenure_years=Decimal(str(spec["tenure"])),
            status="ACTIVE",
        )
        db.add(employee)
        db.flush()
        employees.append(employee)

        contract = EmploymentContract(
            organization_id=organization.id,
            employee_id=employee.id,
            staffing_id=staffing[spec["staffing"]].id,
            contract_number=f"EM-{2020 + index}-{employee.id:04d}",
            contract_type="INDEFINITE",
            work_type="MAIN",
            start_date=spec["start"],
            probation_end_date=spec["start"] + timedelta(days=90),
            gross_salary=spec["salary"],
            salary_type="MONTHLY",
            signed_date=spec["start"],
            status="ACTIVE",
        )
        db.add(contract)
        db.flush()
        contracts.append(contract)

    organization.director_id = employees[0].id
    departments["HR"].head_employee_id = employees[0].id
    departments["IT"].head_employee_id = employees[1].id
    departments["FIN"].head_employee_id = employees[2].id
    departments["SALES"].head_employee_id = employees[3].id

    default_schedule = WorkSchedule(
        organization_id=organization.id,
        name="Standart 5 günlük, 40 saat",
        schedule_type="STANDARD_5",
        weekly_hours=40,
        shift_rules_json={"work_days": [1, 2, 3, 4, 5], "start": "09:00", "end": "18:00", "lunch_break_hours": 1},
        is_default=True,
    )
    db.add(default_schedule)
    db.flush()
    for employee in employees:
        db.add(
            EmployeeSchedule(
                employee_id=employee.id,
                work_schedule_id=default_schedule.id,
                effective_from=date(2024, 1, 1),
            )
        )

    for employee, contract in zip(employees, contracts):
        ensure_balances_for_contract(db, contract, today)

    db.add(
        EmployeeDocument(
            employee_id=employees[1].id,
            doc_type="ID_CARD",
            doc_number="AZE2345678",
            issue_date=date(2020, 1, 1),
            expiry_date=today + timedelta(days=45),
            notes="Demo: müddəti bitməkdə olan sənəd",
        )
    )

    users = [
        ("admin@hr.local", "Sistem Administratoru", "Admin123!", "SUPERADMIN", None),
        ("hr@hr.local", "Aysel Məmmədova", "Hr12345!", "HR_DIRECTOR", employees[0].id),
        ("accountant@hr.local", "Nigar Həsənli", "Acc12345!", "ACCOUNTANT", employees[2].id),
        ("manager@hr.local", "Rəşad Əliyev", "Mgr12345!", "DEPT_MANAGER", employees[1].id),
        ("employee@hr.local", "Leyla Əliyeva", "Emp12345!", "EMPLOYEE", employees[5].id),
    ]
    for email, full_name, password, role, employee_id in users:
        if not db.scalar(select(User).where(User.email == email)):
            db.add(
                User(
                    email=email,
                    full_name=full_name,
                    hashed_password=hash_password(password),
                    role=role,
                    organization_id=organization.id,
                    employee_id=employee_id,
                    is_active=True,
                )
            )
    db.commit()

    current_year = today.year
    current_month = today.month
    month_start = date(current_year, current_month, 1)
    calendar_rows = list(
        db.scalars(
            select(ProductionCalendar).where(
                ProductionCalendar.year == current_year,
                ProductionCalendar.month == current_month,
            )
        )
    )
    workdays = [
        row.cal_date
        for row in calendar_rows
        if row.day_type in ("WORKDAY", "SHORT_WORKDAY") and row.cal_date <= today
    ]
    for index, employee in enumerate(employees):
        for workday in workdays:
            start = datetime.combine(workday, time(9, 0), tzinfo=TZ)
            end_hour = 20 if (index == 1 and workday.day % 5 == 0) else 18
            end = datetime.combine(workday, time(end_hour, 0), tzinfo=TZ)
            db.add(
                AttendanceLog(
                    employee_id=employee.id,
                    punch_time=start,
                    direction="IN",
                    device_id="TURNSTILE-01",
                )
            )
            db.add(
                AttendanceLog(
                    employee_id=employee.id,
                    punch_time=end,
                    direction="OUT",
                    device_id="TURNSTILE-01",
                )
            )
    db.commit()

    annual_type = db.scalar(select(LeaveType).where(LeaveType.code == "ANNUAL"))
    next_monday = today + timedelta(days=(7 - today.weekday()) % 7 or 7)
    leave = create_leave_request(
        db,
        employee=employees[2],
        leave_type=annual_type,
        start_date=next_monday,
        end_date=next_monday + timedelta(days=4),
        reason="İllik məzuniyyət (demo)",
    )
    approve_leave_request(db, leave, None)

    pending_start = next_monday + timedelta(days=14)
    pending_leave = create_leave_request(
        db,
        employee=employees[3],
        leave_type=annual_type,
        start_date=pending_start,
        end_date=pending_start + timedelta(days=2),
        reason="Ailəvi səbəb (demo, təsdiq gözləyir)",
    )
    create_step(
        db,
        entity_type="LEAVE_REQUEST",
        entity_id=pending_leave.id,
        organization_id=employees[3].organization_id,
        employee_id=employees[3].id,
    )
    db.commit()

    previous_month_date = (month_start - timedelta(days=1)).replace(day=1)
    generate_org_timesheets(db, organization.id, previous_month_date.year, previous_month_date.month)
    previous_run = PayrollRun(
        organization_id=organization.id,
        period_year=previous_month_date.year,
        period_month=previous_month_date.month,
        run_type="REGULAR",
        status="DRAFT",
        notes="Demo əməkhaqqı hesablaması",
    )
    db.add(previous_run)
    db.commit()
    calculate_payroll_run(db, previous_run, None)
    approve_payroll_run(db, previous_run, None)
    pay_payroll_run(db, previous_run)

    calculate_sick_leave(
        db,
        employee=employees[4],
        bulletin_number=f"B-{current_year}-0001",
        start_date=today - timedelta(days=2),
        end_date=today,
        notes="Demo bülleten",
    )

    db.add(
        KpiEvaluation(
            employee_id=employees[1].id,
            period_code=f"{current_year}-{current_month:02d}",
            kpi_items_json=[
                {"name": "Layihə çatdırılması", "weight": 0.5, "score": 120},
                {"name": "Komanda işi", "weight": 0.3, "score": 110},
                {"name": "Keyfiyyət", "weight": 0.2, "score": 115},
            ],
            final_score=115,
            bonus_multiplier=Decimal("1.15"),
            is_synced_to_payroll=False,
            notes="Demo KPI - cari ayın əməkhaqqı hesablananda bonus kimi əlavə olunacaq",
        )
    )

    vacancy = Vacancy(
        organization_id=organization.id,
        staffing_id=staffing["DEV2"].id,
        department_id=departments["IT"].id,
        title="Proqram Mühəndisi (Python)",
        openings=1,
        description="FastAPI və PostgreSQL təcrübəsi tələb olunur",
        requirements="3+ il backend təcrübəsi",
        salary_min=2200,
        salary_max=3200,
        status="OPEN",
    )
    candidate = Candidate(
        full_name="Orxan Quliyev",
        phone="+994 55 123 45 67",
        email="orxan.quliyev@example.com",
        skills_json=["Python", "FastAPI", "PostgreSQL", "Docker"],
        experience_years=Decimal("5"),
        current_position="Backend Developer",
        source="LinkedIn",
    )
    db.add_all([vacancy, candidate])
    db.flush()
    db.add(
        Application(
            vacancy_id=vacancy.id,
            candidate_id=candidate.id,
            stage="INTERVIEW",
            score=85,
            applied_at=today,
        )
    )

    db.add(
        Training(
            organization_id=organization.id,
            title="İşə qəbul və seçim texnikaları",
            training_type="INTERNAL",
            provider="HR Departamenti",
            start_date=today + timedelta(days=20),
            end_date=today + timedelta(days=21),
            budget=500,
            cost=0,
            status="PLANNED",
            description="Demo təlim",
        )
    )
    db.add(
        SafetyIncident(
            organization_id=organization.id,
            employee_id=employees[1].id,
            incident_date=today - timedelta(days=10),
            incident_type="MINOR_INJURY",
            description="Demo: yüngül xəsarət",
            severity="LOW",
            lost_days=1,
            investigation_status="CLOSED",
        )
    )

    current_run = PayrollRun(
        organization_id=organization.id,
        period_year=current_year,
        period_month=current_month,
        run_type="REGULAR",
        status="DRAFT",
        notes="Cari ay - hesablamaq üçün /calculate çağırın",
    )
    db.add(current_run)

    if db.scalar(select(func.count(HrOrder.id))) == 0:
        db.add(
            HrOrder(
                organization_id=organization.id,
                order_number="ƏMR-2026/01",
                order_type="HIRE",
                employee_id=employees[0].id,
                labor_code_article="AR ƏM m. 73",
                order_date=today - timedelta(days=60),
                effective_date=today - timedelta(days=60),
                status="APPROVED",
                payload_json={"position": "Kadrlar üzrə menecer", "salary": 2500},
            )
        )
        db.add(
            HrOrder(
                organization_id=organization.id,
                order_number="ƏMR-2026/02",
                order_type="LEAVE",
                employee_id=employees[1].id,
                labor_code_article="AR ƏM m. 113",
                order_date=today - timedelta(days=15),
                effective_date=today - timedelta(days=15),
                status="APPROVED",
                payload_json={"leave_type": "ANNUAL", "days": 14},
            )
        )

    db.commit()


def _ensure_demo_orders(db: Session) -> None:
    if db.scalar(select(func.count(HrOrder.id))) == 0:
        org = db.scalar(select(Organization).order_by(Organization.id))
        emp = db.scalar(select(Employee).order_by(Employee.id))
        if org and emp:
            today = date.today()
            db.add(
                HrOrder(
                    organization_id=org.id,
                    order_number="ƏMR-2026/01",
                    order_type="HIRE",
                    employee_id=emp.id,
                    labor_code_article="AR ƏM m. 73",
                    order_date=today - timedelta(days=60),
                    effective_date=today - timedelta(days=60),
                    status="APPROVED",
                    payload_json={"position": "Kadrlar üzrə menecer", "salary": 2500},
                )
            )
            db.commit()


def seed_all(db: Session) -> None:
    seed_reference_data(db)
    _ensure_calendar(db, {date.today().year - 1, date.today().year, date.today().year + 1})
    if settings.SEED_DEMO:
        seed_demo(db)
        _ensure_demo_orders(db)
    else:
        if db.scalar(select(func.count(Organization.id))) == 0:
            organization = Organization(
                name="Default MMC",
                voen="0000000000",
                sector_type="NON_OIL_PRIVATE",
                is_active=True,
            )
            db.add(organization)
            db.flush()
        organization = db.scalar(select(Organization).order_by(Organization.id))
        has_superadmin = db.scalar(
            select(func.count(User.id)).where(User.role == "SUPERADMIN")
        )
        if not has_superadmin:
            password = settings.INITIAL_ADMIN_PASSWORD
            generated = False
            if not password:
                password = secrets.token_urlsafe(15)
                generated = True
            admin = User(
                email=settings.INITIAL_ADMIN_EMAIL.lower(),
                full_name=settings.INITIAL_ADMIN_NAME,
                hashed_password=hash_password(password),
                role="SUPERADMIN",
                organization_id=organization.id,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            if generated:
                print(
                    "=" * 72
                    + f"\nİlkin admin yaradıldı: {admin.email}\nŞifrə: {password}\n"
                    "Bu şifrə yalnız bir dəfə göstərilir. Dərhal dəyişin.\n" + "=" * 72,
                    flush=True,
                )
